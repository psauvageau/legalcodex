from __future__ import annotations
"""
Helper functions for XML parsing.
"""
from typing import Optional, Callable, TypeVar, Union, Generator
import xml.etree.ElementTree as ET
import logging

DBG_RAISE_ON_UNKNOWN_TAG :bool = False

TagParser  = Callable[[ET.Element],None]
TagParsers = dict[str,TagParser]

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




def get_attribute( element  : ET.Element,
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




def _warn_unknown_tag(element: ET.Element) -> None:
    _logger.warning('Ignoring unknown tag "%s": %s', element.tag, ET.tostring(element, encoding='unicode'))
    if DBG_RAISE_ON_UNKNOWN_TAG:
        raise ValueError(f'Unknown tag: "{element.tag}"')


def get_full_text(element: ET.Element,
                  tag_parsers: TagParsers,
                  default_parser: TagParser = _warn_unknown_tag
                  ) -> Generator[str, None, None]:
    """
    Recursively get the text of an element including its child elements
    """
    if element.text:
        yield element.text
    for child in element:
        yield from _get_full_text_recursive(child, tag_parsers, default_parser)



def _get_full_text_recursive(element: ET.Element,
                            tag_parsers: TagParsers,
                            default_parser: TagParser = _warn_unknown_tag
                            ) -> Generator[str, None, None]:
    """
    Recursively get the text of an element including its child elements
    """
    parser = tag_parsers.get(element.tag, default_parser)
    parser(element)

    if element.text:
        yield element.text
    for child in element:
        yield from _get_full_text_recursive(child, tag_parsers)
        if child.tail:
            yield child.tail
    if element.tail:
        yield element.tail





def clean_text(text: str) -> str:
    """
    Clean up text by removing newlines and extra spaces.
    """
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    return text.strip()

