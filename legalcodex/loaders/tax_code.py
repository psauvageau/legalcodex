"""
Load the tax code document as a XML file.
"""
from __future__ import annotations
import logging
import os
import copy

from typing import List, Optional   , Dict, Callable, TypeVar, Union, Any
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
    loader.root.dbg_print()
    return Document("")

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

    def dbg_print(self, indent:int=0)->None:
        assert indent ==self.level
        print("  " * indent + str(self))
        for sub in self._sub_blocks:
            sub.dbg_print(indent + 1)


class RootBlock(Block):
    def __init__(self)->None:
        super().__init__("", "", 0)


class TaxCodeLoader:
    """
    """
    _block_stack    : List[Block]


    def __init__(self, file_name:str = FILE)->None:
        self._block_stack = [RootBlock()]

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
    def root(self)->Block:
        root = self._block_stack[0]
        assert isinstance(root, RootBlock)
        return root

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

def heading_to_block(element : ET.Element )->Block:
    """
    Parse a Heading XML element into a Block instance.
    """
    assert element.tag == 'Heading'

    level:int = xml.get_attribute(element, 'level', int)
    label:str = xml.get_sub_element_text(element, 'Label', default='')
    title:str = xml.get_sub_element_text(element, 'TitleText')
    return Block(label, title, level)



