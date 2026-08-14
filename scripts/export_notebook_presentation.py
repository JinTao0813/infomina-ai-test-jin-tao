"""Export an executed notebook into a deterministic, website-safe artifact."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
ACTIVE_CONTENT = re.compile(
    r"<(?:script|iframe|object|embed|form)\b|javascript:|\son\w+\s*=",
    re.IGNORECASE,
)
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)")
HEADING = re.compile(r"^(#{1,2})\s+(.+?)\s*$", re.MULTILINE)
SHORT_ANSWER = re.compile(
    r"\*\*Short answer\.\*\*\s*(.+?)(?:\n\n|$)", re.DOTALL | re.IGNORECASE
)


class UnsafeNotebookOutput(ValueError):
    """Raised when notebook content cannot be represented safely."""


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.header_rows: set[int] = set()
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._in_head = False
        self.saw_table = False
        self.unsupported = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        allowed = {"table", "thead", "tbody", "tfoot", "tr", "th", "td"}
        if tag not in allowed:
            self.unsupported = True
            return
        if tag == "table":
            if self.saw_table:
                self.unsupported = True
            self.saw_table = True
        elif tag == "thead":
            self._in_head = True
        elif tag == "tr":
            self._row = []
        elif tag in {"th", "td"}:
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"th", "td"} and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._in_head or not self.rows:
                self.header_rows.add(len(self.rows))
            self.rows.append(self._row)
            self._row = None
        elif tag == "thead":
            self._in_head = False

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)
        elif data.strip():
            self.unsupported = True


def _as_text(value: Any) -> str:
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return str(value)


def _slugify(value: str) -> str:
    value = re.sub(r"[*_`\[\]]", "", value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def _section_kind(title: str) -> str:
    lowered = title.lower()
    if any(word in lowered for word in ("method", "dataset", "quality", "preparation")):
        return "method"
    if any(word in lowered for word in ("comparison", "bias", "weekday", "weekend", "diversity")):
        return "observation"
    if any(word in lowered for word in ("opportunit", "insight", "evaluation")):
        return "hypothesis"
    if any(word in lowered for word in ("prototype", "architecture")):
        return "implementation"
    if any(word in lowered for word in ("limitation", "conclusion", "safeguard")):
        return "limitation"
    return "overview"


def _parse_table(html: str) -> dict[str, Any]:
    if ACTIVE_CONTENT.search(html):
        raise UnsafeNotebookOutput("active or unsupported HTML output")
    # Pandas display HTML wraps the table in a div and a scoped style block.
    # Neither reaches the artifact; only cell text is retained.
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"</?div\b[^>]*>", "", html, flags=re.IGNORECASE)
    parser = _TableParser()
    parser.feed(html)
    parser.close()
    if parser.unsupported or not parser.saw_table or not parser.rows:
        raise UnsafeNotebookOutput("active or unsupported HTML output")
    header_index = min(parser.header_rows) if parser.header_rows else 0
    return {
        "type": "table",
        "headers": parser.rows[header_index],
        "rows": [row for index, row in enumerate(parser.rows) if index != header_index],
    }


def _write_image(
    encoded: str,
    media_type: str,
    assets_dir: Path,
    cell_index: int,
    output_index: int,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    try:
        payload = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise UnsafeNotebookOutput("invalid base64 image output") from error
    extension = {"image/png": "png", "image/jpeg": "jpg"}[media_type]
    digest = hashlib.sha256(payload).hexdigest()
    filename = f"cell-{cell_index:03d}-output-{output_index:02d}-{digest[:12]}.{extension}"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / filename).write_bytes(payload)
    presentation = metadata.get("presentation", {})
    alt = str(presentation.get("chart_alt", "")).strip()
    caption = str(presentation.get("chart_caption", "")).strip()
    if not alt or not caption:
        raise UnsafeNotebookOutput(
            f"chart output in cell {cell_index} requires presentation chart_alt and chart_caption metadata"
        )
    return {
        "type": "image",
        "asset": filename,
        "sha256": digest,
        "alt": alt,
        "caption": caption,
    }


def _safe_outputs(
    cell: dict[str, Any], cell_index: int, assets_dir: Path
) -> list[dict[str, Any]]:
    safe: list[dict[str, Any]] = []
    for output_index, output in enumerate(cell.get("outputs", [])):
        output_type = output.get("output_type")
        if output_type == "error":
            raise UnsafeNotebookOutput(f"error output in cell {cell_index}")
        if output_type == "stream":
            text = _as_text(output.get("text", "")).strip()
            if text:
                safe.append({"type": "text", "text": text})
            continue
        if output_type not in {"display_data", "execute_result"}:
            raise UnsafeNotebookOutput(f"unsupported output type: {output_type}")
        data = output.get("data", {})
        unsupported = set(data) - {"text/plain", "text/html", "image/png", "image/jpeg"}
        if unsupported:
            raise UnsafeNotebookOutput(
                f"unsupported output media type: {sorted(unsupported)[0]}"
            )
        image_type = next((kind for kind in ("image/png", "image/jpeg") if kind in data), None)
        if image_type:
            safe.append(
                _write_image(
                    _as_text(data[image_type]),
                    image_type,
                    assets_dir,
                    cell_index,
                    output_index,
                    cell.get("metadata", {}),
                )
            )
        elif "text/html" in data:
            safe.append(_parse_table(_as_text(data["text/html"])))
        else:
            text = _as_text(data.get("text/plain", "")).strip()
            if text:
                safe.append({"type": "text", "text": text})
    return safe


def _copy_markdown_images(
    markdown: str, source: Path, assets_dir: Path, asset_url_prefix: str
) -> str:
    def replace(match: re.Match[str]) -> str:
        alt, target = match.groups()
        if target.startswith(("http://", "https://", "data:")):
            if target.startswith("data:"):
                raise UnsafeNotebookOutput("embedded markdown data image is unsupported")
            return match.group(0)
        image_path = (source.parent / target).resolve()
        if not image_path.is_file():
            raise UnsafeNotebookOutput(f"missing local markdown image: {target}")
        extension = image_path.suffix.lower()
        if extension not in {".png", ".jpg", ".jpeg", ".svg", ".webp"}:
            raise UnsafeNotebookOutput(f"unsupported markdown image: {target}")
        payload = image_path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        filename = f"reference-{digest[:12]}{extension}"
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / filename).write_bytes(payload)
        return f"![{alt}]({asset_url_prefix.rstrip('/')}/{filename})"

    return MARKDOWN_IMAGE.sub(replace, markdown)


def _generated_at(notebook: dict[str, Any]) -> str:
    timestamps = [
        str(cell.get("metadata", {}).get("execution", {}).get("iopub.status.idle"))
        for cell in notebook.get("cells", [])
        if cell.get("metadata", {}).get("execution", {}).get("iopub.status.idle")
    ]
    return max(timestamps) if timestamps else "Not recorded"


def export_notebook(
    source: Path,
    artifact_path: Path,
    assets_dir: Path,
    *,
    source_label: str | None = None,
    asset_url_prefix: str = "/generated/analysis",
) -> dict[str, Any]:
    """Create a deterministic safe JSON artifact and extracted static assets."""
    source = Path(source)
    artifact_path = Path(artifact_path)
    assets_dir = Path(assets_dir)
    raw = source.read_bytes()
    notebook = json.loads(raw)
    if notebook.get("nbformat") != 4:
        raise ValueError("only nbformat 4 notebooks are supported")

    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    title = source.stem.replace("_", " ").title()
    summary = ""
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    used_ids: set[str] = set()

    for cell_index, cell in enumerate(notebook.get("cells", [])):
        cell_type = cell.get("cell_type")
        source_text = _as_text(cell.get("source", [])).strip()
        if not source_text and not cell.get("outputs"):
            continue
        if cell_type == "markdown":
            if ACTIVE_CONTENT.search(source_text):
                raise UnsafeNotebookOutput(f"active content in markdown cell {cell_index}")
            h1 = re.search(r"^#\s+(.+?)\s*$", source_text, re.MULTILINE)
            if h1:
                title = h1.group(1).strip()
                source_text = source_text[: h1.start()] + source_text[h1.end() :]
            h2_matches = list(re.finditer(r"^##\s+(.+?)\s*$", source_text, re.MULTILINE))
            chunks: list[tuple[str | None, str]] = []
            if h2_matches:
                preamble = source_text[: h2_matches[0].start()].strip()
                if preamble:
                    chunks.append((None, preamble))
                for match_index, h2 in enumerate(h2_matches):
                    end = (
                        h2_matches[match_index + 1].start()
                        if match_index + 1 < len(h2_matches)
                        else len(source_text)
                    )
                    chunks.append((h2.group(1).strip(), source_text[h2.end() : end].strip()))
            else:
                chunks.append((None, source_text.strip()))

            for section_title, markdown_chunk in chunks:
                if section_title is not None:
                    section_id = _slugify(re.sub(r"^\d+\.\s*", "", section_title))
                    base_id = section_id
                    suffix = 2
                    while section_id in used_ids:
                        section_id = f"{base_id}-{suffix}"
                        suffix += 1
                    used_ids.add(section_id)
                    current = {
                        "id": section_id,
                        "title": section_title,
                        "kind": _section_kind(section_title),
                        "blocks": [],
                    }
                    sections.append(current)
                if current is None:
                    current = {"id": "overview", "title": "Overview", "kind": "overview", "blocks": []}
                    sections.append(current)
                markdown_chunk = _copy_markdown_images(
                    markdown_chunk, source, assets_dir, asset_url_prefix
                )
                if markdown_chunk:
                    current["blocks"].append({"type": "markdown", "markdown": markdown_chunk})
            if not summary:
                match = SHORT_ANSWER.search(_as_text(cell.get("source", [])))
                if match:
                    summary = " ".join(match.group(1).split())
        elif cell_type == "code":
            if current is None:
                current = {"id": "setup", "title": "Setup", "kind": "method", "blocks": []}
                sections.append(current)
            outputs = _safe_outputs(cell, cell_index, assets_dir)
            current["blocks"].append(
                {
                    "type": "code",
                    "execution_count": cell.get("execution_count"),
                    "source": source_text,
                    "outputs": outputs,
                }
            )
        elif cell_type != "raw":
            raise UnsafeNotebookOutput(f"unsupported cell type: {cell_type}")

    artifact = {
        "schema_version": SCHEMA_VERSION,
        "title": title,
        "summary": summary,
        "source_notebook": source_label or source.name,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "generated_at": _generated_at(notebook),
        "sections": sections,
    }
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return artifact


def validate_export(source: Path, artifact_path: Path, assets_dir: Path) -> None:
    """Fail clearly when the artifact is stale, malformed, or missing assets."""
    source = Path(source)
    artifact_path = Path(artifact_path)
    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise ValueError("generated notebook artifact is missing or malformed") from error
    if artifact.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("generated notebook artifact schema is unsupported")
    current = hashlib.sha256(source.read_bytes()).hexdigest()
    if artifact.get("source_sha256") != current:
        raise ValueError("generated notebook artifact is stale")
    for section in artifact.get("sections", []):
        for block in section.get("blocks", []):
            for output in block.get("outputs", []):
                if output.get("type") != "image":
                    continue
                asset = Path(assets_dir) / output["asset"]
                if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != output.get("sha256"):
                    raise ValueError(f"generated notebook asset is stale or missing: {asset.name}")

    # Re-export into isolation so referenced static images and every structured
    # block are checked, not only the notebook byte fingerprint.
    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)
        expected_artifact = temporary_root / "analysis.json"
        expected_assets = temporary_root / "assets"
        expected = export_notebook(
            source,
            expected_artifact,
            expected_assets,
            source_label=artifact.get("source_notebook"),
        )
        if expected != artifact:
            raise ValueError("generated notebook artifact is stale")
        committed_assets = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in Path(assets_dir).iterdir()
            if path.is_file()
        }
        regenerated_assets = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in expected_assets.iterdir()
            if path.is_file()
        }
        if committed_assets != regenerated_assets:
            raise ValueError("generated notebook assets are stale or malformed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--source-label")
    parser.add_argument("--asset-url-prefix", default="/generated/analysis")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate_export(args.source, args.artifact, args.assets)
        print(f"Fresh: {args.artifact}")
    else:
        export_notebook(
            args.source,
            args.artifact,
            args.assets,
            source_label=args.source_label,
            asset_url_prefix=args.asset_url_prefix,
        )
        print(f"Exported: {args.artifact}")


if __name__ == "__main__":
    main()
