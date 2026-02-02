# mssb-1099b-to-txf

This repository provides `mssb_1099b_to_txf.py` to convert simple Morgan Stanley
Smith Barney (MSSB) 1099-B PDFs to TXF files that can be imported into TurboTax.
The goal is to reduce data entry rather than to completely automate the process,
meaning that you'll need to modify the entries in TurboTax afterwards. The tool
has been used to import only a few different 1099-Bs so you may encounter
errors.

The TXF format is relatively straightforward and text based. It's defined at
https://taxdataexchange.org/docs/txf/v042/index.html.

## Install

The tool requires that the `pdftotext` executable from
[Poppler](https://github.com/freedesktop/poppler) be available on your path. On
most distros this dependency can be satisfied by installing the `poppler-utils`
package using your disto's package manager, e.g. for Debian/Ubuntu run:
`sudo apt install poppler-utils`

## Usage

```
$ python3 mssb_1099b_to_txf.py ~/Downloads/1099-B.pdf > ~/1099b.txf
```

Then import `1099b.txf` into TurboTax. You'll likely need to add some fields
and **please** double-check the results.

## Development

### Running Tests

You can run the tests using the built-in `unittest` module:

```bash
python3 mssb_test.py
```

Or using `pytest` if installed:

```bash
pytest
```

### Type Checking

The project uses Python type hints. You can verify them using `mypy`:

```bash
# Install mypy if you haven't already
pip install mypy

# Run type check
mypy mssb_1099b_to_txf.py
```
