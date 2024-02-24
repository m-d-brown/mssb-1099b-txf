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

if __name__ == '__main__':
    unittest.main()
