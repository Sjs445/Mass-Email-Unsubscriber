"""A simple printer class that prints in different colors."""


class colors:
    """The colors class"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_purple(output: str) -> None:
    """Print an error. Purple output.

    Args:
        output (str): The string to print.
    """
    print(f"{colors.HEADER}{output}{colors.ENDC}")


def print_error(output: str) -> None:
    """Print an error. Red output.

    Args:
        output (str): The string to print.
    """
    print(f"{colors.FAIL}{output}{colors.ENDC}")


def print_warning(output: str) -> None:
    """Print a warning. Yellow output.

    Args:
        output (str): The string to print.
    """
    print(f"{colors.WARNING}{output}{colors.ENDC}")


def print_success(output: str) -> None:
    """Print a success message. Green output.

    Args:
        output (str): The string to print.
    """
    print(f"{colors.OKGREEN}{output}{colors.ENDC}")
