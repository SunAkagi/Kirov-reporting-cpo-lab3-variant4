# Kirov reporting！- lab 2 - variant 4 - eDSL for Moore finite state machine

A Python implementation of a Moore machine interpreter with validation,
tracing, and unit tests. Designed for educational purposes to demonstrate
finite state machine concepts.

## Project Structure

- `moore_fsm_interpreter.py` -- Core implementation:
   - `Transition` dataclass for state transitions
   - `MooreMachine` builder class for FSM definition
   - `MooreInterpreter` class for execution and validation
- `moore_fsm_interpreter_test.py` -- Unit tests covering:
   - Basic state transitions
   - Input tracing
   - Error handling
   - Edge cases

## Features

- **Builder pattern** for intuitive FSM definition
- **Runtime validation** of state references
- **Step-by-step execution** with `step()` method
- **Full trace generation** with `trace()`
- **PEP 8 compliant** code style
- **100% test coverage** with unittest

## Usage Example

```python
from moore_fsm_interpreter import MooreMachine, MooreInterpreter

# Create a traffic light FSM
fsm = MooreMachine("TrafficLight") \
    .state("Red", "STOP") \
    .state("Yellow", "SLOW") \
    .state("Green", "GO") \
    .transition("Red", "Green", "timer") \
    .transition("Green", "Yellow", "timer") \
    .transition("Yellow", "Red", "timer") \
    .initial("Red")

# Simulate the machine
interpreter = MooreInterpreter(fsm)
print(interpreter.trace(["timer", "timer", "timer"]))
# Output: ['STOP', 'GO', 'SLOW', 'STOP']
```

## Contribution

- Implementation & Documentation: `Sun Jiajian (<sunakagi@163.com>)`  
- Test Development: `Yang Liang (<2663048219@qq.com>)`  

## Changelog

- **12.05.2025 - 1**
- fix the problem and add the readme

- **05.05.2025 - 0**
- Initial implementation.
- Basic tests.

## Design Notes

- **Moore vs Mealy**: Outputs are state-based (Moore) rather than transition-based
- **Immutable Design**: Machines cannot be modified after creation
- **Fail-Fast Validation**: All state references are checked during interpreter initialization
- **Minimal Dependencies**: Only requires Python standard library
- **Educational Focus**: Clear implementation over optimization
