import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SCRIPTS = [
    "scripts/build_index.py",
    "scripts/build_dictionary.py",
    "scripts/build_kgram.py",
    "scripts/build_permuterm.py",
]

def rebuild_indexes():
    """
    Rebuild SEMUA index:
    - inverted index
    - dictionary (blocking + front coding)
    - k-gram
    - permuterm
    """

    for script in SCRIPTS:
        script_path = BASE_DIR / script

        if not script_path.exists():
            raise FileNotFoundError(f"{script} tidak ditemukan")

        print(f"[INDEXER] Running {script}")
        subprocess.run(
            ["python3", str(script_path)],
            check=True
        )

    print("[INDEXER] Semua index berhasil dibangun ulang")
