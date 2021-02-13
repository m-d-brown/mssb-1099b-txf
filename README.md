# mssb-1099b-to-txf

This repository provides `mssb_1099b_to_txf.py` to convert simple Morgan Stanley
Smith Barney (MSSB) 1099-B PDFs to TXF files that can be imported into TurboTax.
The goal is to reduce data entry rather than to completely automate the process,
meaning that you'll need to modify the entries in TurboTax afterwards. The tool
has been used to import only a few different 1099-Bs so you may encounter
errors.

The TXF format is relatively straightforward and text based. It's defined at
https://www.taxdataexchange.org/txf/txf-spec.html

The tool requires `pdftotext` from
[Poppler](https://github.com/freedesktop/poppler).

## Usage

```
$ ./mssb_1099b_to_txf.py ~/Downloads/1099-B.pdf > ~/1099b.txf
```

Then import `1099b.txf` into TurboTax. You'll likely need to add some fields
and **please** double-check the results.
