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
        entry_code = mssb_1099b_to_txf.categories[section_match.group(1)]
        contents = section_match.group(2)
        serialized = mssb_1099b_to_txf.parseAndSerializeRows(contents,
                                                             entry_code)
        self.assertEqual(serialized, """\
TD
N711
C1
L1
P123.450000 sh. of XYZ INC CL C
D01/01/23
D02/02/23
$1,000.00
$1,100.00
$
^
""")

if __name__ == '__main__':
    unittest.main()
