import os
from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.custom_types import Function, FunctionResult, FunctionResultStatus
from typing import Tuple

def get_game_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """Simple state with nearby and total apples"""
    return current_state

def collect_apple(**kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    """Try to collect a nearby apple"""
    state = get_game_state_fn(None, {})
    nearby_apples = state.get('nearby_apples', 0)
    
    if nearby_apples > 0:
        actions.append("eat")
        return FunctionResultStatus.DONE, "Got apple", {"action": "collect"}
    
    return FunctionResultStatus.FAILED, "No apples nearby", {}

def switch_zone(**kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    """Switch between safe and danger zone"""
    actions.append("switch")
    return FunctionResultStatus.DONE, "Switching zones", {"action": "switch_zone"}

collect_fn = Function(
    fn_name="collect_apple",
    fn_description="Collect a nearby apple if one exists",
    args=[],
    executable=collect_apple
)

switch_fn = Function(
    fn_name="switch_zone",
    fn_description="Switch between safe and danger zones",
    args=[],
    executable=switch_zone
)

apple_collector_worker = WorkerConfig(
    id="apple_collector",
    worker_description="Collects apples",
    get_state_fn=get_game_state_fn,
    action_space=[collect_fn, switch_fn],
    instruction="""If nearby_apples > 0: collect_apple()
Then: if human_score > agent_score and not in_danger_zone: switch_zone()"""
)

def main(nearby_apples=2, total_apples=20, agent_score=1, human_score=20, in_danger_zone=False):
    global actions
    actions = []
    
    # Create initial state from parameters
    initial_state = {
        "nearby_apples": nearby_apples,
        "total_apples": total_apples,
        "agent_score": agent_score,
        "human_score": human_score,
        "in_danger_zone": in_danger_zone
    }
    
    # Update get_state_fn to use our initial state
    def get_state_with_params(function_result: FunctionResult, current_state: dict) -> dict:
        return initial_state
    
    agent = Agent(
        api_key=os.environ['VIRTUAL_API_KEY'],
        name="Simple Collector",
        agent_goal="Collect apples when nearby",
        agent_description="Collects nearby apples",
        get_agent_state_fn=get_state_with_params,
        workers=[apple_collector_worker]
    )

    agent.compile()
    agent.step()
    
    return actions

if __name__ == "__main__":
    # Example usage with default values
    actions = main(nearby_apples=2, total_apples=20, agent_score=10, human_score=4, in_danger_zone=True)
    print("\nActions taken:", actions)