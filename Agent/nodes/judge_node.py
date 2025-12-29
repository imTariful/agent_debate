import collections
from typing import Dict


class JudgeNode:
    def __init__(self, logger=None):
        self.logger = logger

    def judge(self, turns: list, summary: str) -> Dict:

        # basic scoring: count novel (non-duplicate) phrases and topic overlap
        scores = collections.Counter()
        topic = "" if not turns else self._infer_topic(turns[0]["text"]) or ""

        for t in turns:
            agent = t["agent"]
            text = t["text"]
            score = 0
            score += len(text.split())
            # novelty heuristic: penalize reused short suffixes
            if text.count(" ") < 5:
                score -= 1
            # topic overlap
            if topic and any(word.lower() in text.lower() for word in topic.split()):
                score += 2
            scores[agent] += score

        # determine winner
        winner = scores.most_common(1)[0][0] if scores else "AgentA"

        justification = f"{winner} had higher aggregate score ({scores})."
        verdict = {"summary": summary, "winner": winner, "justification": justification, "scores": dict(scores)}
        if self.logger:
            self.logger.log_event({"event":"judge_verdict","verdict":verdict})
        return verdict

    def _infer_topic(self, text: str) -> str:
        # crude guess: pick words that are not stopwords (very simple)
        words = [w for w in text.split() if len(w) > 3]
        return " ".join(words[:3])
