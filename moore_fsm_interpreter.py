import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)

# -- Data Models -- #
@dataclass
class State:
    name: str
    output: Any

@dataclass
class Transition:
    source: str
    target: str
    event: str

@dataclass
class MooreMachine:
    name: str
    states: Dict[str, State] = field(default_factory=dict)
    transitions: List[Transition] = field(default_factory=list)
    initial_state: Optional[str] = None

    def state(self, name: str, output: Any):
        self.states[name] = State(name, output)
        return self

    def transition(self, source: str, target: str, on: str):
        self.transitions.append(Transition(source, target, on))
        return self

    def initial(self, state_name: str):
        self.initial_state = state_name
        return self

# -- Interpreter -- #
class MooreInterpreter:
    def __init__(self, machine: MooreMachine):
        self.machine = machine
        self.current_state = machine.initial_state
        self._validate()

    def _validate(self):
        assert self.current_state in self.machine.states, "Initial state undefined"
        for t in self.machine.transitions:
            assert t.source in self.machine.states, f"Undefined source: {t.source}"
            assert t.target in self.machine.states, f"Undefined target: {t.target}"

    def step(self, event: str) -> Any:
        for t in self.machine.transitions:
            if t.source == self.current_state and t.event == event:
                logging.info(f"Transition: {t.source} --[{event}]--> {t.target}")
                self.current_state = t.target
                return self.machine.states[self.current_state].output
        logging.warning(f"No transition for event '{event}' from state '{self.current_state}'")
        return self.machine.states[self.current_state].output

    def trace(self, events: List[str]) -> List[Any]:
        outputs = [self.machine.states[self.current_state].output]
        for e in events:
            outputs.append(self.step(e))
        return outputs

# -- Text Visualization -- #
def print_transitions(machine: MooreMachine):
    """Simple text-based visualization without external dependencies"""
    print(f"\nFSM: {machine.name}")
    print("States:", list(machine.states.keys()))
    print("Initial state:", machine.initial_state)
    print("\nTransitions:")
    for t in machine.transitions:
        print(f"  {t.source} --[{t.event}]--> {t.target}")

# -- Example Usage -- #
def traffic_light_example():
    fsm = MooreMachine("TrafficLight") \
        .state("Red", output="STOP") \
        .state("Green", output="GO") \
        .state("Yellow", output="SLOW") \
        .transition("Red", "Green", on="timer") \
        .transition("Green", "Yellow", on="timer") \
        .transition("Yellow", "Red", on="timer") \
        .initial("Red")

    interpreter = MooreInterpreter(fsm)
    trace = interpreter.trace(["timer", "timer", "timer", "timer"])
    print("Trace Output:", trace)

    print("\nText Visualization:")
    print_transitions(fsm)

if __name__ == "__main__":
    traffic_light_example()
