"""Console entrypoint that prints runtime environment details."""

import platform
import sys


def main() -> None:
    """Print operating system and Python version, then exit."""
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()} ({sys.version.split()[0]})")


if __name__ == "__main__":
    main()
