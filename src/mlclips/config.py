from pathlib import Path
import json

APP_NAME = "MLClips"

CONFIG_DIR = (
    Path.home()
    / "Library"
    / "Application Support"
    / "Bisneto"
    / APP_NAME
)

CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "watch_directory": str(
        Path.home() / "Movies" / "MobileLegends"
    ),
    "output_directory": str(
        Path.home() / "Movies" / "MLClips"
    ),
    "video_extensions": [
        ".mp4",
        ".mov",
        ".mkv"
    ],
    "auto_detect": True,
    "auto_edit": True,
    "auto_publish": False
}


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            config,
            file,
            indent=4,
            ensure_ascii=False
        )