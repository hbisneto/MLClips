import click

from rich.console import Console
from rich.panel import Panel

from mlclips.core.database import initialize_database
from mlclips.commands.watch import watch_command
from mlclips.commands.scan import scan_command
from mlclips.commands.process import process_command
from mlclips.commands.publish import publish_command
from mlclips.commands.status import status_command


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """MLClips - Mobile Legends Highlights Automation."""

    initialize_database()
    pass


main.add_command(watch_command, name="watch")
main.add_command(scan_command, name="scan")
main.add_command(process_command, name="process")
main.add_command(publish_command, name="publish")
main.add_command(status_command, name="status")


if __name__ == "__main__":
    main()
