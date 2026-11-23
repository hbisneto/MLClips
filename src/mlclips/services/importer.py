import json
import re

from datetime import datetime
from pathlib import Path

from mlclips.core.database import get_connection
from mlclips.config import load_config


def get_creation_date(path):
    stat = path.stat()

    timestamp = getattr(
        stat,
        "st_birthtime",
        stat.st_mtime
    )

    return datetime.fromtimestamp(
        timestamp
    ).astimezone().isoformat(timespec="seconds")


def create_directory_name(video_id, filename):
    name = Path(filename).stem

    name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        name
    ).strip("_")

    name = name[:60] or "gameplay"

    return f"{video_id:06d}_{name}"


def register_video(file_path):

    path = Path(file_path).expanduser().resolve()

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)

    config = load_config()

    output_root = Path(
        config["output_directory"]
    ).expanduser()

    processed_root = output_root / "processed"

    created_at = get_creation_date(path)

    imported_at = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with get_connection() as db:

        cursor = db.execute("""
            INSERT OR IGNORE INTO videos (
                original_filename,
                source_path,
                created_at,
                imported_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            path.name,
            str(path),
            created_at,
            imported_at
        ))

        inserted = cursor.rowcount == 1

        video = db.execute("""
            SELECT *
            FROM videos
            WHERE source_path = ?
        """, (str(path),)).fetchone()

        video_id = video["id"]

        directory_name = create_directory_name(
            video_id,
            path.name
        )

        output_dir = processed_root / directory_name

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        db.execute("""
            UPDATE videos
            SET output_dir = ?
            WHERE id = ?
        """, (
            str(output_dir),
            video_id
        ))

        metadata = {
            "id": video_id,
            "original_filename": path.name,
            "source_path": str(path),
            "created_at": created_at,
            "imported_at": imported_at,
            "status": "pending"
        }

        metadata_file = output_dir / "metadata.json"

        metadata_file.write_text(
            json.dumps(
                metadata,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        return {
            "id": video_id,
            "filename": path.name,
            "output_dir": str(output_dir),
            "status": video["status"],
            "new": inserted
        }
