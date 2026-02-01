import unittest

import mssb_1099b_to_txf

class _MorganStanelyTxf(unittest.TestCase):
    """Unittests for the mssb_1099b_to_txf parser.
    """

    def testCategorizesLongTermGains(self):
        sample = """
Short Term – Noncovered Securities* (Short-term transactions for which basis is not reported to the IRS—Report on Form 8949, Part I, with Box B checked.)
...
Short Term – Noncovered Securities* (continued)
...
Total Short Term – Noncovered Securities $0.00 $0.00
...
Long Term – Noncovered Securities* (Long-term transactions for which basis is not reported to the IRS—Report on Form 8949, Part II, with Box E checked.)
...
Long Term – Noncovered Securities* (continued)
...
Total Long Term – Noncovered Securities $0.00 $0.00
...
        """
        section_matches = mssb_1099b_to_txf.parse_sections(sample)
        self.assertEqual(next(section_matches).group(1),
                         'Short Term – Noncovered Securities')
        self.assertEqual(next(section_matches).group(1),
                         'Long Term – Noncovered Securities')

    def testDescriptionIncludesShareQuantity(self):
        sample = """
Short Term – Noncovered Securities* (Short-term transactions for which basis is not reported to the IRS—Report on Form 8949, Part I, with Box B checked.)

XYZ INC CL C
00000K000

123.450000

01/01/23 02/02/23

$1,100.00

$1,000.00
Total Short Term – Noncovered Securities
        """
        section_matches = mssb_1099b_to_txf.parse_sections(sample)
        section_match = next(section_matches)
        entry_code = mssb_1099b_to_txf.CATEGORIES[section_match.group(1)]
        contents = section_match.group(2)
        serialized = mssb_1099b_to_txf.parse_and_serialize_rows(contents,
                                                             entry_code)
        self.assertEqual(serialized, """\
TD
N711
C1
L1
P123.45 sh. of XYZ INC CL C
D01/01/23
D02/02/23
$1,000.00
$1,100.00
$
^
""")

    def testFormatShareQuantity(self):
        self.assertEqual(mssb_1099b_to_txf.format_share_quantity('123'), '123',
                         'Whole numbers should be left as-is')
        self.assertEqual(mssb_1099b_to_txf.format_share_quantity('123.'),'123',
                         'Remove decimal if there is no fractional part')
        self.assertEqual(mssb_1099b_to_txf.format_share_quantity('123.00'), '123',
                         'Trim trailing zeros and decimal if the fractional part is zero')
        self.assertEqual(mssb_1099b_to_txf.format_share_quantity('45.6'), '45.6',
                         'Leave fractional part if there are no trailing zeros')
        self.assertEqual(mssb_1099b_to_txf.format_share_quantity('45.60'), '45.6',
                         'Trim trailing zeros but leave non-zero fractional part')
        self.assertEqual(mssb_1099b_to_txf.format_share_quantity('70'), '70',
                         'Do not trim trailing zeros for whole numbers')
        self.assertEqual(mssb_1099b_to_txf.format_share_quantity('70.0'), '70',
                         'Do not trim trailing zeros to the left of the decimal')

if __name__ == '__main__':
    unittest.main()
