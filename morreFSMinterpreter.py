import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from graphviz import Digraph
from tabulate import tabulate

logging.basicConfig(level=logging.INFO)

# -- Data Models -- #
@dataclass
class State:
    name: str
    output: str

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

    def state(self, name: str, output: str):
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

    def step(self, event: str) -> str:
        for t in self.machine.transitions:
            if t.source == self.current_state and t.event == event:
                logging.info(f"Transition: {t.source} --[{event}]--> {t.target}")
                self.current_state = t.target
                return self.machine.states[self.current_state].output
        logging.warning(f"No transition for event '{event}' from state '{self.current_state}'")
        return self.machine.states[self.current_state].output

    def trace(self, events: List[str]) -> List[str]:
        outputs = [self.machine.states[self.current_state].output]
        for e in events:
            outputs.append(self.step(e))
        return outputs

# -- Visualization -- #
def visualize(machine: MooreMachine) -> str:
    dot = Digraph(name=machine.name)
    for state in machine.states.values():
        dot.node(state.name, label=f"{state.name}\n{state.output}")
    for t in machine.transitions:
        dot.edge(t.source, t.target, label=t.event)
    return dot.source

def print_transition_table(machine: MooreMachine):
    rows = [(t.source, t.event, t.target) for t in machine.transitions]
    print(tabulate(rows, headers=["From", "Event", "To"], tablefmt="github"))

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

    print("\nDOT Visualization:")
    print(visualize(fsm))

    print("\nTransition Table:")
    print_transition_table(fsm)

if __name__ == "__main__":
    traffic_light_example()
