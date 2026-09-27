"""Validate the clean and executed notebook artifacts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "notebooks" / "Algorand_PS2_Fee_Choice_Game.ipynb"
EXECUTED = ROOT / "notebooks" / "Algorand_PS2_Fee_Choice_Game.executed.ipynb"


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main() -> None:
    clean = load(CLEAN)
    executed = load(EXECUTED)
    assert clean["nbformat"] == executed["nbformat"] == 4
    assert len(clean["cells"]) == len(executed["cells"]) == 28
    assert [cell["cell_type"] for cell in clean["cells"]] == [
        cell["cell_type"] for cell in executed["cells"]
    ]

    clean_code = [cell for cell in clean["cells"] if cell["cell_type"] == "code"]
    executed_code = [cell for cell in executed["cells"] if cell["cell_type"] == "code"]
    assert len(clean_code) == len(executed_code) == 13
    assert all(cell.get("execution_count") is None for cell in clean_code)
    assert all(cell.get("execution_count") is not None for cell in executed_code)

    errors = [
        output
        for cell in executed_code
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    assert not errors, errors
    assert all(cell.get("id") for cell in clean["cells"])
    assert all(cell.get("id") for cell in executed["cells"])
    print("Notebook validation passed: 28 cells, 13 executed code cells, 0 errors.")


if __name__ == "__main__":
    main()
