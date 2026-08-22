"""Export Terrible Ninja timing data from the desktop source for the web game."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT_DIR / "Terrible_Ninja" / "main.py"
OUTPUT_PATH = ROOT_DIR / "static" / "data" / "terrible_ninja.json"


def read_literal_assignment(tree: ast.AST, name: str):
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f"Assignment not found: {name}")


def main() -> None:
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    notes = read_literal_assignment(tree, "justtime_notes")
    change_notes = read_literal_assignment(tree, "changetime_notes")

    justtimes = [note["justtime"] for note in notes]
    payload = {
        "justtimes": justtimes,
        "enemyJusttimes": [round(value - 5.991, 3) for value in justtimes[:-1]],
        "changeTimes": [note["changetime"] for note in change_notes],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Exported timing data to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
