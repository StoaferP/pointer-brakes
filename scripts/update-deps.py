"""Update dependencies in all envs"""

import json
import subprocess


def main():
    # get envs from hatch
    envs: dict = json.loads(
        subprocess.check_output(["hatch", "--no-color", "env", "show", "--json"], encoding="utf-8")  # noqa: S607
    )

    # run a dummy command in each env causing hatch to ensure deps are in sync
    for env in envs:
        subprocess.check_output(["hatch", "env", "run", "--env", env, "--", "python", "--version"])  # noqa: S607


if __name__ == "__main__":
    main()
