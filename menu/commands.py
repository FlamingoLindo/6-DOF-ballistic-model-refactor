"""
_summary_

Returns:
    _type_: _description_
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import IntPrompt
from rich import print as rprint

from monte_carlo.example_monte_carlo import eg_monte_carlo
from monte_carlo_prep.azimutal_scan_example import eg_azimutal_scan
from monte_carlo_prep.points_selection_example import points_selec_eg
from monte_carlo_prep.used_points_estat import used_points_estat

console = Console()


def menu_options():
    """_summary_

    Returns:
        _type_: _description_
    """
    console.clear()

    # ── welcome banner ──
    console.print(Panel.fit(
        "[bold cyan]DOF BALLISTIC MODEL REFACTOR[/bold cyan]\n"
        "[dim]ADD SMALL DESCRIPTION HERE[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan")  # key
    table.add_column(style="bold")       # label
    table.add_column(style="dim")        # description

    table.add_row("[1]", "Monte Carlo eg",      "Run Monte Carlo example")
    table.add_row("[2]", "Azimutal Scan eg",     "Run Azimutal Scan example")
    table.add_row("[3]", "Points Selection eg",         "Points Selection example")
    table.add_row("[4]", "Used Points stats",         "Used Points Statistics")
    table.add_row("[5]", "Exit",             "Quit ProjectX")

    console.print(table)
    console.print()

    choice = IntPrompt.ask(
        "[cyan]Choose an option[/cyan]",
        choices=["1", "2", "3", "4"],
        show_choices=False,
    )
    return choice


def run_command(func):
    """_summary_

    Args:
        func (_type_): _description_

    Returns:
        _type_: _description_
    """
    console.clear()
    func()
    console.print()
    console.input("[dim]Press Enter to return to menu...[/dim]")


def show_menu():
    """_summary_
    """
    while True:
        choice = menu_options()
        match choice:
            case 1: run_command(eg_monte_carlo)
            case 2: run_command(eg_azimutal_scan)
            case 3: run_command(points_selec_eg)
            case 4: run_command(used_points_estat)
            case 5:
                rprint("\n[dim]Goodbye 👋[/dim]\n")
                break
