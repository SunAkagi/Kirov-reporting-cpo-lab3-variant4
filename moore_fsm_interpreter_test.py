import unittest
from moore_fsm_interpreter import \
    MooreMachine, MooreInterpreter, Transition


class TestMooreFSM(unittest.TestCase):
    def test_simple_toggle(self):
        fsm = MooreMachine("Toggle") \
            .state("Off", output="0") \
            .state("On", output="1") \
            .transition("Off", "On", on="press") \
            .transition("On", "Off", on="press") \
            .initial("Off")

        interpreter = MooreInterpreter(fsm)
        trace = interpreter.trace(["press", "press", "press"])
        self.assertEqual(trace, ["0", "1", "0", "1"])

    def test_traffic_light(self):
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
        self.assertEqual(trace, ["STOP", "GO", "SLOW", "STOP", "GO"])

    def test_no_transition(self):
        fsm = MooreMachine("Static") \
            .state("Idle", output="WAIT") \
            .initial("Idle")

        interpreter = MooreInterpreter(fsm)
        trace = interpreter.trace(["unknown", "invalid"])
        self.assertEqual(trace, ["WAIT", "WAIT", "WAIT"])

    def test_invalid_state_reference(self):
        fsm = MooreMachine("Invalid") \
            .state("A", output="A") \
            .initial("A")

        fsm.transitions.append(Transition("A", "B", "go"))
        with self.assertRaises(AssertionError):
            MooreInterpreter(fsm)

    def test_invalid_initial_state(self):
        fsm = MooreMachine("BadInit")
        fsm.state("A", output="Hello")
        fsm.initial("Z")
        with self.assertRaises(AssertionError):
            MooreInterpreter(fsm)


if __name__ == '__main__':
    unittest.main()
