#!/usr/bin/env python

"""mssb_1099b_to_txf converts simple Morgan Stanley (MSSB) 1099-B PDFs to TXF files."""

import datetime
import re
import subprocess
import sys

if len(sys.argv) != 2:
    sys.exit(f'Usage: {sys.argv[0]} path-to-1099b-pdf')
text = subprocess.check_output(['pdftotext', '-raw', sys.argv[1], '-']).decode()

# Codes and structure are defined at
# https://www.taxdataexchange.org/txf/txf-spec.html

entry_codes = []
for (label, code) in (
        ('Short Term – Noncovered Securities', '711'),
        ('Long Term – Noncovered Securities', '713'),
    ):
    if label in text:
        entry_codes.append(code)
if len(entry_codes) == 0:
    sys.exit('Could not identify sales category')
if len(entry_codes) != 1:
    sys.exit(f'Found more than one sales category. This is not yet supported. {entry_codes}')
entry_code = entry_codes[0]

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
pattern = re.compile(
        r'^(?P<ref>\d+)\s+'
        '(?P<descr>(\w| )+)\s+'
        '(?P<cusip>\w+)\s+'
        '(?P<quantity>\d+\.\d+)\s+'
        '(?P<acquired>(\d+/\d+/\d+|\w+))\s+'
        '(?P<sold>\d+/\d+/\d+)\s+'
        '(?P<proceeds>\$[0-9,.]+)\s+'
        '(?P<cost>\$[0-9,.]+)\s', re.DOTALL|re.MULTILINE)

print('V042')
print('A mssb_1099b_to_txf')
print('D ' + datetime.datetime.now().strftime('%m/%d/%Y'))
print('^')
for match in pattern.finditer(text):
    print('TD')
    print('N' + entry_code)
    print('C1')
    print('L1')
    print('P' + match.group('ref') + ' ' + match.group('descr'))
    print('D' + match.group('acquired'))
    print('D' + match.group('sold'))
    # These have a leading dollar sign.
    print(match.group('cost'))
    print(match.group('proceeds'))
    print("$") # Wash sale. Leaving blank. They aren't handled here.
    print('^')
