from typing import List
from .main import reflections, wins


def user_history_fingerprint() -> str:
    texts = [r.text for r in reflections.values()]
    return " | ".join(texts[-5:])


def suggested_wins() -> List[str]:
    return [w.win for w in wins][-3:]
