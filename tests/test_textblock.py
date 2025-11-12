from __future__ import annotations
import unittest

import xml.etree.ElementTree as ET

from legalcodex.loaders.tax_code import TextBlock




class TestTextBlock(unittest.TestCase):



    def test_textblock_preserves_inner_tags(self)->None:

        xml_str = "<Text>begin<DefinedTermFr>defined</DefinedTermFr>end</Text>"

        el = ET.fromstring(xml_str)
        tb = TextBlock(el)

        t = el.text


        aa=0
        # The parsed text should include the inline tag serialization
        self.assertTrue( '<DefinedTermFr>' in tb._text)
        # And the inner text content should be present
        #assert 'defined' in tb._text
        #assert tb._text == "begin<DefinedTermFr>defined</DefinedTermFr>end"
