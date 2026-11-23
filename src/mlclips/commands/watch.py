import time

import click

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

from mlclips.config import load_config


console = Console()


class VideoHandler(FileSystemEventHandler):

    def __init__(self, extensions):
        self.extensions = extensions

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix.lower() not in self.extensions:
            return

        console.print(
            f"[green][+] Novo vídeo detectado:[/green] {path.name}"
        )

        # O processamento será integrado posteriormente.


@click.command()
def watch_command():
    """Monitor video directory for new recordings."""

    config = load_config()

    directory = Path(
        config["watch_directory"]
    ).expanduser()

    directory.mkdir(parents=True, exist_ok=True)

    extensions = tuple(
        config["video_extensions"]
    )

    event_handler = VideoHandler(extensions)

    observer = Observer()

    observer.schedule(
        event_handler,
        str(directory),
        recursive=False
    )

    observer.start()

    console.print(
        f"[bold green]MLClips[/bold green] - Monitoring started"
    )

    console.print(f"Directory: {directory}")
    console.print("Press CTRL+C to stop.\n")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping monitor...[/yellow]")

    finally:
        observer.stop()
        observer.join()
