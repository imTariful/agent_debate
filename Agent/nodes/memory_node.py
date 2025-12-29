import json
from typing import List


class MemoryNode:
    def __init__(self, logger=None):
        self.logger = logger

    def get_relevant_memory_for_agent(self, agent_name: str, turns: List[dict], summary: str) -> dict:
        # Supply only last two turns and a short summary to each agent
        last_turns = turns[-2:]
        mem = {"turns": last_turns, "summary": summary}
        if self.logger:
            self.logger.log_event({"event":"memory_requested","agent":agent_name,"memory_snapshot":mem})
        return mem

    def get_all_texts(self, turns: List[dict]):
        return [t["text"] for t in turns]

    def has_similar(self, text: str, turns: List[dict], threshold: float = 0.75) -> bool:
        # check against all prior turns for substantial similarity
        import difflib

        for t in self.get_all_texts(turns):
            ratio = difflib.SequenceMatcher(None, text.lower(), t.lower()).ratio()
            if ratio >= threshold:
                if self.logger:
                    self.logger.log_event({"event":"duplicate_detected","text":text,"matched":t,"ratio":ratio})
                return True
        return False

    def generate_summary(self, turns: List[dict]) -> str:
        # simplistic summary update: append bullet
        summary_parts = [t["text"] for t in turns[-4:]]
        summary = " | ".join(summary_parts)
        if self.logger:
            self.logger.log_event({"event":"summary_updated","summary":summary})
        return summary
