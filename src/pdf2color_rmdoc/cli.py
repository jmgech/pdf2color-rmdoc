import argparse
import shutil
import subprocess
from pathlib import Path


def _which_or_die(cmd: str) -> str:
    p = shutil.which(cmd)
    if not p:
        raise SystemExit(
            f"ERROR: '{cmd}' not found in PATH.\n"
            f"Fix: install Drawj2d and ensure a 'drawj2d' executable is available.\n"
            f"Try: drawj2d -h"
        )
    return p


def run_drawj2d(input_pdf: Path, output_rmdoc: Path, resolution: int | None) -> None:
    drawj2d = _which_or_die("drawj2d")

    # Drawj2d consumes a simple script on stdin. We embed the PDF as an image.
    # Color is preserved only when Drawj2d's rmdoc backend maps the PDF colors.
    script = f"image {input_pdf.as_posix()}\n"

    argv = [drawj2d, "-Trmdoc", "-o", str(output_rmdoc)]
    if resolution is not None:
        argv.insert(2, f"-r{resolution}")

    proc = subprocess.run(
        argv,
        input=script,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"Drawj2d failed:\n{proc.stderr.strip()}\n{proc.stdout.strip()}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf2color-rmdoc",
        description="Convert a PDF to a reMarkable .rmdoc using Drawj2d (color-aware on Paper Pro when supported).",
    )
    p.add_argument("input_pdf", help="Path to input PDF")
    p.add_argument("-o", "--output", help="Output .rmdoc path (default: <input>.rmdoc)")
    p.add_argument(
        "--resolution",
        type=int,
        default=None,
        help="Optional scaling resolution (Drawj2d -rNNN). Example: 229 for Paper Pro scaling.",
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
