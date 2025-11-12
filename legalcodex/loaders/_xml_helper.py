from __future__ import annotations
"""
Helper functions for XML parsing.
"""
from typing import List, Optional, Callable, Dict, TypeVar, Union
import xml.etree.ElementTree as ET
import logging


TagParser  = Callable[[ET.Element],None]
TagParsers = Dict[str,TagParser]

_AttributeType = TypeVar('_AttributeType')
class _Undef:
    pass

_undef = _Undef()

_logger = logging.getLogger(__name__)



def parse_element(element    : ET.Element,
                  tag_parsers: TagParsers) -> None:
    """
    Generic XML element parser that dispatches to tag-specific parsers.
    """
    #_logger.debug("Parsing element: %s", element.tag)
    parse_function = tag_parsers.get(element.tag, None)
    if parse_function:
        parse_function(element)
    else:
        _logger.warning("Unknown tag: %s", element.tag)
        full_text = ET.tostring(element, encoding='unicode')
        _logger.warning('Full element text: "%s"', full_text)




def get_attribute( element : ET.Element,
                    name    : str,
                    type_   : Callable[[str],_AttributeType],
                    default : Union[_AttributeType, _Undef] = _undef
                    ) -> _AttributeType:
    """
    Get and convert an attribute from an XML element.
    Args:
        element: The XML element.
        name: The attribute name.
        type_: A callable to convert the attribute value.
        default: Optional default value if the attribute is missing.

        raise ValueError if the attribute is missing and no default is provided.
    """
    value :Optional[str] = element.get(name, None)
    if value is None:
        if default is not _undef:
            return default #type: ignore[return-value]
        raise ValueError(f'Element missing required attribute: "{name}" in "{element.tag}"')
    return type_(value)

def get_sub_element_text(  element: ET.Element,
                            name   : str,
                            default: Union[str, _Undef] = _undef
             ) -> str:
    """
    Get and convert a sub-element's text from an XML element.
    Args:
        element: The XML element.
        name: The sub-element name.
        default: Optional default value if the sub-element is missing.

            raise ValueError if the sub-element is missing and no default is provided.
    """
    sub_element :Optional[ET.Element] = element.find(name)
    if sub_element is None or sub_element.text is None:
        if default is _undef:
            raise ValueError(f'Element missing required sub-element: "{name}" in "{element.tag}"')
        return default #type: ignore[return-value]
    return clean_text(sub_element.text)

def clean_text(text: str) -> str:
    """
    Clean up text by removing newlines and extra spaces.
    """
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    return text.strip()
