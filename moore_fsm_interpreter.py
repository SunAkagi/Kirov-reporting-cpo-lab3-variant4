from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Transition:
    source: str
    target: str
    on: str


class MooreMachine:
    def __init__(self, name: str):
        self.name = name
        self.states: Dict[str, str] = {}
        self.transitions: List[Transition] = []
        self.initial_state: str | None = None

    def state(self, name: str, output: str):
        self.states[name] = output
        return self

    def transition(self, source: str, target: str, on: str):
        self.transitions.append(Transition(source, target, on))
        return self

    def initial(self, state_name: str):
        self.initial_state = state_name
        return self

    def to_dot(self) -> str:
        lines = [f'digraph {self.name} {{']
        for state, output in self.states.items():
            label = f"{state}\\n{output}"
            lines.append(f'  {state} [label="{label}"];')
        for t in self.transitions:
            lines.append(f'  {t.source} -> {t.target} [label="{t.on}"];')
        lines.append("}")
        return "\n".join(lines)

    def to_markdown_table(self) -> str:
        """
        Returns a Markdown table showing state-to-output mapping.
        """
        lines = ["| State | Output |", "|-------|--------|"]
        for state, data in self.states.items():
            lines.append(f"| {state} | {data} |")
        return "\n".join(lines)

    def to_transition_table(self) -> str:
        """
        Returns a Markdown table of all transitions.
        """
        lines = ["| Source | Input | Target |", "|--------|--------|--------|"]
        for t in self.transitions:
            lines.append(f"| {t.source} | {t.on} | {t.target} |")
        return "\n".join(lines)


class Validator:
    @staticmethod
    def validate(machine: MooreMachine):
        if machine.initial_state not in machine.states:
            raise AssertionError(
                f"Initial state '{machine.initial_state}' is not defined."
            )
        for t in machine.transitions:
            if t.source not in machine.states:
                raise AssertionError(
                    f"Transition source '{t.source}' is undefined."
                )
            if t.target not in machine.states:
                raise AssertionError(
                    f"Transition target '{t.target}' is undefined."
                )


def validate_string_input(func):
    def wrapper(self, input_signal: str, *args, **kwargs):
        if not isinstance(input_signal, str):
            raise TypeError("Input signal must be a string.")
        return func(self, input_signal, *args, **kwargs)
    return wrapper


class MooreInterpreter:
    def __init__(self, machine: MooreMachine):
        self.machine = machine
        Validator.validate(machine)
        self.current_state = machine.initial_state
        self._print(
            f"FSM Initialized |
            Current State: {self.current_state} |
            Output: {self._current_output()}"
        )

    def _print(self, message: str):
        print(f"[FSM PROCESS] {message}")

    def _current_output(self) -> str:
        return self.machine.states[self.current_state]

    @validate_string_input
    def step(self, input_signal: str) -> str:
        if self.current_state is None:
            raise RuntimeError(
                "Current state is None, FSM not initialized properly"
            )

        self._print(f"┌─── Processing Input: '{input_signal}'")
        self._print(f"│ Current State: {self.current_state}")
        for t in self.machine.transitions:
            if t.source == self.current_state and t.on == input_signal:
                self._print(f"│ TRANSITION: {t.source} --[{t.on}]--> {t.target}")
                self.current_state = t.target
                break
        else:
            self._print(f"│ NO TRANSITION for input '{input_signal}'")
        
        output = self._current_output()
        self._print(f"└─── New State: {self.current_state} | Output: '{output}'")
        return output

    def trace(self, inputs: List[str]) -> List[str]:
        outputs = [self._current_output()]
        self._print(f"\n=== TRACE START ===")
        self._print(f"Initial Output: '{outputs[0]}'")
        
        for i, signal in enumerate(inputs, 1):
            self._print(f"\nStep {i}:")
            outputs.append(self.step(signal))
            self._print(f"Output Sequence: {outputs}")
        
        self._print("\n=== TRACE COMPLETE ===")
        return outputs


if __name__ == '__main__':
    elevator = MooreMachine("Elevator") \
        .state("Idle", "Waiting") \
        .state("MovingUp", "Up") \
        .state("MovingDown", "Down") \
        .state("DoorOpen", "Open") \
        .transition("Idle", "MovingUp", "call_up") \
        .transition("Idle", "MovingDown", "call_down") \
        .transition("MovingUp", "DoorOpen", "arrived") \
        .transition("MovingDown", "DoorOpen", "arrived") \
        .transition("DoorOpen", "Idle", "door_closed") \
        .initial("Idle")

    interpreter = MooreInterpreter(elevator)
    inputs = [
        "call_up",
        "arrived",
        "door_closed",
        "call_down",
        "arrived",
        "door_closed"
    ]
    print("Trace:", interpreter.trace(inputs))

    print("\nDOT representation:")
    print(elevator.to_dot())

    print("\nMarkdown Table:")
    print(elevator.to_markdown_table())
