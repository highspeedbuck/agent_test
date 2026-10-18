"""Minimal hello world 5 script for REQ-0005."""

MESSAGE = "Hello World 5"
NAME_MESSAGE = "My name is Tan"


def main() -> None:
    """Print the greeting and the name line to stdout, in this order."""
    print(MESSAGE)
    print(NAME_MESSAGE)


if __name__ == "__main__":
    main()
