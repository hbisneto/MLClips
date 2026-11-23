import sqlite3
from pathlib import Path
from contextlib import contextmanager

from platformdirs import user_data_dir

# DATA_DIR = Path(user_data_dir("MLClips", "Bisneto"))
# DATABASE = DATA_DIR / "mlclips.db"

APP_DATA_DIR = (
    Path.home()
    / "Library"
    / "Application Support"
    / "Bisneto"
    / "MLClips"
)

DATABASE = APP_DATA_DIR / "mlclips.db"

@contextmanager
def get_connection():
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def initialize_database():

    with get_connection() as db:

        db.executescript("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                source_path TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                output_dir TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                output_path TEXT NOT NULL,
                start_time REAL,
                duration REAL,
                status TEXT NOT NULL DEFAULT 'pending',

                FOREIGN KEY(video_id)
                    REFERENCES videos(id)
            );

            CREATE TABLE IF NOT EXISTS upload_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clip_id INTEGER NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                published_at TEXT,
                error_message TEXT,

                FOREIGN KEY(clip_id)
                    REFERENCES clips(id)
            );
        """)

        # Migration for databases created with the earlier schema.
        columns = {
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(videos)"
            )
        }

        if "imported_at" not in columns:
            db.execute("""
                ALTER TABLE videos
                ADD COLUMN imported_at TEXT NOT NULL DEFAULT ''
            """)

        if "output_dir" not in columns:
            db.execute("""
                ALTER TABLE videos
                ADD COLUMN output_dir TEXT NOT NULL DEFAULT ''
            """)

        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_videos_status
            ON videos(status)
        """)

        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_upload_status
            ON upload_queue(status, id)
        """)
