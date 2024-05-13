import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from shutil import rmtree, copy
from shared.time_utils import now_utc


def copy_file(path_from: Path, path_to: Path, new_name: str = None) -> None:
    """Copying a file"""
    path_to.mkdir(parents=True, exist_ok=True)

    if not new_name:
        full_path_to = path_to.joinpath(path_from.name)
    else:
        full_path_to = path_to.joinpath(new_name)

    copy(path_from, full_path_to, follow_symlinks=True)


def save_json(path: Path, data: dict) -> None:
    """Saving json to file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="UTF-8") as target:
        json.dump(data, target, indent=4, ensure_ascii=False)


def load_json(path: Path) -> dict | None:
    """Loading json from file"""
    try:
        with path.open("r", encoding="UTF-8") as target:
            data = json.load(target)
        return data
    except Exception:
        return None


def save_string_to_file(path: Path, file: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(file, encoding='utf-8')


def remove_file(path: Path) -> None:
    if path.exists() and path.is_file():
        path.unlink()


def remove_files_older_than(path: Path, expiration: timedelta) -> None:
    paths = sorted(path.glob('*'))
    for path in paths:
        time_create_unix = path.stat().st_ctime
        time_create = datetime.fromtimestamp(time_create_unix).astimezone(timezone.utc)
        if time_create + expiration < now_utc():
            remove_file(path)


def remove_folder(path: Path) -> None:
    if path.exists() and path.is_dir():
        rmtree(path)


def create_path(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_string_from_file(path: Path) -> str | None:
    if path.exists() and path.is_file():
        return path.read_text(encoding='utf-8')
