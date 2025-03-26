#!/usr/bin/env python

"""mssb_1099b_to_txf converts simple Morgan Stanley (MSSB) 1099-B PDFs to TXF files."""

import datetime
import re
import subprocess
import sys

# Codes and structure are defined at
# https://www.taxdataexchange.org/txf/txf-spec.html
categories = {
        'Short Term – Noncovered Securities': '711',
        'Long Term – Noncovered Securities': '713',
}

# Match a section of sales for one sales category.
# The last line can say 'Total Short Term – Noncovered Securities' or
# 'Total Short Term Noncovered Securities' (without the hypen) so match
# only on "^Total".
categories_pattern = '|'.join(categories)
section_expr = re.compile(
        r'^('+categories_pattern+r')'
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
row_expr = re.compile(
        r'^(?P<descr>(\w| )+)\s+'
        r'(?P<cusip>\w+)\s+'
        r'(?P<quantity>\d*\.\d+)\s+'
        r'(?P<acquired>(\d+/\d+/\d+|\w+))\s+'
        r'(?P<sold>\d+/\d+/\d+)\s+'
        r'(?P<proceeds>\$[0-9,.]+)\s+'
        r'(?P<cost>\$[0-9,.]+)\s', re.DOTALL|re.MULTILINE)

def parseAndSerializeRows(text, entry_code):
    output_rows = []
    for match in row_expr.finditer(text):
        output_rows.append('TD')
        output_rows.append('N' + entry_code)
        output_rows.append('C1')
        output_rows.append('L1')
        # Form 8949 documents "100 sh. XYZ Co." as the example format.
        output_rows.append('P' + match.group('quantity') +
                           ' sh. of ' + match.group('descr'))
        output_rows.append('D' + match.group('acquired'))
        output_rows.append('D' + match.group('sold'))
        # These have a leading dollar sign.
        output_rows.append(match.group('cost'))
        output_rows.append(match.group('proceeds'))
        output_rows.append("$") # Wash sale. Leaving blank. They aren't handled here.
        output_rows.append('^')
    return '\n'.join(output_rows) + '\n'

def parse_sections(text):
    return section_expr.finditer(text)

def main():
    if len(sys.argv) != 2:
        sys.exit(f'Usage: {sys.argv[0]} path-to-1099b-pdf')
    text = subprocess.check_output(['pdftotext', '-raw', sys.argv[1], '-']).decode()

    print('V042')
    print('A mssb_1099b_to_txf')
    print('D ' + datetime.datetime.now().strftime('%m/%d/%Y'))
    print('^')
    for section_match in parse_sections(text):
        entry_code = categories[section_match.group(1)]
        contents = section_match.group(2)
        serialized = parseAndSerializeRows(contents, entry_code)
        sys.stdout.write(serialized)

if __name__ == '__main__':
    main()
