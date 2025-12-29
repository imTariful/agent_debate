#!/usr/bin/env python3
"""CLI launcher for the debate workflow using LangGraph."""
import argparse
import sys
import os
from datetime import datetime
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from nodes.user_input_node import UserInputNode
from nodes.memory_node import MemoryNode
from nodes.agent_node import AgentNode
from nodes.judge_node import JudgeNode
from nodes.logger_node import LoggerNode
from nodes.graph_state import DebateState


def main():
    parser = argparse.ArgumentParser(description="Run a structured debate between two agents.")
    parser.add_argument("--topic", type=str, help="Topic to debate (if omitted, prompted)")
    parser.add_argument("--seed", type=int, default=42, help="Optional seed for deterministic runs")
    parser.add_argument("--log-path", type=str, default=None, help="Path to write the debate log")
    args = parser.parse_args()

    # Setup log path
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = args.log_path or f"debate_log_{ts}.jsonl"
    logger = LoggerNode(log_path)
    
    # Initialize implementation nodes
    user_node = UserInputNode(logger=logger)
    
    # Get Topic
    if args.topic:
        topic = args.topic
    else:
        topic = user_node.prompt_topic()
    
    topic_clean = user_node.validate_and_sanitize(topic)
    if not topic_clean:
        print("Invalid topic. Exiting.")
        sys.exit(1)

    print(f"Starting debate on: {topic_clean}")
    logger.log_event({"event":"start_debate","topic":topic_clean, "seed": args.seed})

    # Initialize Agents and Helpers
    a_persona = os.path.join("persona_templates", "scientist.txt")
    b_persona = os.path.join("persona_templates", "philosopher.txt")
    
    agent_a = AgentNode("AgentA", persona_path=a_persona, seed=args.seed, logger=logger)
    agent_b = AgentNode("AgentB", persona_path=b_persona, seed=args.seed + 1, logger=logger)
    memory_node = MemoryNode(logger=logger)
    judge_node = JudgeNode(logger=logger)

    app = build_graph(agent_a, agent_b, memory_node, judge_node, logger, topic_clean, log_path)

    # Run
    initial_state = {
        "messages": [], 
        "round_count": 0, 
        "summary": "", 
        "current_speaker": None
    }
    
    app.invoke(initial_state)

def build_graph(agent_a, agent_b, memory_node, judge_node, logger, topic_clean, log_path):
    # --- Graph Node Functions ---

    def call_agent_a(state: DebateState):
        current_round = state.get("round_count", 0) + 1 # Increment here effectively for the turn
        messages = state.get("messages", [])
        summary = state.get("summary", "")
        
        # Get relevant context
        relevant = memory_node.get_relevant_memory_for_agent("AgentA", messages, summary)
        
        # Generate text
        try:
            text = agent_a.take_turn(topic_clean, relevant, messages, current_round)
        except Exception as e:
            text = f"[ERROR] {str(e)}"
            if logger:
                logger.log_event({"event":"turn_error","agent":"AgentA","error":str(e)})

        entry = {"round": current_round, "agent": "AgentA", "text": text}
        print(f"[Round {current_round}] AgentA: {text}")
        
        return {
            "messages": [entry],
            "round_count": current_round, 
            "current_speaker": "AgentA"
        }

    def call_agent_b(state: DebateState):
        current_round = state.get("round_count", 0) + 1
        messages = state.get("messages", [])
        summary = state.get("summary", "")
        
        relevant = memory_node.get_relevant_memory_for_agent("AgentB", messages, summary)
        
        try:
            text = agent_b.take_turn(topic_clean, relevant, messages, current_round)
        except Exception as e:
            text = f"[ERROR] {str(e)}"
            if logger:
                logger.log_event({"event":"turn_error","agent":"AgentB","error":str(e)})

        entry = {"round": current_round, "agent": "AgentB", "text": text}
        print(f"[Round {current_round}] AgentB: {text}")

        return {
            "messages": [entry],
            "round_count": current_round,
            "current_speaker": "AgentB"
        }

    def update_memory(state: DebateState):
        # Update summary
        messages = state.get("messages", [])
        new_summary = memory_node.generate_summary(messages)
        return {
            "summary": new_summary,
            "current_speaker": state.get("current_speaker")
        }

    def call_judge(state: DebateState):
        messages = state.get("messages", [])
        summary = state.get("summary", "")
        verdict = judge_node.judge(messages, summary)
        
        print("\n[Judge] Summary of debate:")
        print(verdict["summary"])
        print(f"[Judge] Winner: {verdict['winner']}\nReason: {verdict['justification']}")
        
        if logger:
            logger.log_event({"event":"final_verdict","verdict":verdict})
        print(f"Log saved to {log_path}")
        
        return {"verdict": verdict}

    # --- Conditional Edge ---

    def route_turn(state: DebateState) -> Literal["AgentA", "AgentB", "Judge"]:
        rc = state.get("round_count", 0)
        
        # We need 8 rounds TOTAL. 
        if rc >= 8: 
            return "Judge"
        
        if rc % 2 == 1:
            return "AgentB"
        else:
            return "AgentA"

    # --- Build Graph ---
    workflow = StateGraph(DebateState)

    workflow.add_node("AgentA", call_agent_a)
    workflow.add_node("AgentB", call_agent_b)
    workflow.add_node("Memory", update_memory)
    workflow.add_node("Judge", call_judge)

    workflow.add_edge(START, "AgentA")
    workflow.add_edge("AgentA", "Memory")
    workflow.add_edge("AgentB", "Memory")

    workflow.add_conditional_edges(
        "Memory",
        route_turn,
        {
            "AgentA": "AgentA",
            "AgentB": "AgentB",
            "Judge": "Judge"
        }
    )

    workflow.add_edge("Judge", END)

    app = workflow.compile()
    
    # Generate Diagram
    try:
        png_data = app.get_graph().draw_mermaid_png()
        with open("dag.png", "wb") as f:
            f.write(png_data)
        # print("Generated DAG: dag.png") 
    except Exception:
        pass
        
    return app

if __name__ == "__main__":
    main()
