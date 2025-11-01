"""
Load the tax code document as a XML file.
"""
from __future__ import annotations
import logging
import os

from typing import List
from dataclasses import dataclass

import xml.etree.ElementTree as ET

from .document import Document


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
    return Document("")


@dataclass(frozen=True)
class Heading:
    _level : int
    _label  : str
    _title : str

    @classmethod
    def parse(cls, element : ET.Element )->Heading:
        assert element.tag == 'Heading'

        level = int(element.get('level', '-1'))

        label_element = element.find('Label')
        if label_element is None:
            label = ''
        else:
            label = label_element.text.strip()

        title = element.find('TitleText').text.strip()

        return cls(level, label, title)

    def __str__(self)->str:

        indent = "  " * (self._level - 1)

        return f'{self._level:<2} {indent} "{self._label:<10}" "{self._title}"'


@dataclass(frozen=True)
class Section:
    _headings : List[Heading]
    _text     : List[str]



class TaxCodeLoader:
    """
    """
    _current_heading : List[str]
    _sections : List[Section]

    def __init__(self, file_name:str = FILE)->None:
        self._current_heading = []
        self._sections = []

        tree = ET.parse(file_name)
        root = tree.getroot()

        #Find the <body> element and extract its text content
        body = root.find('Body')
        if body is None:
            raise ValueError("No <Body> element found in the XML document.")


        tags = {
            "Heading": self._parse_heading,
            "Section": self._parse_section,
        }

        #iter over the direct children of body
        _logger.debug("Processing %d body elements", len(body))
        for elem in body:
            parse_function = tags.get(elem.tag, None)
            if parse_function:
                parse_function(elem)
            else:
                _logger.warning("Unknown tag: %s", elem.tag)

    def _parse_heading(self, element : ET.Element )->None:
        assert element.tag == 'Heading'

        heading = Heading.parse(element)



        _logger.debug(heading)


    def _parse_section(self, element : ET.Element )->None:
        assert element.tag == 'Section'














