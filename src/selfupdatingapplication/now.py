"""Console entrypoint that prints the current local time."""

from datetime import datetime

from selfupdatingapplication.update_check import check_for_updates


def main() -> None:
    """Run update check, then print current local time and exit."""
    check_for_updates()
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
