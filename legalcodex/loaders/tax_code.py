"""
Load the tax code document as a XML file.
"""
from __future__ import annotations
import logging
import os
import copy

from typing import List, Optional   , Dict, Callable, TypeVar, Union, Any, Generator
from dataclasses import dataclass

import xml.etree.ElementTree as ET

from .document import Document
from . import _xml_helper as xml

#import parse_element, get_attribute, get_sub_element_text, TagParsers

_logger = logging.getLogger(__name__)

FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "I-3.3.xml"))
assert os.path.isfile(FILE), f"Tax code file not found: {FILE}"



def load_tax_code(file_name: str = FILE) -> Document:
    """
    Load the tax code document from the given XML file path.

    Args:
        path (str): The file path to the XML document.

    Returns:
        Document: The loaded tax code document.
    """
    # Parse the XML file
    loader = TaxCodeLoader(file_name=file_name)
    if 1:
        loader.root.dbg_print()
    return Document("")


class TaxCodeLoader:
    """
    """
    _block_stack    : List[Block]
    root : Block

    def __init__(self, file_name:str = FILE)->None:
        self.root = RootBlock()
        self._block_stack = [self.root]
        tree = ET.parse(file_name)
        root = tree.getroot()

        #Find the <body> element and extract its text content
        body = root.find('Body')
        if body is None:
            raise ValueError("No <Body> element found in the XML document.")

        tags_parsers :xml.TagParsers = {
            "Heading": self._parse_heading,
            "Section": self._parse_section,
        }
        for element in body:
            xml.parse_element(element, tags_parsers)

    @property
    def current_block(self)->Block:
        block = self._block_stack[-1]
        assert block.level == len(self._block_stack) - 1
        return block

    @property
    def current_level(self)->int:
        return len(self._block_stack) - 1


    def _parse_heading(self, element : ET.Element )->None:
        assert element.tag == 'Heading'

        block : Block = heading_to_block(element)
        _logger.debug("Parsed heading: %s", block)

        current_level = self.current_level
        if block.level == current_level:
            self._block_stack.pop()
            self._block_stack[-1].add_child(block)
            self._block_stack.append(block)
        elif block.level == current_level + 1:
            self.current_block.add_child(block)
            self._block_stack.append(block)
        elif block.level < current_level:
            while self.current_level >= block.level:
                self._block_stack.pop()
            self.current_block.add_child(block)
            self._block_stack.append(block)
        else:
            raise ValueError(f"Invalid heading level: {block.level} (current: {current_level})")

    def _parse_section(self, element : ET.Element )->None:
        assert element.tag == 'Section'
        block = SectionBlock(level=self.current_level + 1)
        block.parse(element)
        self.current_block.add_child(block)

class Block:
    level       :int
    label       :str
    content     :str
    _sub_blocks :List[Block]

    def __init__(self, label:str, content:str, level:int)->None:
        self._sub_blocks = []
        self.label = label
        self.content = content
        self.level = level

    def add_child(self, block:Block)->None:
        self._sub_blocks.append(block)

    def __str__(self)->str:
        return f'Block(level={self.level:<2}, "{self.label:<20}" : {self.content}'

    def dbg_print(self, labels:str = "", indent:int=0)->None:
        assert indent ==self.level

        label = self.to_label(labels=labels)
        print("*", "  " * indent + label)

        for line in self.to_lines(indent):
            print(line)

        for sub in self._sub_blocks:
            sub.dbg_print(label, indent + 1)
        print()

    def to_label(self, labels:str)->str:
        if self.label:
            return f"{labels} {self.label}"
        return labels

    def to_lines(self, indent:int)->Generator[str,None,None]:
        i = "  " * (indent + 1)
        if self.content:
            for line in _dbg_text_to_80_columns(self.content):
                yield f'{i}{line}'

class RootBlock(Block):
    def __init__(self)->None:
        super().__init__("", "", 0)

class HeadingBlock(Block):
    pass

class SectionBlock(Block):
    _VALID_TAGS = set(['Section', 'Subsection', 'Paragraph', 'Subparagraph', "Subclause", "Clause", "Provision","ReadAsText"])

    def __init__(self, level:int)->None:
        super().__init__(label="", content="", level=level)

    def parse(self, element : ET.Element )->None:
        assert element.tag in SectionBlock._VALID_TAGS

        def _null(elem: ET.Element) -> None:
            pass

        tags_parsers :xml.TagParsers = {
            "Label"        : self._parse_label,
            "Text"         : self._parse_text,
            "Subsection"   : self._parse_sub_bloc,
            "Paragraph"    : self._parse_sub_bloc,
            "Subparagraph" : self._parse_sub_bloc,
            "Clause"       : self._parse_sub_bloc,
            "Subclause"    : self._parse_sub_bloc,
            "Provision"    : self._parse_sub_bloc,
            "ReadAsText"  : self._parse_sub_bloc,


            "HistoricalNote": _null,
            "MarginalNote"  : _null,
            "Definition": _null,
            "FormulaGroup": _null,
            "ContinuedSectionSubsection": _null,
            "ContinuedSubparagraph": _null,
            "ContinuedParagraph": _null,



            "FormulaDefinition": _null,
        }
        for child in element:
            xml.parse_element(child, tags_parsers)

    def _parse_label(self, element : ET.Element )->None:
        assert element.tag == 'Label'
        assert self.label == ''
        self.label:str = xml.clean_text(element.text)

    def _parse_sub_bloc(self, element : ET.Element )->None:
        block = SectionBlock(level=self.level + 1)
        block.parse(element)

        self.add_child(block)

    def _parse_text(self, element : ET.Element )->None:
        assert element.tag == 'Text'
        assert self.content == ''

        if element.text is None:
            self.content = ''
            _logger.warning("Empty text in Text element")
        else:
            self.content = xml.clean_text(element.text)







def heading_to_block(element : ET.Element )->Block:
    """
    Parse a Heading XML element into a Block instance.
    """
    assert element.tag == 'Heading'

    level:int = xml.get_attribute(element, 'level', int)
    label:str = xml.get_sub_element_text(element, 'Label', default='')
    title:str = xml.get_sub_element_text(element, 'TitleText')
    return HeadingBlock(label, title, level)





def _dbg_text_to_80_columns(text:str)->Generator[str,None,None]:
    """
    Split text into lines of max 80 columns for debugging output.
    """
    words = text.split()
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= 80:
            if current_line:
                current_line += " "
            current_line += word
        else:
            yield current_line
            current_line = word
    if current_line:
        yield current_line
