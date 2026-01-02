"""
Load the tax code document as a XML file.
"""
from __future__ import annotations
import logging
import os
import copy
from abc import ABC, abstractmethod
import io

from typing import Optional, Callable, TypeVar, Union, Any, Generator, Sequence, BinaryIO
from dataclasses import dataclass

import xml.etree.ElementTree as ET

from legalcodex.loaders._xml_helper import TagParsers

from .document import Document
from . import _xml_helper as xml
from .._misc import dbg_text_to_80_columns

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


    if 1:
        file_name = r".work\tax_code_dump.txt"
        print("Saving:",file_name)
        with open(file_name, "w", encoding="utf-8") as f:
            for line in loader.body.to_lines(0):
                f.write(line + "\n")

    return Document("")


class TaxCodeLoader:
    """
    """
    body : BodyBlock

    def __init__(self, file_name:str = FILE)->None:
        with open(file_name, "rb") as f:
            tree = ET.parse(f)
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


    def _yield_sub_elements_text(self, name: str,
                                       blocks: Sequence[Block],
                                       indent:int) -> Generator[str,None,None]:
        if blocks:
            indent_str = self.get_indent_string(indent)
            #yield f"{indent_str}============================================"
            #yield ""
            yield f"{indent_str}{name}"
            for block in blocks:
                yield from block.to_lines(indent + 1)
            #yield f"{indent_str}============================================"




class CompositeBlock(Block):
    _content : list[Block]

    def __init__(self)->None:
        self._content = []

    def add(self, block : Block)->None:
        self._content.append(block)

    def to_lines(self, indent:int) -> Generator[str, None, None]:
        for block in self._content:
            yield from block.to_lines(indent + 1)


class BodyBlock(CompositeBlock):
    _heading_stack : list[CompositeBlock]

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
    label : str
    _tag:str

    _historical_notes : list[Block]
    _marginal_notes: list[Block]
    _definitions : list[Block]

    def __init__(self, element: ET.Element, level:int)->None:
        super().__init__()
        self.level = level
        self._tag = element.tag
        self.label = ""
        self._marginal_notes = []
        self._historical_notes = []
        self._definitions = []

        tags_parsers  = self.get_parsers()
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

        block = MarginalNoteBlock(element)
        self._marginal_notes.append(block)

    def _parse_historical_note(self, element: ET.Element) -> None:
        self._historical_notes.append(HistoricalNoteBlock(element))

    def _parse_definition(self, element: ET.Element) -> None:
        self._definitions.append(DefinitionBlock(element))

    def _parse_formula_group(self, element: ET.Element) -> None:
        self._content.append(FormulaBlock(element))


    def to_lines(self, indent:int) -> Generator[str, None, None]:
        indent_str = self.get_indent_string(indent)
        if self.label:
            yield f"{indent_str}{self.label}"

        yield from super().to_lines(indent)
        yield from self._yield_sub_elements_text("Marginal Notes",  self._marginal_notes,   indent)
        yield from self._yield_sub_elements_text("Historical Notes",self._historical_notes, indent)
        yield from self._yield_sub_elements_text("Definitions",     self._definitions,      indent)

    def get_parsers(self)->xml.TagParsers:


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

            "HistoricalNote"            : self._parse_historical_note,

            "Definition"                : self._parse_definition,

            "FormulaGroup"              : self._parse_formula_group,
            "FormulaDefinition": null_parser,
            "FormulaParagraph"          : self._parse_sub_bloc,
            "XRefExternal": null_parser,
            "DefinitionRef": null_parser,
            #"DefinedTermFr": null_parser,
            "Language": null_parser,
        }
        return tags_parsers





class SimpleTextBlock(Block):
    _tag                : str
    _text               : str
    _historical_notes   : list[HistoricalNoteBlock]

    def __init__(self, element:ET.Element)->None:
        self._text = ''
        self._tag  = element.tag
        self._historical_notes = []

        tag_parsers : xml.TagParsers = self.get_tag_parsers()
        text = ''.join(xml.get_full_text(element,
                                         tag_parsers))
        if text:
            self._text = xml.clean_text(text)
        else:
            _logger.warning("Empty text in Text element")

    def get_tag_parsers(self) -> xml.TagParsers:





        return {
            "Text":             null_parser,
            "Emphasis":         null_parser,
            "Sup":              null_parser,
            "Language":         null_parser,

            #"MarginalNote":     null_parser,
            "HistoricalNote":   self._parse_historical_note,
        }


    @property
    def text(self)->str:
        return self._text

    def to_lines(self, indent:int)->Generator[str,None,None]:
        indent_str = self.get_indent_string(indent)
        for line in dbg_text_to_80_columns(self._text):
            yield f"{indent_str}{line}"

        if self._historical_notes:
            yield ""
            yield f"{indent_str}Historical Notes:"
            for note in self._historical_notes:
                yield from note.to_lines(indent + 1)


    def _parse_historical_note(self, element: ET.Element) -> None:
        self._historical_notes.append(HistoricalNoteBlock(element))


class FormulaBlock(Block):
    _content :list[str]

    def __init__(self, element: ET.Element)->None:
        self._content = []
        self._content= list(xml.get_full_text(element, tag_parsers={}, default_parser=null_parser))

    def to_lines(self, indent:int) -> Generator[str,None,None]:
        indent_str = self.get_indent_string(indent)
        yield f"{indent_str}Formula:"
        for line in self._content:
            yield f"{indent_str}  {line}"






class HistoricalNoteBlock(SimpleTextBlock):
    def __init__(self, element: ET.Element)->None:
        assert element.tag == 'HistoricalNote'
        super().__init__(element)

    def get_tag_parsers(self) -> xml.TagParsers:
        return super().get_tag_parsers() | {
            "HistoricalNoteSubItem": null_parser,
        }



class TextBlock(SimpleTextBlock):
    #_definition  : list[Definition]
    _references  : list[Block]
    _repealed    : Optional[str] = None
    _defined_terms: list[Block]
    _marginal_notes : list[MarginalNoteBlock]

    def __init__(self, element:ET.Element)->None:
     #   self._definition    =  []
        self._repealed      = None
        self._references    = []
        self._defined_terms = []
        self._marginal_notes= []

        super().__init__(element)

    def get_tag_parsers(self) -> xml.TagParsers:

        tag_parser = super().get_tag_parsers()

        tag_parser.update({
            "XRefExternal":     self._add_reference,
            "XRefInternal":     self._add_reference,

            "Repealed":         self._repealed_notice,
            "DefinedTermFr":    self._definition_notice,
            "DefinitionRef":    self._definition_notice,
            "MarginalNote":     self._add_marginal_note,
        })
        return tag_parser



    def to_lines(self, indent:int)->Generator[str,None,None]:

        yield from super().to_lines(indent)

        indent_str:str = self.get_indent_string(indent)

        if self._repealed:
            yield ""
            yield f"{indent_str}REPEALED: {self._repealed}"

        self._yield_sub_elements_text("References",     self._references,     indent)
        self._yield_sub_elements_text("Defined Terms",  self._defined_terms,  indent)
        self._yield_sub_elements_text("Marginal Notes", self._marginal_notes, indent)




    def _add_reference(self, element: ET.Element) -> None:
        block: Block = ReferenceBlock(element)
        self._references.append(block)

    def _repealed_notice(self, element: ET.Element) -> None:
        assert self._repealed is None
        self._repealed = element.text or ''
        assert len(element) == 0, "Non-empty Repealed element"


    def _definition_notice(self, element: ET.Element) -> None:

        assert element.tag == 'DefinedTermFr' or element.tag == 'DefinitionRef'
        block = SimpleTextBlock(element)
        self._defined_terms.append(block)

    def _add_marginal_note(self, element: ET.Element) -> None:
        assert element.tag == 'MarginalNote'
        block = MarginalNoteBlock(element)
        self._marginal_notes.append(block)
        _logger.warning("Parsed MarginalNote: %s", block.text)


class MarginalNoteBlock(TextBlock):
    def __init__(self, element: ET.Element)->None:
        assert element.tag == 'MarginalNote'
        super().__init__(element)


class ReferenceBlock(SimpleTextBlock):
    _type: str
    _link: str

    def __init__(self, element: ET.Element)->None:
        assert element.tag == 'XRefExternal' or element.tag == 'XRefInternal'

        self._type =  xml.get_attribute(element, 'reference-type', str, default="--")
        self._link = xml.get_attribute(element, 'link', str, default="")
        super().__init__(element)

    def to_lines(self, indent: int) -> Generator[str, None, None]:
        yield "Reference: {self._type} : {self._link}"
        yield from super().to_lines(indent)


class DefinitionBlock(Block):
    _text:str
    _terms : list[str]

    def __init__(self, element: ET.Element)->None:


        assert element.tag == 'Definition'
        assert not bool(element.text.strip()), f'"Definition element should not have direct text "{element.text}"'
        self._terms  = []

        self._text = " ".join(xml.get_full_text(element,tag_parsers={}, default_parser=null_parser))

        #tag_parsers : xml.TagParsers = {
        #    "Text":                 self._parse_text,
#
        #    "Paragraph":            null_parser,
        #    "ContinuedDefinition":  null_parser,
        #    "FormulaGroup":         null_parser,
        #    "FormulaDefinition":    null_parser,
        #    "Provision":            null_parser,
        #}
#
        #for child in element:
        #    xml.parse_element(child, tag_parsers)

    def get_parsers(self) -> dict[str, Callable[[Element], None]]:
        parent =  super().get_parsers()

        tag_parsers : xml.TagParsers = {
            "Text":                 self._parse_text,
#
            #"Paragraph":            null_parser,
            #"ContinuedDefinition":  null_parser,
            #"FormulaGroup":         null_parser,
            #"FormulaDefinition":    null_parser,
            #"Provision":            null_parser,
        }
        return parent | tag_parsers


    def _parse_text(self, element: ET.Element) -> None:
        assert element.tag == 'Text'

        first_child : Optional[ET.Element] = element[0]
        assert first_child is not None
        assert first_child.tag == 'DefinedTermFr', "Expected DefinedTermFr as first child of Definition Text"

        for child in element:
            if child.tag == 'DefinedTermFr':
                term = xml.clean_text(child.text or '')
                if term not in self._terms:
                    self._terms.append(term)
            elif child.tag == 'Repealed':
                pass #TODO
            else:
                accepted = {"DefinedTermEn","Language","Sup", "DefinitionRef","XRefExternal" }
                if child.tag not in accepted:
                    _logger.warning("Unexpected tag in Definition Text: %s", child.tag)

    def to_lines(self, indent:int) -> Generator[str, None, None]:
        indent_str = self.get_indent_string(indent)
        #yield f"{indent_str}Definition Block TODO"
        #assert self._terms

        #line =  f"{indent_str}Definitions: {', '.join(self._terms)}"
#
        #if len(self._terms) > 1:
        #    _logger.warning("Definition with multiple terms:")
        #    for term in self._terms:
        #        _logger.warning(" - %s", term)
        #    print()
#
        #yield line
        yield f"{indent_str}Definition: {self._text}"

def null_parser(element: ET.Element) -> None:
    pass