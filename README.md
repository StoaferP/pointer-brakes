# pointer-brakes

[![PyPI - Version](https://img.shields.io/pypi/v/pointer-brakes.svg)](https://pypi.org/project/pointer-brakes)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pointer-brakes.svg)](https://pypi.org/project/pointer-brakes)
![Pointer Brakes logo -- generated with OpenAI DALL-E 3](https://chrisargyle.github.io/pointer-brakes/pointer-brakes-logo.png)

-----

Pointer Brakes is a library for simulating mouse pointer motion.  The pointer will behave like it is a little car with brakes.  If you push it, it moves.  If you let go, it keeps moving but slowly comes to a stop as it applies the brakes.


**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install pointer-brakes
```

## Usage

```python
a_brakes = 1
sim_instance = PointerMotionSim(a_brakes)
sim_instance.tick(time.monotonic(), (-52, -5))
sim_instance.tick(time.monotonic(), (21, -92))
change_in_position = sim_instance.delta_position
```

For more information check out the [documentation](https://chrisargyle.github.io/pointer-brakes).

## License

`pointer-brakes` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
