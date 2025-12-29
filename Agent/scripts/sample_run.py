"""Generate a deterministic sample debate and write log and dag outputs."""
from datetime import datetime
import os
import sys

# Ensure project root is on sys.path so sibling packages like `nodes` can be imported when
# running this script directly (python scripts/sample_run.py) as sys.path[0] is then
# the `scripts/` directory, not the project root.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from nodes.logger_node import LoggerNode
from nodes.agent_node import AgentNode
from nodes.memory_node import MemoryNode
from nodes.coordinator import RoundCoordinator
from nodes.judge_node import JudgeNode


def run_sample(topic="Should AI be regulated like medicine?", seed=123, out_log=None):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = out_log or f"debate_log_{ts}.jsonl"
    logger = LoggerNode(log_path)

    agent_a = AgentNode("AgentA", persona_path="persona_templates/scientist.txt", seed=seed, logger=logger)
    agent_b = AgentNode("AgentB", persona_path="persona_templates/philosopher.txt", seed=seed+1, logger=logger)
    mem = MemoryNode(logger=logger)
    coord = RoundCoordinator(total_rounds=8, logger=logger)

    logger.log_event({"event":"start_debate","topic":topic,"seed":seed})
    current, other = agent_a, agent_b
    while not coord.finished():
        mem_slice = mem.get_relevant_memory_for_agent(current.name)
        text = current.take_turn(topic, mem_slice, coord)
        mem.update_with_turn(coord.round_number(), current.name, text)
        current, other = other, current
        coord.advance_round()

    judge = JudgeNode(logger=logger)
    verdict = judge.judge(mem)
    logger.log_event({"event":"final_verdict","verdict":verdict})
    print(f"Sample run complete. Log: {log_path}")


if __name__ == "__main__":
    run_sample()
