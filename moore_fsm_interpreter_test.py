import unittest
from moore_fsm_interpreter import (
    MooreMachine, MooreInterpreter, Transition, Validator
)


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

        # Add invalid transition to undefined state "B"
        fsm.transitions.append(Transition("A", "B", "go"))
        with self.assertRaises(AssertionError):
            Validator.validate(fsm)

    def test_invalid_initial_state(self):
        fsm = MooreMachine("BadInit")
        fsm.state("A", output="Hello")
        fsm.initial("Z")  # Invalid initial state
        with self.assertRaises(AssertionError):
            Validator.validate(fsm)

    def test_to_dot(self):
        fsm = MooreMachine("DotTest") \
            .state("A", output="a") \
            .state("B", output="b") \
            .transition("A", "B", "go") \
            .initial("A")
        dot_output = fsm.to_dot()
        self.assertIn("digraph", dot_output)
        self.assertIn("A", dot_output)
        self.assertIn("B", dot_output)
        self.assertIn("go", dot_output)

    def test_to_markdown_table(self):
        fsm = MooreMachine("MDTest") \
            .state("S1", output="X") \
            .state("S2", output="Y") \
            .transition("S1", "S2", "next") \
            .initial("S1")
        table = fsm.to_markdown_table()
        expected_lines = [
            "| State | Output |",
            "|-------|--------|",
            "| S1    | X      |",
            "| S2    | Y      |"
        ]
        for line in expected_lines:
            self.assertIn(line, table)
    
    def test_to_transition_table(self):
        fsm = MooreMachine("TRTest") \
            .state("S1", output="A") \
            .state("S2", output="B") \
            .transition("S1", "S2", "go") \
            .initial("S1")
        table = fsm.to_transition_table()
        expected_lines = [
            "| Source | Input | Target |",
            "|--------|--------|--------|",
            "| S1 | go | S2 |"
        ]
        for line in expected_lines:
            self.assertIn(line, table)

    def test_elevator_controller(self):
        fsm = MooreMachine("Elevator") \
            .state("Idle", "IDLE") \
            .state("MovingUp", "UP") \
            .state("MovingDown", "DOWN") \
            .state("DoorOpen", "OPEN") \
            .transition("Idle", "MovingUp", "up") \
            .transition("Idle", "MovingDown", "down") \
            .transition("MovingUp", "DoorOpen", "arrived") \
            .transition("MovingDown", "DoorOpen", "arrived") \
            .transition("DoorOpen", "Idle", "close") \
            .initial("Idle")

        interpreter = MooreInterpreter(fsm)
        trace = interpreter.trace(["up", "arrived", "close"])
        self.assertEqual(trace, ["IDLE", "UP", "OPEN", "IDLE"])

        trace2 = interpreter.trace(["down", "arrived", "close", "up", "arrived", "close"])
        self.assertEqual(trace2, ["IDLE", "DOWN", "OPEN", "IDLE", "UP", "OPEN", "IDLE"])


if __name__ == '__main__':
    unittest.main()
