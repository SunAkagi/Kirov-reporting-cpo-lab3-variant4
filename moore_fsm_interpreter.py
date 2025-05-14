from dataclasses import dataclass


@dataclass
class Transition:
    source: str
    target: str
    on: str


class MooreMachine:
    def __init__(self, name):
        self.name = name
        self.states = {}
        self.transitions = []
        self.initial_state = None


    def state(self, name, output):
        self.states[name] = output
        return self


    def transition(self, source, target, on):
        self.transitions.append(Transition(source, target, on))
        return self


    def initial(self, state_name):
        self.initial_state = state_name
        return self


class MooreInterpreter:
    def __init__(self, machine):
        self.machine = machine
        self.current_state = machine.initial_state
        self._validate()


    def _validate(self):
        assert self.current_state in self.machine.states, \
            "Initial state undefined"
        for t in self.machine.transitions:
            assert t.source in self.machine.states, \
                f"Undefined source: {t.source}"
            assert t.target in self.machine.states, \
                f"Undefined target: {t.target}"


    def step(self, input_signal):
        for t in self.machine.transitions:
            if t.source == self.current_state and t.on == input_signal:
                self.current_state = t.target
                break
        return self.machine.states[self.current_state]


    def trace(self, inputs):
        output = [self.machine.states[self.current_state]]
        for signal in inputs:
            output.append(self.step(signal))
        return output


if __name__ == '__main__':
    fsm = MooreMachine("Toggle") \
        .state("Off", output="0") \
        .state("On", output="1") \
        .transition("Off", "On", on="press") \
        .transition("On", "Off", on="press") \
        .initial("Off")

    interpreter = MooreInterpreter(fsm)
    print(interpreter.trace(["press", "press", "press"]))
