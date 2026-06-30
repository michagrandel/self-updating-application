"""Console entrypoint that prints runtime environment details."""

import platform
import sys

from selfupdatingapplication.update_check import check_for_updates


def main() -> None:
    """Print operating system and Python version, then exit."""
    check_for_updates()
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()} ({sys.version.split()[0]})")


if __name__ == "__main__":
    main()
