#!/usr/bin/env python

"""mssb_1099b_to_txf converts simple Morgan Stanley (MSSB) 1099-B PDFs to TXF files."""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterator, NamedTuple, Optional, TextIO

# Codes and structure are defined at
# https://taxdataexchange.org/docs/txf/v042/reference-numbers-by-form.html
CATEGORIES = {
        'Short Term – Noncovered Securities': '711',
        'Long Term – Noncovered Securities': '713',
}

# Match a section of sales for one sales category.
# The last line can say 'Total Short Term – Noncovered Securities' or
# 'Total Short Term Noncovered Securities' (without the hypen) so match
# only on "^Total".
CATEGORIES_PATTERN = '|'.join(CATEGORIES)
SECTION_EXPR = re.compile(
        r'^('+CATEGORIES_PATTERN+r')'
        r'(.*?)'
        r'^Total', re.DOTALL|re.MULTILINE)

# Fields: RefNumber Description CUSIP Quantity DateAcquired DateSold
#         GrossProceeds CostBasis
#
# Example:
#   1234 ALPHABET INC CL C
#   12345A678
#   1.000000 01/01/20 02/01/20 $2,000.00 $1,9999.00
#
# Example:
#   1234 ALPHABET INC CL C
#   12345A678
#   1.000000 VARIOUS 02/01/20 $2,000.00 $1,9999.00
ROW_EXPR = re.compile(
        r'^(?P<descr>(\w| )+)\s+'
        r'(?P<cusip>\w+)\s+'
        r'(?P<quantity>\d*\.\d+)\s+'
        r'(?P<acquired>(\d+/\d+/\d+|\w+))\s+'
        r'(?P<sold>\d+/\d+/\d+)\s+'
        r'(?P<proceeds>\$[0-9,.]+)\s+'
        r'(?P<cost>\$[0-9,.]+)\s', re.DOTALL|re.MULTILINE)


class Transaction(NamedTuple):
    description: str
    cusip: str
    quantity: str
    date_acquired: str
    date_sold: str
    proceeds: str
    cost_basis: str


def check_dependencies() -> None:
    """Checks if required system dependencies are installed."""
    if not shutil.which('pdftotext'):
        print("Error: 'pdftotext' is not found in your PATH.", file=sys.stderr)
        print("Please install 'poppler-utils' or 'poppler' via your package manager.", file=sys.stderr)
        sys.exit(1)

def format_share_quantity(quantity: str) -> str:
    if '.' in quantity:
        # Trim off trailing zeroes. If there is no remaining fractional part,
        # then also trim the decimal point.
        return quantity.rstrip('0').rstrip('.')
    return quantity


def parse_rows(text: str) -> Iterator[Transaction]:
    """Parses text content to yield Transaction objects."""
    for match in ROW_EXPR.finditer(text):
        yield Transaction(
            description=match.group('descr'),
            cusip=match.group('cusip'),
            quantity=match.group('quantity'),
            date_acquired=match.group('acquired'),
            date_sold=match.group('sold'),
            proceeds=match.group('proceeds'),
            cost_basis=match.group('cost'),
        )


def serialize_transaction(transaction: Transaction, entry_code: str) -> list[str]:
    """Serializes a single transaction into TXF format lines."""
    output_rows = []
    output_rows.append('TD')
    output_rows.append('N' + entry_code)
    output_rows.append('C1')
    output_rows.append('L1')

    # Form 8949 documents "100 sh. XYZ Co." as the example format.
    quantity = format_share_quantity(transaction.quantity)
    output_rows.append(f'P{quantity} sh. of {transaction.description}')

    output_rows.append('D' + transaction.date_acquired)
    output_rows.append('D' + transaction.date_sold)
    # These have a leading dollar sign.
    output_rows.append(transaction.cost_basis)
    output_rows.append(transaction.proceeds)
    output_rows.append("$")  # Wash sale. Leaving blank. They aren't handled here.
    output_rows.append('^')
    return output_rows


def parse_and_serialize_rows(text: str, entry_code: str) -> str:
    """Parses text and returns a serialized TXF string."""
    output_lines = []
    for transaction in parse_rows(text):
        output_lines.extend(serialize_transaction(transaction, entry_code))
    
    if output_lines:
        return '\n'.join(output_lines) + '\n'
    return ''

def parse_sections(text: str) -> Iterator[re.Match]:
    return SECTION_EXPR.finditer(text)


def write_txf(text: str, output_stream: TextIO) -> None:
    """Writes parsed PDF text to the output stream in TXF format."""
    output_stream.write('V042' + '\n')
    output_stream.write('A mssb_1099b_to_txf' + '\n')
    output_stream.write('D ' + datetime.datetime.now().strftime('%m/%d/%Y') + '\n')
    output_stream.write('^' + '\n')
    for section_match in parse_sections(text):
        entry_code = CATEGORIES[section_match.group(1)]
        contents = section_match.group(2)
        serialized = parse_and_serialize_rows(contents, entry_code)
        output_stream.write(serialized)


def main() -> None:
    check_dependencies()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_path',
        type=Path,
        help='The path to the 1099-B PDF document.')
    parser.add_argument(
        'output_path',
        nargs='?',
        default=None,
        type=Path,
        help=('The destination file name for the TXF output. If this argument '
              'is omitted, then the TXF output will print to stdout.'))
    args = parser.parse_args()
    
    if not args.input_path.exists():
        print(f"Error: Input file '{args.input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    try:
        text = subprocess.check_output(['pdftotext', '-raw', str(args.input_path), '-']).decode()
    except subprocess.CalledProcessError as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output_path:
        if args.output_path.exists():
            print(f'Error: Output path "{args.output_path}" already exists', file=sys.stderr)
            sys.exit(1)
        with args.output_path.open('w') as output_stream:
            write_txf(text, output_stream)
    else:
        write_txf(text, sys.stdout)

if __name__ == '__main__':
    main()
