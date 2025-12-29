from run_debate import build_graph
from nodes.logger_node import LoggerNode
from nodes.agent_node import AgentNode
from nodes.memory_node import MemoryNode
from nodes.judge_node import JudgeNode
import os

def generate_dag(output_path="dag.png"):
    # Create dummy objects to initialize graph
    logger = LoggerNode("dummy_log.json")
    
    a_persona = os.path.join("persona_templates", "scientist.txt")
    b_persona = os.path.join("persona_templates", "philosopher.txt")
    
    agent_a = AgentNode("AgentA", persona_path=a_persona, seed=42, logger=logger)
    agent_b = AgentNode("AgentB", persona_path=b_persona, seed=43, logger=logger)
    memory_node = MemoryNode(logger=logger)
    judge_node = JudgeNode(logger=logger)
    
    # Build graph
    app = build_graph(agent_a, agent_b, memory_node, judge_node, logger, "dummy_topic", "dummy_log.json")
    
    try:
        png_data = app.get_graph().draw_mermaid_png()
        with open(output_path, "wb") as f:
            f.write(png_data)
        print(f"Generated DAG: {output_path}")
        return output_path
    except Exception as e:
        print(f"Failed to generate DAG: {e}")
        return None

if __name__ == "__main__":
    generate_dag()
