import base64
import json
from pathlib import Path

import pytest

from scripts.export_notebook_presentation import (
    UnsafeNotebookOutput,
    export_notebook,
    validate_export,
)

ONE_PIXEL_PNG = base64.b64encode(
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
).decode("ascii")


def _notebook() -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"kernelspec": {"name": "python3"}},
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Fixture analysis\n\n## 1. Objective\n\n"
                    "**Short answer.** Evidence remains visible.\n\n"
                    "The equation is $H=-\\sum p_i\\log_2p_i$.\n\n"
                    "| City | Median |\n|---|---:|\n| NYC | 0.85 |"
                ],
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {
                    "execution": {"iopub.status.idle": "2026-01-02T03:04:05Z"},
                    "presentation": {
                        "chart_alt": "A dot marks the fixture result.",
                        "chart_caption": "Fixture evidence caption.",
                    },
                },
                "source": ["display(result)"],
                "outputs": [
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {"image/png": ONE_PIXEL_PNG, "text/plain": ["<Figure>"]},
                    },
                    {
                        "output_type": "execute_result",
                        "execution_count": 1,
                        "metadata": {},
                        "data": {
                            "text/html": [
                                "<table><thead><tr><th>city</th><th>value</th></tr></thead>"
                                "<tbody><tr><td>NYC</td><td>0.85</td></tr></tbody></table>"
                            ],
                            "text/plain": ["  city  value\n0 NYC   0.85"],
                        },
                    },
                ],
            },
        ],
    }


def _write_notebook(path: Path, notebook: dict | None = None) -> None:
    path.write_text(json.dumps(notebook or _notebook()), encoding="utf-8")


def test_export_is_deterministic_and_preserves_safe_presentation_content(
    tmp_path: Path,
) -> None:
    source = tmp_path / "analysis.ipynb"
    _write_notebook(source)
    first_artifact = tmp_path / "first" / "analysis.json"
    second_artifact = tmp_path / "second" / "analysis.json"

    export_notebook(source, first_artifact, first_artifact.parent / "assets")
    export_notebook(source, second_artifact, second_artifact.parent / "assets")

    first = json.loads(first_artifact.read_text(encoding="utf-8"))
    second = json.loads(second_artifact.read_text(encoding="utf-8"))
    assert first == second
    assert first["title"] == "Fixture analysis"
    assert first["summary"] == "Evidence remains visible."
    assert first["generated_at"] == "2026-01-02T03:04:05Z"
    serialized = json.dumps(first)
    assert "$H=-\\\\sum p_i\\\\log_2p_i$" in serialized
    assert "| City | Median |" in serialized
    assert "display(result)" in serialized
    assert first["sections"][0]["blocks"][1]["outputs"][0]["alt"] == (
        "A dot marks the fixture result."
    )
    table = first["sections"][0]["blocks"][1]["outputs"][1]
    assert table["type"] == "table"
    assert table["headers"] == ["city", "value"]
    assert table["rows"] == [["NYC", "0.85"]]
    assert sorted(path.name for path in (first_artifact.parent / "assets").iterdir()) == sorted(
        path.name for path in (second_artifact.parent / "assets").iterdir()
    )


def test_export_rejects_active_or_unsupported_output(tmp_path: Path) -> None:
    source = tmp_path / "unsafe.ipynb"
    notebook = _notebook()
    notebook["cells"][1]["outputs"] = [
        {
            "output_type": "display_data",
            "metadata": {},
            "data": {"text/html": "<script>alert('no')</script>"},
        }
    ]
    _write_notebook(source, notebook)

    with pytest.raises(UnsafeNotebookOutput, match="active or unsupported HTML"):
        export_notebook(source, tmp_path / "analysis.json", tmp_path / "assets")


def test_validation_detects_stale_source_and_reexport_repairs_it(
    tmp_path: Path,
) -> None:
    source = tmp_path / "analysis.ipynb"
    artifact = tmp_path / "analysis.json"
    assets = tmp_path / "assets"
    _write_notebook(source)
    export_notebook(source, artifact, assets)

    validate_export(source, artifact, assets)
    changed = _notebook()
    changed["cells"][0]["source"].append("\nA changed interpretation.")
    _write_notebook(source, changed)

    with pytest.raises(ValueError, match="stale"):
        validate_export(source, artifact, assets)

    export_notebook(source, artifact, assets)
    validate_export(source, artifact, assets)


def test_validation_detects_changed_referenced_static_asset(tmp_path: Path) -> None:
    source = tmp_path / "analysis.ipynb"
    reference = tmp_path / "reference.png"
    notebook = _notebook()
    notebook["cells"][0]["source"].append("\n\n![Reference chart](reference.png)")
    _write_notebook(source, notebook)
    reference.write_bytes(base64.b64decode(ONE_PIXEL_PNG))
    artifact = tmp_path / "analysis.json"
    assets = tmp_path / "assets"
    export_notebook(source, artifact, assets)
    validate_export(source, artifact, assets)

    reference.write_bytes(b"changed image bytes")

    with pytest.raises(ValueError, match="stale"):
        validate_export(source, artifact, assets)
