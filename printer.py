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


def print_progress(
    current_iteration: int,
    total: int,
    decimals: int = 1,
    bar_length: int = 100,
    prefix: str = "",
    suffix: str = "",
) -> None:
    """Print a message with a progress bar.

    Args:
        current_iteration (int): The current iteration.
        total (int): The total iterations to completion
        decimals (int, optional): number of decimals in complete percentage. Defaults to 1.
        bar_length (int, optional): The length of the progress bar. Defaults to 100.
        prefix (str, optional): A message for before the progress bar. Defaults to an empty string.
        suffix (str, optional): A message for after the progress bar. Defaults to an empty string.
    """
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (current_iteration / float(total))
    )
    filled_length = int(bar_length * current_iteration // total)
    bar = "█" * filled_length + ("-" * (bar_length - filled_length))
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="")

    # Print newline on complete
    if current_iteration == total:
        print()
