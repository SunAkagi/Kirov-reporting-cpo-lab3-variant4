import unittest
import logging
from moore_fsm_interpreter import (
    MooreMachine, MooreInterpreter, Transition, Validator
)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
            "| S1 | X |",
            "| S2 | Y |"
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

        trace2 = interpreter.trace(
            ["down", "arrived", "close", "up", "arrived", "close"]
        )
        self.assertEqual(
            trace2,
            ["IDLE", "DOWN", "OPEN", "IDLE", "UP", "OPEN", "IDLE"]
        )

    def test_crossroad_traffic_light(self):
        # States: Red_Main, Green_Main, Yellow_Main, Red_Ped, Green_Ped
        # Outputs: Main_Stop, Main_Go, Main_Slow, Ped_Stop, Ped_Go
        fsm = MooreMachine("CrossroadTrafficLight") \
            .state("Red_Main_Red_Ped", "Main_Stop_Ped_Stop") \
            .state("Green_Main_Red_Ped", "Main_Go_Ped_Stop") \
            .state("Yellow_Main_Red_Ped", "Main_Slow_Ped_Stop") \
            .state("Red_Main_Green_Ped", "Main_Stop_Ped_Go") \
            .state("Red_Main_Yellow_Ped", "Main_Stop_Ped_Slow") \
            .initial("Red_Main_Red_Ped") \
            .transition("Red_Main_Red_Ped", "Green_Main_Red_Ped",
                        "timer_main") \
            .transition("Green_Main_Red_Ped", "Yellow_Main_Red_Ped",
                        "timer_main") \
            .transition("Yellow_Main_Red_Ped", "Red_Main_Red_Ped",
                        "timer_main") \
            .transition("Red_Main_Red_Ped", "Red_Main_Green_Ped",
                        "ped_button") \
            .transition("Red_Main_Green_Ped", "Red_Main_Yellow_Ped",
                        "timer_ped") \
            .transition("Red_Main_Yellow_Ped", "Red_Main_Red_Ped",
                        "timer_ped")

        interpreter = MooreInterpreter(fsm)
        # Scenario 1: Main road cycle
        trace1 = interpreter.trace(["timer_main", "timer_main", "timer_main"])
        self.assertEqual(
            trace1,
            [
                "Main_Stop_Ped_Stop",
                "Main_Go_Ped_Stop",
                "Main_Slow_Ped_Stop",
                "Main_Stop_Ped_Stop",
            ],
        )

        # Scenario 2: Pedestrian button press
        interpreter = MooreInterpreter(fsm)  # Reset interpreter for new trace
        trace2 = interpreter.trace(["ped_button", "timer_ped", "timer_ped"])
        self.assertEqual(
            trace2,
            [
                "Main_Stop_Ped_Stop",
                "Main_Stop_Ped_Go",
                "Main_Stop_Ped_Slow",
                "Main_Stop_Ped_Stop",
            ],
        )

    def test_step_input_validation(self):
        fsm = MooreMachine("Test") \
            .state("A", "OutputA") \
            .initial("A")
        interpreter = MooreInterpreter(fsm)

        with self.assertRaises(TypeError):
            interpreter.step(123)  # Pass an integer instead of a string

        with self.assertRaises(TypeError):
            interpreter.step(None)  # Pass None instead of a string


if __name__ == '__main__':
    unittest.main()
