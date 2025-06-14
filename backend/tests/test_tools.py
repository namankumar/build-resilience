import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.tools import user_history_fingerprint, suggested_wins
from app.main import reflections, wins, Reflection


def test_tools():
    """Validate ``user_history_fingerprint`` and ``suggested_wins`` helpers."""
    reflections[1] = Reflection(id=1, text="first", mood=None)
    reflections[2] = Reflection(id=2, text="second", mood=None)
    wins.clear()
    from app.main import Win
    wins.append(Win(reflection_id=1, win="walk"))
    assert user_history_fingerprint() == "first | second"
    assert suggested_wins() == ["walk"]
