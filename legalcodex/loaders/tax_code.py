"""
Load the tax code document as a XML file.
"""
from __future__ import annotations
import logging
import os
import copy
from abc import ABC, abstractmethod

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
        loader.body.dbg_print()
    return Document("")


class TaxCodeLoader:
    """
    """
    body : BodyBlock

    def __init__(self, file_name:str = FILE)->None:
        tree = ET.parse(file_name)
        xml_root = tree.getroot()

        #Find the <body> element and extract its text content
        body = xml_root.find('Body')
        if body is None:
            raise ValueError("No <Body> element found in the XML document.")
        self.body = BodyBlock(body)

INVALID_LEVEL = -1

class Block(ABC):
    level : int = INVALID_LEVEL

    @abstractmethod
    def to_lines(self, indent:int)->Generator[str,None,None]:
        pass

    @classmethod
    def get_indent_string(cls, indent: int) -> str:
        return "  " * indent

    def dbg_print(self)->None:
        print("----- DEBUG PRINT BLOCK -----")
        for line in self.to_lines(0):
            print(line)
        print("----- DEBUG PRINT BLOCK -----")

    def __str__(self) -> str:
        return f"B: {self.level} {str(type(self))}"




class CompositeBlock(Block):
    _content : List[Block]

    def __init__(self)->None:
        self._content = []

    def add(self, block : Block)->None:
        self._content.append(block)

    def to_lines(self, indent:int) -> Generator[str, None, None]:
        for block in self._content:
            yield from block.to_lines(indent + 1)


class BodyBlock(CompositeBlock):
    _heading_stack : List[CompositeBlock]

    def __init__(self, body: ET.Element)->None:
        super().__init__()
        assert body.tag == 'Body'
        self.level = 0
        self._heading_stack = [self]

        tags_parsers :xml.TagParsers = {
            "Heading": self._parse_heading,
            "Section": self._parse_section,
        }
        for element in body:
            xml.parse_element(element, tags_parsers)

    @property
    def current_level(self)->int:
        return len(self._heading_stack) - 1

    @property
    def current_block(self)->CompositeBlock:
        block = self._heading_stack[-1]
        assert block.level == len(self._heading_stack) - 1
        return block


    def _parse_heading(self, element : ET.Element )->None:
        heading = HeadingBlock(element)
        current_level = self.current_level

        if heading.level <= current_level:
            while self.current_level >= heading.level:
                self._heading_stack.pop()
        else:
            assert heading.level == current_level + 1, f"Invalid heading level: {heading.level} (current: {current_level})"
        self.current_block.add(heading)
        self._heading_stack.append(heading)


    def _parse_section(self, element : ET.Element )->None:
        section = SectionBlock(element, level=self.current_level + 1)
        self.current_block.add(section)


class HeadingBlock(CompositeBlock):
    label:str
    title:str

    def __init__(self, element: ET.Element )->None:
        super().__init__()
        assert element.tag == 'Heading'
        level:int = xml.get_attribute(          element, 'level', int)
        label:str = xml.get_sub_element_text(   element, 'Label', default='')
        title:str = xml.get_sub_element_text(   element, 'TitleText')
        self.level = level
        self.label = label
        self.title = title

    def to_lines(self, indent:int) -> Generator[str, None, None]:
        indent_str = self.get_indent_string(indent)
        if self.label:
            yield f"{indent_str}{self.label} : {self.title}"
        else:
            yield f"{indent_str}{self.title}"
        yield from super().to_lines(indent)


class SectionBlock(CompositeBlock):
    _VALID_TAGS = set(['Section', 'Subsection', 'Paragraph', 'Subparagraph', "Subclause", "Clause", "Provision","ReadAsText"])

    label : str


    def __init__(self, element: ET.Element, level:int)->None:
        super().__init__()
        self.label = ""
        assert element.tag in SectionBlock._VALID_TAGS

        def _null(elem: ET.Element) -> None:
            pass

        tags_parsers :xml.TagParsers = {
            "Section"      : self._parse_sub_bloc,
            "Label"        : self._parse_label,
            "Text"         : self._parse_text,
            "Subsection"   : self._parse_sub_bloc,
            "Paragraph"    : self._parse_sub_bloc,
            "Subparagraph" : self._parse_sub_bloc,
            "Clause"       : self._parse_sub_bloc,
            "Subclause"    : self._parse_sub_bloc,
            "Provision"    : self._parse_sub_bloc,
            "ReadAsText"   : self._parse_sub_bloc,


            "HistoricalNote": _null,
            "MarginalNote"  : _null,
            "Definition": _null,

            "ContinuedSectionSubsection": _null,
            "ContinuedSubparagraph": _null,
            "ContinuedParagraph": _null,
            "ContinuedClause": _null,

            "ContinuedSubclause": _null,

            "Subsubclause": _null,
            "SectionPiece": _null,

            "FormulaGroup": _null,
            "FormulaDefinition": _null,
            "FormulaParagraph": _null,
        }
        for child in element:
            xml.parse_element(child, tags_parsers)

    def _parse_label(self, element : ET.Element )->None:
        assert element.tag == 'Label'
        assert self.label == ''
        text = element.text
        assert text, "Empty Label element"
        self.label:str = xml.clean_text(text)

    def _parse_sub_bloc(self, element : ET.Element )->None:
        block = SectionBlock(element, level=self.level + 1)
        self._content.append(block)

    def _parse_text(self, element : ET.Element )->None:
        block = TextBlock(element)
        self._content.append(block)


    def to_lines(self, indent:int) -> Generator[str, None, None]:
        indent_str = self.get_indent_string(indent)
        if self.label:
            yield f"{indent_str}{self.label}"
        yield from super().to_lines(indent)





class TextBlock(Block):
    _text: str

    def __init__(self, element:ET.Element)->None:
        assert element.tag == 'Text'
        if element.text is None:
            self._text = ''
            _logger.warning("Empty text in Text element")
        else:
            self._text = xml.clean_text(element.text)

    def to_lines(self, indent:int)->Generator[str,None,None]:
        indent_str = self.get_indent_string(indent)

        for line in _dbg_text_to_80_columns(self._text):
            yield f"{indent_str}{line}"





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
