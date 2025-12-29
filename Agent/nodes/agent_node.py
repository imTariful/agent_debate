import os
import random
import json
import difflib
from typing import List


def is_duplicate(new_text: str, prior_texts: List[str], threshold: float = 0.75) -> bool:
    # use sequence matcher as a cheap semantic similarity proxy
    for t in prior_texts:
        ratio = difflib.SequenceMatcher(None, new_text.lower(), t.lower()).ratio()
        if ratio >= threshold:
            return True
    return False


class AgentNode:
    def __init__(self, name: str, persona_path: str, seed: int = 42, logger=None):
        self.name = name
        self.logger = logger
        self.persona_text = ""
        if os.path.exists(persona_path):
            with open(persona_path, "r", encoding="utf-8") as f:
                self.persona_text = f.read()
        self.rng = random.Random(seed)

    def take_turn(self, topic: str, relevant_memory: dict, current_round: int) -> str:
        # relevant_memory comes from MemoryNode (turns + summary)
        
        # internal duplication check logic moved here or relies on caller checking global history?
        # The prompt says: "Enforce turn control... no repeated arguments"
        # The agent should try to generate unique arguments. 
        # But `relevant_memory` only has last 2 turns.
        # We need check against global history?
        # The original code checked `memory.get("turns", [])`.
        # I will assume `relevant_memory["turns"]` passed here is what the agent SEES, 
        # but for duplication check it might need more? 
        # Actually proper agent design: Agent doesn't see everything, so it might repeat old stuff. 
        # The COORDINATOR or MEMORY node should reject it. 
        # But to keep it simple and reusing the simple logic: I will rely on the caller to handle rejection loop, 
        # OR passing the full history for the check.
        # Let's Stick to the signature: `relevant_memory` (dict from MemoryNode).
        # AND `all_turns` (list) for duplication check.
        
        pass 
        # Wait, I can't put comments in the function body effectively with this tool if I am rewriting it.
        # I will just write the code.
        
    def take_turn(self, topic: str, relevant_memory: dict, all_turns: List[dict], current_round: int) -> str:
        prior_texts = [t["text"] for t in all_turns]
        
        for attempt in range(5):
            # generate a short argument combining persona and seeded behavior
            base_templates = [
                f"As {self.name}, I contend that {topic} because {self._reason_phrase()}",
                f"{self._reason_phrase().capitalize()} is why {topic} matters, and {self._support_phrase()}",
                f"From my perspective ({self.persona_text.splitlines()[0] if self.persona_text else self.name}), {self._claim_phrase(topic)}",
            ]
            text = self.rng.choice(base_templates)
            
            # Simple local check if we want, but better to use the exact logic as before
            if is_duplicate(text, prior_texts):
                # try to vary
                text = text + " " + self._support_phrase()
            if is_duplicate(text, prior_texts):
                continue
                
            # log
            if self.logger:
                self.logger.log_event({"event":"agent_turn","agent":self.name,"text":text,"round":current_round})
            return text

        raise Exception("Could not generate a non-duplicate argument after attempts")

    def _reason_phrase(self):
        return self.rng.choice([
            "it presents measurable risks to public safety",
            "it fosters responsible development",
            "historical precedents suggest oversight is needed",
            "unchecked progress can cause long-term harm",
        ])

    def _support_phrase(self):
        return self.rng.choice([
            "for example, consider high-risk applications",
            "this can be addressed through standards",
            "society benefits when harms are mitigated",
            "case studies show meaningful impact",
        ])

    def _claim_phrase(self, topic):
        return self.rng.choice([
            f"{topic} should balance innovation with caution",
            f"we must consider ethical consequences of {topic}",
            f"regulation may be appropriate depending on risk profiles of {topic}",
        ])
