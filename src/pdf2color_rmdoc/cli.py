import argparse
import os
import shutil
import subprocess
from pathlib import Path


def _find_drawj2d() -> str:
    """
    Resolve the drawj2d executable in a Homebrew-friendly way.

    Priority:
    1) PDF2COLOR_RMDOC_DRAWJ2D env var (set by Homebrew formula wrapper)
    2) drawj2d found in PATH
    """
    env_path = os.environ.get("PDF2COLOR_RMDOC_DRAWJ2D", "").strip()
    if env_path:
        p = Path(env_path).expanduser()
        if p.exists() and p.is_file():
            return str(p)

    p2 = shutil.which("drawj2d")
    if p2:
        return p2

    raise SystemExit(
        "ERROR: 'drawj2d' not found.\n"
        "Fix:\n"
        "  - If installed via Homebrew, reinstall/relink pdf2color-rmdoc.\n"
        "  - Otherwise, install Drawj2d and ensure 'drawj2d' is in your PATH.\n"
        "Test:\n"
        "  drawj2d -h"
    )


def run_drawj2d(input_pdf: Path, output_rmdoc: Path, resolution: int | None) -> None:
    drawj2d = _find_drawj2d()

    # Drawj2d consumes a simple script on stdin. We embed the PDF as an image.
    script = f"image {input_pdf.as_posix()}\n"

    argv: list[str] = [drawj2d, "-Trmdoc", "-o", str(output_rmdoc)]
    if resolution is not None:
        # Drawj2d accepts -rNNN to scale output for different device targets.
        argv.insert(2, f"-r{resolution}")

    proc = subprocess.run(
        argv,
        input=script,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "Unknown error"
        raise SystemExit(f"Drawj2d failed:\n{msg}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf2color-rmdoc",
        description=(
            "Convert a PDF to a reMarkable .rmdoc using Drawj2d "
            "(color-aware on Paper Pro when supported by the source PDF)."
        ),
    )
    p.add_argument("input_pdf", help="Path to input PDF")
    p.add_argument("-o", "--output", help="Output .rmdoc path (default: <input>.rmdoc)")
    p.add_argument(
        "--resolution",
        type=int,
        default=None,
        help="Optional scaling resolution (Drawj2d -rNNN). Example: 229 for Paper Pro.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    in_pdf = Path(args.input_pdf).expanduser().resolve()
    if not in_pdf.exists():
        raise SystemExit(f"ERROR: input file not found: {in_pdf}")
    if in_pdf.suffix.lower() != ".pdf":
        raise SystemExit("ERROR: input must be a .pdf")

    out_rmdoc = Path(args.output).expanduser().resolve() if args.output else in_pdf.with_suffix(".rmdoc")
    out_rmdoc.parent.mkdir(parents=True, exist_ok=True)

    if out_rmdoc.exists() and out_rmdoc.is_dir():
        raise SystemExit(f"ERROR: output is a directory: {out_rmdoc}")

    run_drawj2d(in_pdf, out_rmdoc, args.resolution)

    if not out_rmdoc.exists():
        raise SystemExit("ERROR: conversion finished but output .rmdoc not found (unexpected).")

    print(str(out_rmdoc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())