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
    if 0:
        loader.body.dbg_print()

    print("Saving:")
    with open(r".work\tax_code_dump.txt", "w", encoding="utf-8") as f:
        for line in loader.body.to_lines(0):
            f.write(line + "\n")

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
    _label:str
    _title:str

    def __init__(self, element: ET.Element )->None:
        super().__init__()
        assert element.tag == 'Heading'
        self.level = xml.get_attribute(          element, 'level', int)
        self._label = xml.get_sub_element_text(   element, 'Label', default='')
        self.title = xml.get_sub_element_text(   element, 'TitleText')

    def to_lines(self, indent:int) -> Generator[str, None, None]:
        indent_str = self.get_indent_string(indent)
        if self._label:
            yield f"{indent_str}{self._label} : {self.title}"
        else:
            yield f"{indent_str}{self.title}"
        yield from super().to_lines(indent)


class SectionBlock(CompositeBlock):
    #_VALID_TAGS = set(['Section', 'Subsection', 'Subsubclause','Paragraph', 'Subparagraph', "Subclause", "Clause", "Provision","ReadAsText","SectionPiece"])

    label : str
    _tag:str


    def __init__(self, element: ET.Element, level:int)->None:
        super().__init__()
        self.level = level
        self._tag = element.tag
        self.label = ""
        #assert element.tag in SectionBlock._VALID_TAGS
        self._marginal_notes: List[Block] = []

        def _null(elem: ET.Element) -> None:
            pass

        tags_parsers :xml.TagParsers = {
            "Section"                   : self._parse_sub_bloc,

            "Subsection"                : self._parse_sub_bloc,
            "Paragraph"                 : self._parse_sub_bloc,
            "Subparagraph"              : self._parse_sub_bloc,
            "Clause"                    : self._parse_sub_bloc,
            "Subclause"                 : self._parse_sub_bloc,
            "Subsubclause"              : self._parse_sub_bloc,
            "Provision"                 : self._parse_sub_bloc,
            "ReadAsText"                : self._parse_sub_bloc,
            "SectionPiece"              : self._parse_sub_bloc,
            "ContinuedSubclause"        : self._parse_sub_bloc,

            "ContinuedSectionSubsection": self._parse_sub_bloc,
            "ContinuedSubparagraph"     : self._parse_sub_bloc,
            "ContinuedParagraph"        : self._parse_sub_bloc,
            "ContinuedClause"           : self._parse_sub_bloc,

            "Label"                     : self._parse_label,
            "Text"                      : self._parse_text,
            "MarginalNote"              : self._parse_MarginalNote,

            "HistoricalNote": _null,

            "Definition": _null,

            "FormulaGroup": _null,
            "FormulaDefinition": _null,
            "FormulaParagraph": _null,
            "XRefExternal": _null,
            "DefinitionRef": _null,
            #"DefinedTermFr": _null,
            "Language": _null,
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

    def _parse_MarginalNote(self, element: ET.Element) -> None:
        assert element.tag == 'MarginalNote'

        block = TextBlock(element)
        self._marginal_notes.append(block)


    def to_lines(self, indent:int) -> Generator[str, None, None]:
        indent_str = self.get_indent_string(indent)
        if self.label:
            yield f"{indent_str}{self.label}"
        yield from super().to_lines(indent)



@dataclass
class Reference:
    type: str
    link: str
    text: str

    def __str__(self)->str:
        return f"{self.text} : {self.link} ({self.type})"

@dataclass
class Definition:
    term: str
    description: str


class TextBlock(Block):
    _text        : str
    _definition  : Definition
    _references  : List[Reference]
    _tag_parsers : xml.TagParsers
    _repealed    : Optional[str] = None
    _defined_terms: List[str]



    def __init__(self, element:ET.Element)->None:
        self._repealed = None
        self._references = []
        self._defined_terms = []

        null = lambda e: None

        self._tag_parsers : xml.TagParsers = {
            "Text":             null,
            "XRefExternal":     self._add_reference,

            "Repealed":         self._repealed_notice,
            "DefinedTermFr":    self._definition_notice,
            "DefinitionRef":    self._definition_notice,
            "XRefInternal":     self._add_reference,

            "Emphasis":         null,
            "Sup":              null,
            "Language":         null,

            "MarginalNote":     null,
            "HistoricalNote":   null,
        }

        text = ''.join(self._get_text_rec(element))
        if text:
            self._text = xml.clean_text(text)
        else:
            _logger.warning("Empty text in Text element")

    def _get_text_rec(self, element: ET.Element) -> Generator[str, None, None]:
        """
        Recursively get the text of an element including its child elements
        """

        def _null(elem: ET.Element) -> None:
            _logger.warning("Ignoring unknown tag in TextBlock: %s", elem.tag)


        self._tag_parsers.get(element.tag, _null)(element)

        if element.text:
            yield element.text
        for child in element:
            yield from self._get_text_rec(child)
            if child.tail:
                yield child.tail

    def to_lines(self, indent:int)->Generator[str,None,None]:
        indent_str = self.get_indent_string(indent)
        for line in _dbg_text_to_80_columns(self._text):
            yield f"{indent_str}{line}"

        if self._repealed:
            yield ""
            yield f"{indent_str}REPEALED: {self._repealed}"

        if self._references:
            yield ""
            yield f"{indent_str}References:"
            indent_str = self.get_indent_string(indent+1)
            for ref in self._references:
                yield indent_str + str(ref)

        if self._defined_terms:
            yield ""
            yield f"{indent_str}Defined Terms:"
            indent_str = self.get_indent_string(indent+1)
            for term in self._defined_terms:
                yield indent_str + term

    def _add_reference(self, element: ET.Element) -> None:

        type_:str = xml.get_attribute(element, 'reference-type', str, default="--")
        link = xml.get_attribute(element, 'link', str, default="--")
        text = element.text or ''
        reference = Reference(type=type_, link=link, text=xml.clean_text(text))
        self._references.append(reference)

    def _repealed_notice(self, element: ET.Element) -> None:
        assert self._repealed is None
        self._repealed = element.text or ''
        assert len(element) == 0, "Non-empty Repealed element"


    def _definition_notice(self, element: ET.Element) -> None:

        accepted = {"Emphasis",
                    }


        self._defined_terms.append(element.text or '--')
        if len(element) != 0:
            for child in element:
                if child.tag not in accepted:
                    _logger.warning('Non-empty DefinedTermFr element : "%s" - "%s"', child.tag, child.text or '--')






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
