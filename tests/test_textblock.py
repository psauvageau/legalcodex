from __future__ import annotations
import unittest

import xml.etree.ElementTree as ET

from legalcodex.loaders.tax_code import TextBlock, SimpleTextBlock

XML_TEXT = """
    <Text>
        begin
        <DefinedTermFr>
            defined_fr
        </DefinedTermFr>
        middle
            <Sup>
            sup
            <Language>
                lang
            </Language>
            </Sup>
        <DefinitionRef>
            defined_en
            <Text>
                defined_en_inner
            </Text>
        </DefinitionRef>
        end
    </Text>
"""

expected_text = "begin defined_fr middle sup lang defined_en defined_en_inner end"

class TestSimpleTextBlock(unittest.TestCase):
    def test_textblock_preserves_inner_tags(self)->None:

        element = ET.fromstring(XML_TEXT)
        text_block = SimpleTextBlock(element)
        text = text_block.text

        self.assertEqual(text, expected_text)
