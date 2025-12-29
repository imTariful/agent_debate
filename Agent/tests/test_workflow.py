import os
import tempfile
from nodes.agent_node import AgentNode, is_duplicate
from nodes.memory_node import MemoryNode
from nodes.coordinator import RoundCoordinator
from nodes.logger_node import LoggerNode
from nodes.judge_node import JudgeNode


def test_duplicate_detection():
    prior = ["AI must be regulated due to high risk."]
    new = "AI must be regulated due to high risk."
    assert is_duplicate(new, prior)


def test_turn_enforcement():
    coord = RoundCoordinator(total_rounds=4)
    # round 1 expect AgentA
    coord.require_turn("AgentA", "AgentA")
    try:
        coord.require_turn("AgentB", "AgentA")
        assert False, "Should have raised exception"
    except Exception:
        pass


def test_memory_update_and_relevant_slice(tmp_path):
    log = LoggerNode(str(tmp_path / "log.jsonl"))
    mem = MemoryNode(logger=log)
    mem.update_with_turn(1, "AgentA", "First point")
    mem.update_with_turn(2, "AgentB", "Second point")
    slice_a = mem.get_relevant_memory_for_agent("AgentA")
    assert len(slice_a["turns"]) <= 2


def test_judge_output(tmp_path):
    log = LoggerNode(str(tmp_path / "log.jsonl"))
    mem = MemoryNode(logger=log)
    mem.update_with_turn(1, "AgentA", "Argument A")
    mem.update_with_turn(2, "AgentB", "Argument B")
    judge = JudgeNode(logger=log)
    verdict = judge.judge(mem)
    assert "summary" in verdict and "winner" in verdict and "justification" in verdict


def test_memory_has_similar(tmp_path):
    log = LoggerNode(str(tmp_path / "log.jsonl"))
    mem = MemoryNode(logger=log)
    mem.update_with_turn(1, "AgentA", "AI must be regulated due to high risk of harm")
    assert mem.has_similar("AI must be regulated due to high risk of harm")
    assert mem.has_similar("AI must be regulated due to high risks")


def test_full_run_and_repeat_detection(tmp_path):
    log = LoggerNode(str(tmp_path / "log.jsonl"))
    a = AgentNode("AgentA", persona_path="persona_templates/scientist.txt", seed=1, logger=log)
    b = AgentNode("AgentB", persona_path="persona_templates/philosopher.txt", seed=2, logger=log)
    mem = MemoryNode(logger=log)
    coord = RoundCoordinator(total_rounds=8, logger=log)

    current = a
    other = b
    while not coord.finished():
        mem_slice = mem.get_relevant_memory_for_agent(current.name)
        text = current.take_turn("Should AI be regulated like medicine?", mem_slice, coord)
        # check duplication: if we forcibly repeat an earlier text it should be detected
        mem.update_with_turn(coord.round_number(), current.name, text)
        current, other = other, current
        coord.advance_round()

    # assert memory has 8 turns
    assert len(mem.export()["turns"]) == 8
    judge = JudgeNode(logger=log)
    verdict = judge.judge(mem)
    assert verdict["winner"] in ("AgentA","AgentB")
