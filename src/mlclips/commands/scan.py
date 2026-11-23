import click

from pathlib import Path
from rich.console import Console
from rich.table import Table

from mlclips.config import load_config
from mlclips.services.importer import (
    register_video,
    get_creation_date
)


console = Console()


@click.command()
def scan_command():
    """Scan and register gameplay recordings."""

    config = load_config()

    directory = Path(
        config["watch_directory"]
    ).expanduser()

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    extensions = {
        ext.lower()
        for ext in config["video_extensions"]
    }

    videos = [
        file
        for file in directory.iterdir()
        if file.is_file()
        and file.suffix.lower() in extensions
        and not file.name.startswith(".")
    ]

    videos.sort(
        key=lambda file: (
            get_creation_date(file),
            file.name.lower()
        )
    )

    table = Table(
        title="MLClips - Video Scanner"
    )

    table.add_column("ID", style="cyan")
    table.add_column("Filename")
    table.add_column("Status")
    table.add_column("Result")

    registered = 0
    existing = 0
    errors = 0

    for video in videos:

        try:
            result = register_video(video)

            is_new = result["new"]

            if is_new:
                registered += 1
                result_label = "[green]Imported[/green]"
            else:
                existing += 1
                result_label = "[dim]Already registered[/dim]"

            table.add_row(
                f'{result["id"]:06d}',
                result["filename"],
                result["status"],
                result_label
            )

        except Exception as error:

            errors += 1

            table.add_row(
                "-",
                video.name,
                "[red]Error[/red]",
                str(error)
            )

    console.print(table)

    console.print()
    console.print(f"[green]New videos:[/green] {registered}")
    console.print(f"[dim]Already registered:[/dim] {existing}")
    console.print(f"[red]Errors:[/red] {errors}")
    console.print(f"Total found: {len(videos)}")
