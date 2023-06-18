from rich.console import Console

_c = Console()


class console():
    @staticmethod
    def debug(*msgs):
        _c.print(">>> DEBG", *msgs)

    @staticmethod
    def log(*msgs):
        _c.print(">>> [bold white]LOGS[/bold white]", *msgs)

    @staticmethod
    def info(*msgs):
        _c.print(">>> [bold cyan]INFO[/bold cyan]", *msgs)

    @staticmethod
    def warn(*msgs):
        _c.print(">>> [bold yellow]WARN[/bold yellow]", *msgs)

    @staticmethod
    def error(*msgs):
        _c.print(">>> [bold red]ERRR[/bold red]", *msgs)
