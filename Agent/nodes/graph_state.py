from typing import TypedDict, List, Annotated
import operator

class DebateState(TypedDict):
    # The list of messages in the conversation
    messages: Annotated[List[dict], operator.add]
    # Current round number (1-8)
    round_count: int
    # Summary of the conversation so far
    summary: str
    # The final verdict from the judge
    verdict: dict
