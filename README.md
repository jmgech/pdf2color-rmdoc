# pdf2color-rmdoc

Convert a PDF to a reMarkable `.rmdoc` using Drawj2d.

This tool is designed for reMarkable Paper Pro. Color preservation depends on Drawj2d’s color mapping and on the colors used in the source PDF. Only supported exact colors may appear in color on the device.

## Requirements

- Drawj2d available as `drawj2d` in your PATH
- Java (OpenJDK recommended)
- Python 3.10 or newer

## Install (editable / development)

Create a virtual environment and install the project in editable mode:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install -e .

Verify the command is available:

    pdf2color-rmdoc -h

## Usage

Convert a PDF to `.rmdoc`:

    pdf2color-rmdoc input.pdf

Specify an output file:

    pdf2color-rmdoc input.pdf -o output.rmdoc

Optional scaling resolution (useful for Paper Pro):

    pdf2color-rmdoc input.pdf --resolution 229

## Notes on color support

Drawj2d supports color output for reMarkable Paper Pro notebooks, but only for a limited set of exact colors. PDFs using gradients or near colors may still appear partially or fully grayscale.

For full color fidelity, keeping the document as a PDF and importing it directly on the device may still be preferable.