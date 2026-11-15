"""GymFlow Streamlit app: run the simulated pipeline and inspect its results."""
import asyncio
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gymflow.concurrency import concurrent_edits_demo  # noqa: E402
from gymflow.engine import rebuild_state, run_block  # noqa: E402
from gymflow.i18n import UI, describe_alert  # noqa: E402
from gymflow.profiles import ATHLETES  # noqa: E402
from gymflow.rules import epley_1rm  # noqa: E402

PALETTES = {
    "light": {"surface": "#fcfcfb", "text": "#52514e", "grid": "#e3e2dd",
              "athletes": {"ALEX": "#2a78d6", "SARA": "#eb6834", "MALIK": "#1baf7a"}},
    "dark": {"surface": "#1a1a19", "text": "#c3c2b7", "grid": "#3a3a37",
             "athletes": {"ALEX": "#3987e5", "SARA": "#d95926", "MALIK": "#199e70"}},
}
LEVEL_COLORS = {"RED": "#d03b3b", "ORANGE": "#fab219", "GREEN": "#0ca30c", "BLUE": "#2a78d6"}
LEVEL_ICONS = {"RED": "🔴", "ORANGE": "🟠", "GREEN": "🟢", "BLUE": "🔵"}
LOCK_EDITS = 20

st.set_page_config(page_title="GymFlow", page_icon="🏋️", layout="wide")


def theme():
    return PALETTES["dark" if st.context.theme.type == "dark" else "light"]


def base_layout(fig, x_title, y_title, height=340):
    p = theme()
    fig.update_layout(height=height, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(color=p["text"]), xaxis_title=x_title, yaxis_title=y_title,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    fig.update_xaxes(gridcolor=p["grid"], zerolinecolor=p["grid"])
    fig.update_yaxes(gridcolor=p["grid"], zerolinecolor=p["grid"])
    return fig


def alerts_figure(alerts, t):
    p = theme()
    fig = go.Figure()
    counts = alerts.groupby(["athlete", "level"]).size().unstack(fill_value=0).reindex(index=list(ATHLETES), fill_value=0)
    for level in LEVEL_COLORS:
        if level in counts:
            fig.add_bar(y=counts.index, x=counts[level], orientation="h", name=t["levels"][level],
                        marker=dict(color=LEVEL_COLORS[level], line=dict(color=p["surface"], width=2)))
    return base_layout(fig, t["count"], None, 280).update_layout(barmode="stack", legend_traceorder="normal")


def hr_figure(sets, athlete, session, t):
    p = theme()
    rows = sets[(sets["athlete"] == athlete) & (sets["session"] == session)].sort_values("seq").copy()
    rows["order"] = range(1, len(rows) + 1)
    limit = int(ATHLETES[athlete]["max_hr"] * 0.85)
    fig = go.Figure()
    fig.add_scatter(x=rows["order"], y=rows["hr"], mode="lines+markers", name=athlete,
                    line=dict(color=p["athletes"][athlete], width=2), marker=dict(size=8),
                    customdata=rows[["exercise", "set"]],
                    hovertemplate="%{customdata[0]}, " + t["set"].lower() + " %{customdata[1]}<br>%{y} bpm<extra></extra>")
    fig.add_hline(y=limit, line=dict(color=p["text"], width=1, dash="dash"),
                  annotation_text=f"{t['hr_limit']}: {limit} bpm", annotation_position="bottom right")
    return base_layout(fig, t["set_order"], t["hr"]).update_layout(showlegend=False).update_xaxes(dtick=1)


def best_1rm_table(sets):
    rows = sets.assign(e1rm=[epley_1rm(w, r) for w, r in zip(sets["weight"], sets["reps"])])
    table = rows.groupby(["athlete", "exercise", "session"])["e1rm"].max().round(1).reset_index()
    table["session"] += 1
    return table


def progress_figure(table, exercise, t):
    p = theme()
    fig = go.Figure()
    for athlete in ATHLETES:
        rows = table[(table["exercise"] == exercise) & (table["athlete"] == athlete)]
        fig.add_scatter(x=rows["session"], y=rows["e1rm"], mode="lines+markers", name=athlete,
                        line=dict(color=p["athletes"][athlete], width=2), marker=dict(size=8),
                        hovertemplate=athlete + "<br>" + t["session"] + " %{x}<br>%{y} kg<extra></extra>")
    return base_layout(fig, t["session"], t["e1rm"]).update_xaxes(dtick=1)


lang = st.sidebar.radio("Language / Langue", ["en", "fr"], format_func={"en": "English", "fr": "Français"}.get, horizontal=True)
t = UI[lang]

st.title("🏋️ GymFlow")
st.write(t["tagline"])
st.caption(t["disclaimer"])

with st.sidebar:
    st.header(t["settings"])
    sessions = st.slider(t["sessions"], 1, 8, 5)
    seed = st.number_input(t["seed"], 0, 9999, 42)
    delay_ms = st.slider(t["delay"], 0, 200, 20, 10)
    stop_after = st.number_input(t["stop"], 0, 240, 0)
    clicked = st.button(t["run"], type="primary", width="stretch")

if clicked or "result" not in st.session_state:
    feed = st.empty()

    def show_set(s, alerts):
        badges = " ".join(LEVEL_ICONS[a["level"]] for a in alerts)
        feed.info(f"{t['live_now']}: {t['session']} {s['session'] + 1} · {s['athlete']} · {s['exercise']} "
                  f"· {s['weight']} kg × {s['reps']} · {s['hr']} bpm · RPE {s['rpe']} {badges}")

    st.session_state["result"] = asyncio.run(run_block(sessions, seed, delay_ms / 1000, stop_after or None, on_set=show_set))
    feed.empty()

result = st.session_state["result"]
stats = result["stats"]
sets = pd.DataFrame(result["sets"])
alerts = pd.DataFrame(result["alerts"], columns=["athlete", "session", "exercise", "set", "level", "type", "params"])

if stats["stopped_early"]:
    st.warning(t["stopped"])

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(t["m_produced"], stats["produced"])
c2.metric(t["m_sets"], stats["persisted"])
c3.metric(t["m_lost"], stats["produced"] - stats["persisted"])
c4.metric(t["m_alerts"], stats["alerts"])
c5.metric(t["m_latency"], f"{stats['latency_median_ms']:.1f} ms")
st.caption(t["backend"].format(live=result["live_backend"], log=result["log_backend"]) + " " + t["latency_note"])

tab_live, tab_alerts, tab_arch = st.tabs([t["tab_live"], t["tab_alerts"], t["tab_arch"]])

with tab_live:
    left, right = st.columns(2)
    with left:
        st.subheader(t["chart_hr"])
        pick_athlete, pick_session = st.columns(2)
        athlete = pick_athlete.selectbox(t["athlete"], list(ATHLETES))
        sessions_run = sorted(int(s) for s in sets["session"].unique())
        session = pick_session.selectbox(t["session"], sessions_run, index=len(sessions_run) - 1, format_func=lambda s: str(s + 1))
        st.plotly_chart(hr_figure(sets, athlete, session, t), width="stretch")
    with right:
        st.subheader(t["chart_1rm"])
        exercise = st.selectbox(t["exercise"], list(sets["exercise"].unique()))
        table = best_1rm_table(sets)
        st.plotly_chart(progress_figure(table, exercise, t), width="stretch")
    if sets["session"].nunique() < 3:
        st.caption(t["plateau_hint"])
    with st.expander(t["view_table"]):
        st.dataframe(sets[["session", "athlete", "exercise", "set", "weight", "reps", "hr", "rpe", "rest"]],
                     width="stretch", hide_index=True)

with tab_alerts:
    st.subheader(t["chart_alerts"])
    if alerts.empty:
        st.info(t["no_alerts"])
    else:
        st.plotly_chart(alerts_figure(alerts, t), width="stretch")
        choices = st.multiselect(t["athlete"], list(ATHLETES), default=list(ATHLETES))
        shown = alerts[alerts["athlete"].isin(choices)]
        if shown.empty:
            st.info(t["no_alerts"])
        else:
            text = [describe_alert(a, lang) for a in shown.to_dict("records")]
            st.dataframe(pd.DataFrame({
                t["session"]: shown["session"].values + 1, t["athlete"]: shown["athlete"].values,
                t["exercise"]: shown["exercise"].values, t["set"]: shown["set"].values,
                t["level"]: [f"{LEVEL_ICONS[v]} {t['levels'][v]}" for v in shown["level"]],
                t["alert"]: [x[0] for x in text], t["detail"]: [x[1] for x in text], t["action"]: [x[2] for x in text],
            }), width="stretch", hide_index=True)

with tab_arch:
    st.subheader(t["arch_title"])
    st.graphviz_chart("""
    digraph {
      rankdir=LR; bgcolor="transparent"; node [shape=box, style=rounded, fontname="sans-serif"];
      A [label="ALEX stream"]; S [label="SARA stream"]; M [label="MALIK stream"];
      Q [label="FIFO queue"]; E [label="Analysis engine\\n(rules)"];
      R [label="Live view\\nRedis or in-memory"]; L [label="Event log\\nMongoDB or mongomock"];
      A -> Q; S -> Q; M -> Q; Q -> E; E -> R; E -> L;
    }""")

    st.subheader(t["replay_title"])
    st.write(t["replay_text"])
    state = rebuild_state(result["sets"])
    st.dataframe(pd.DataFrame([
        {t["athlete"]: a, t["sets"]: s["sets"], t["volume"]: round(s["volume_kg"], 1), t["last_hr"]: s["last_hr"]}
        for a, s in state.items()]), width="stretch", hide_index=True)

    st.subheader(t["lock_title"])
    st.write(t["lock_text"])
    if st.button(t["lock_run"].format(n=LOCK_EDITS)):
        col_with, col_without = st.columns(2)
        col_with.metric(t["with_lock"], t["lock_result"].format(**asyncio.run(concurrent_edits_demo(LOCK_EDITS, use_lock=True))))
        col_without.metric(t["without_lock"], t["lock_result"].format(**asyncio.run(concurrent_edits_demo(LOCK_EDITS, use_lock=False))))
