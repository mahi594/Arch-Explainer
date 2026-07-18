"""Renders each Diagram's Mermaid source into an actual image file using
mermaid-cli (mmdc), run locally via Node/npx — fully offline after the
first run downloads mermaid-cli's npm package (and the headless Chromium
it uses internally to render).

Shells out rather than using a Python Mermaid-rendering library: there
isn't a solid pure-Python one, and mmdc is the reference renderer Mermaid's
own team maintains, so output matches exactly what any Mermaid-aware
viewer would show.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from arch_explainer.models import Diagram


class MermaidCliNotAvailable(RuntimeError):
    """Raised when npx/node isn't on PATH — caller decides whether to skip
    image rendering or fail the whole pipeline over it."""


def _check_npx_available() -> None:
    if shutil.which("npx") is None:
        raise MermaidCliNotAvailable(
            "npx not found on PATH. Install Node.js (https://nodejs.org) to enable "
            "diagram image rendering, or run the pipeline with image rendering skipped."
        )


def _invoke_mmdc(cli_args: list[str]) -> subprocess.CompletedProcess:
    """Runs mmdc via npx, working around a Windows-specific subprocess quirk:
    Popen's CreateProcess-based execution doesn't apply the PATHEXT resolution
    a real shell does, so a bare "npx" (which on Windows is actually npx.CMD)
    can raise WinError 2 / FileNotFoundError even though `npx` works fine
    typed directly into a terminal.

    Resolving the full path via shutil.which fixes most environments. If a
    particular machine still hits FileNotFoundError even with the full path
    (rare, but seen in the wild), falling back to `cmd /c` — which does apply
    that resolution — covers it.
    """
    npx_path = shutil.which("npx")
    if npx_path is None:
        raise MermaidCliNotAvailable(
            "npx not found on PATH. Install Node.js (https://nodejs.org) to enable "
            "diagram image rendering, or run the pipeline with image rendering skipped."
        )

    try:
        return subprocess.run([npx_path, *cli_args], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        return subprocess.run(["cmd", "/c", "npx", *cli_args], check=True, capture_output=True, text=True)


def _estimate_canvas_size(mermaid_text: str) -> tuple[int, int]:
    """mmdc's default 800x600 canvas doesn't auto-scale to fit content — it
    squeezes whatever's in the diagram into that fixed size, so a dense
    diagram (the whole-repo architecture/class/call ones routinely have
    30-50+ nodes) ends up with text rendered at a couple pixels tall,
    which then looks blurry no matter how much you zoom into the image
    afterward. Sizing the canvas up front based on rough node count keeps
    text legible at the size it's actually rendered at.
    """
    node_count = mermaid_text.count('["') + mermaid_text.count('(["') + mermaid_text.count("\n  class ")
    node_count = max(node_count, 4)
    width = min(6000, max(1200, node_count * 160))
    height = min(4000, max(800, node_count * 90))
    return width, height


def render_diagram_image(diagram: Diagram, output_dir: Path, fmt: str = "png") -> Path:
    """Renders one Diagram's Mermaid source to `output_dir/{diagram.id}.{fmt}`.

    mmdc reads from a file, not stdin, so this writes the mermaid text to a
    temp .mmd file first. Raises on a genuine mmdc failure (e.g. invalid
    Mermaid syntax) rather than swallowing it — that's a real bug worth
    surfacing, not something to hide.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{diagram.id}.{fmt}"
    width, height = _estimate_canvas_size(diagram.mermaid)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False, encoding="utf-8") as f:
        f.write(diagram.mermaid)
        input_path = Path(f.name)

    try:
        _invoke_mmdc(
            [
                "--yes", "@mermaid-js/mermaid-cli",
                "-i", str(input_path),
                "-o", str(output_path),
                "-b", "white",
                "-t", "default",
                "-w", str(width),
                "-H", str(height),
                "-s", "2",
            ]
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"mmdc failed to render diagram '{diagram.id}':\n{e.stderr}") from e
    finally:
        input_path.unlink(missing_ok=True)

    return output_path


def render_diagram_images(
    diagrams: list[Diagram], output_dir: Path, fmt: str = "png", log=print
) -> list[Path]:
    """Renders every diagram to an image file, skipping (not failing the
    whole pipeline on) any single diagram that errors — one bad diagram
    shouldn't block the rest of Publish from finishing.

    Raises MermaidCliNotAvailable up front if npx isn't found at all, so
    the caller can decide once whether to skip this whole step rather than
    failing on every diagram individually.
    """
    _check_npx_available()

    written: list[Path] = []
    for diagram in diagrams:
        try:
            path = render_diagram_image(diagram, output_dir, fmt=fmt)
            written.append(path)
            log(f"        rendered {path}")
        except RuntimeError as e:
            log(f"        WARNING: skipped '{diagram.id}': {e}")

    return written