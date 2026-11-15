import pytest

from gymflow.rules import analyse_set, epley_1rm, is_plateau

BASE = {"max_hr": 200, "hr": 120, "rpe": 7.0, "weight": 50.0, "target_weight": 50.0, "target_reps": 10,
        "reps": 10, "rest": 120, "min_rest": 90, "exercise": "Bench Press"}


def types(**changes):
    return {a["type"] for a in analyse_set({**BASE, **changes})}


def test_epley():
    assert epley_1rm(60, 10) == pytest.approx(80)


def test_normal_set_raises_nothing():
    assert types() == set()


def test_hr_limit_is_strict():
    assert "HR_OVERLOAD" not in types(hr=170)
    assert "HR_OVERLOAD" in types(hr=171)


def test_rpe_critical():
    assert "RPE_CRITICAL" in types(rpe=9.0)
    assert "RPE_CRITICAL" not in types(rpe=8.9)


def test_short_rest_uses_the_1rm_of_the_current_exercise():
    # 1RM estimated at 66.7 kg, so the heavy threshold is 46.7 kg.
    assert "SHORT_REST" in types(rest=60, weight=50.0)
    assert "SHORT_REST" not in types(rest=60, weight=40.0)


def test_fatigue_and_progress():
    assert "FATIGUE" in types(reps=8, rpe=8.0)
    assert "CAN_PROGRESS" in types(rpe=6.0)


@pytest.mark.parametrize("history,expected", [
    ([100, 100], False),
    ([100, 100, 100], True),
    ([100, 100, 100.9], True),
    ([100, 100, 102], False),
    ([90, 95, 100, 102, 102.5], False),
    ([100, 90, 100], True),
    ([120, 100, 100, 100, 100.5], True),
])
def test_plateau(history, expected):
    assert is_plateau(history) is expected
