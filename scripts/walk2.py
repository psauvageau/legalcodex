from __future__ import annotations
import sys
import os
import logging
import xml.etree.ElementTree as ET
from typing import Set, Generator, Optional, Callable, Iterable
from abc import abstractmethod, ABC

_logger = logging.getLogger()

VERBOSE = False

BLOCK_CTOR = Callable[[ET.Element, int],"Block"]


#=========================================================================================

class Block(ABC):
    """
    Base class for all blocks in the XML structure.
    """
    #Class-level mappings of XML tags to Block constructors.
    # Not supposed to change at run-time
    _BLOCKS        : dict[str, Optional[BLOCK_CTOR]] = {}
    _DEFAULT_BLOCK : Optional[BLOCK_CTOR] = None
    _TEXT          : bool = False

    def __init__(self, elem:ET.Element, level:int)->None:
        self.elem = elem
        self.level = level

        if not self._TEXT:
            text = _get_text(elem)
            if text:
                raise ValueError(f"Unexpected text in element <{elem.tag}>: Block Type {type(self).__name__} '{text}'")

    @property
    def tag(self)->str:
        return self.elem.tag

    @property
    def indent(self)->str:
        return "  " * self.level

    def __str__(self) -> str:
        return f"{self.indent}<{self.tag}>"

    def children(self)->Generator[Block,None,None]:
        try:
            for child in self.elem:
                sub_block = self._get_block(child)
                if sub_block:
                    yield sub_block
        except UnsupportedBlockError as e:
            e.parent_element = self.elem
            raise e

    def _get_block(self, elem: ET.Element)->Optional[Block]:
        block_constructor = self._BLOCKS.get(elem.tag, self._DEFAULT_BLOCK)
        if block_constructor is None:
            return None
        return block_constructor(elem, self.level+1)



class _unsupported(Block):
    def __init__(self, elem: ET.Element, level:int)->None:
        raise UnsupportedBlockError(f"Block type not implemented: {elem.tag}")


class _LabelledBlock(Block):
    _BLOCKS = {
        "Label": None,
    }
    label: Optional[str]

    def __init__(self, elem: ET.Element, level:int)->None:
        super().__init__(elem, level)
        self.label = None

        for child in self.elem:
            if child.tag == "Label":
                assert self.label is None, "Multiple Label elements in LabelledBlock"
                self.label = child.text

    def __str__(self) -> str:
        if self.label:
            return f"{self.indent}({self.label}) <{self.tag}>"
        else:
            return f"{self.indent}<{self.tag}>"

class _TextBlock(Block):
    _TEXT = True
    _text : list[str]

    _MAX_WIDTH = 80

    _DEFAULT_BLOCK = _unsupported

    def __init__(self, elem: ET.Element, level:int)->None:
        super().__init__(elem, level)
        self._text = list(_full_test(elem))

    def __str__(self) -> str:
        return self._formated_text()


    def _formated_text(self, max_column:int=_MAX_WIDTH)->str:
        indent_str = "    " * self.level
        lines = _word_wrap(self._text, max_column - len(indent_str))
        return "\n".join(f"{indent_str}{line}" for line in lines)





class Heading(_LabelledBlock):
    title: Optional[str]
    _BLOCKS = _LabelledBlock._BLOCKS.copy()
    _BLOCKS.update({
            "TitleText":    None,
        })

    _DEFAULT_BLOCK = _unsupported

    def __init__(self, elem: ET.Element, level:int)->None:
        super().__init__(elem, level)
        self.title = None

        for child in self.elem:
            if child.tag == "TitleText":
                assert self.title is None, "Multiple TitleText in Heading"
                self.title = child.text


    def _get_block(self, elem: ET.Element)->Optional[Block]:
        return None

    def __str__(self) -> str:
        s:str = ":".join(  p for p in [self.label, self.title]  if p )
        assert s
        return f"{self.indent}{s} <{self.tag}>"




class Text(_TextBlock):
    _BLOCKS = {
        "DefinedTermEn":        None,
        "DefinedTermFr":        None,
        "DefinitionRef":        None,
        "Emphasis":             None,
        "Language":             None,
        "LeaderRightJustified": None,
        "Repealed":             None,
        "Sup":                  None,
        "XRefExternal":         None,
        "XRefInternal":         None,
    }



class HistoricalNote(_TextBlock):
    _BLOCKS = {
        "HistoricalNoteSubItem":None,
    }






class MarginalNote(Block):
    _TEXT = True
    _BLOCKS = {
        "DefinedTermFr":None,
        "DefinitionRef":None,
        "HistoricalNote":HistoricalNote,
        "Language":None,
        "XRefExternal":None,
    }
    _DEFAULT_BLOCK = _unsupported




class Subparagraph(_LabelledBlock):
   _BLOCKS = {
        "Clause":                   Block,
        "ContinuedSubparagraph":    Block,
        "FormulaGroup":             Block,
        "Label":                    None,
        "ReadAsText":               Block,
        "Text":                     Text,
   }


class Paragraph(_LabelledBlock):
   _BLOCKS = {
        "ContinuedParagraph" : Block,
        "FormulaDefinition" : Block,
        "FormulaGroup" : Block,
        "Label" : None,
        "MarginalNote" : MarginalNote,
        "ReadAsText" : Block,
        "Subparagraph" : Subparagraph,
        "Text" : Text,
   }







class Subsection(_LabelledBlock):
    _BLOCKS = {
        "ContinuedSectionSubsection": Block,
        "Definition":                 Block,
        "FormulaDefinition":          Block,
        "FormulaGroup":               Block,
        "Label":                      None,
        "MarginalNote":               MarginalNote,
        "Paragraph":                  Paragraph,
        "Provision":                  Block,
        "ReadAsText":                 Block,
        "Text":                       Text,
    }
    _DEFAULT_BLOCK = _unsupported



class Section(_LabelledBlock):

    _BLOCKS = {
        "AmendedText":                  Block,
        "ContinuedSectionSubsection":   Block,
        "Definition":                   Block,
        "FormulaGroup":                 Block,
        "HistoricalNote":               HistoricalNote,
        "Label":                        None,
        "MarginalNote":                 MarginalNote,
        "Paragraph":                    Paragraph,
        "ReadAsText":                   Block,
        "Subsection":                   Subsection,
        "Text":                         Text,
    }
    _DEFAULT_BLOCK = _unsupported


class Body(Block):
    _BLOCKS = {
        "Heading":      Heading,
        "Section":      Section,
    }
    _DEFAULT_BLOCK = _unsupported

    def _get_block(self, elem: ET.Element)->Optional[Block]:
        block_constructor = self._BLOCKS.get(elem.tag, None)
        if block_constructor is None:
            return None
        return block_constructor(elem, self.level+1)


class Statute(Block):

    _BLOCKS = {
        "Body":             Body,
        "Identification":   None,
        "RecentAmendments": None,
        "Schedule":         None,
    }
    _DEFAULT_BLOCK = _unsupported

    def __init__(self, elem:ET.Element, level:int)->None:
        assert elem.tag == "Statute"
        super().__init__(elem, level)


#=========================================================================================


def walk(block:Block,
         f:Callable[[Block], None])->None:
    f(block)
    for child in block.children():
        walk(child, f)





class UnsupportedBlockError(Exception):
    parent_element : Optional[ET.Element] = None

    @property
    def parent_content(self)->str:
        assert self.parent_element is not None
        return ET.tostring(self.parent_element, encoding="unicode")


def _get_text(elem: ET.Element)->str:
    """
    Check that an element has no text or tail text.
    """
    text = []



    if elem.text:
        text.append(elem.text)


    for child in elem:
        if child.tail:
            text.append(child.tail)
    return " ".join(text).strip()



def _full_test(elem: ET.Element)->Iterable[str]:
    """
    Yield all text in an element, including tails.
    """
    if elem.text:
        yield elem.text
    for child in elem:
        yield from _full_test(child)
        if child.tail:
            yield child.tail




def _word_wrap(text:Iterable[str], max_widht:int=80)->Iterable[str]:
    """
    Simple word-wrapping for an iterable of text strings.
    Yield lines of text no longer than max_width.
    """
    current_line = ""
    for segment in text:
        words = segment.split()
        for word in words:
            if len(current_line) + 1 + len(word) <= max_widht:
                if current_line:
                    current_line += " " + word
                else:
                    current_line += word
            else:
                yield current_line
                current_line = word
    if current_line:
        yield current_line







def _init_logger(verbose:bool)->None:
    ENCODING = "utf-8"
    sys.stdout.reconfigure(encoding=ENCODING) #type:ignore
    #sys.stderr.reconfigure(encoding=ENCODING)


    full_format = "%(levelname)-8s : %(message)s"
    if verbose:
        level = logging.DEBUG
        info_format = full_format
    else:
        level = logging.INFO
        info_format = "%(message)s"

    LEVEL_FORMATS : dict[int, str] = {
        logging.CRITICAL: full_format,
        logging.ERROR:    full_format,
        logging.WARNING:  full_format,
        logging.INFO:     info_format,
        logging.DEBUG:    full_format,
    }
    logging.basicConfig(level=level , format=full_format)


    # Set up logging with different format for INFO level
    class InfoFormatter(logging.Formatter):
        def format(self, record:logging.LogRecord)->str:
            fmt = self._style._fmt
            self._style._fmt = LEVEL_FORMATS[record.levelno]
            try:
                log_message = super().format(record)
                return log_message

                #encoding="utf-8"
                #return log_message.encode(encoding, errors='replace').decode(encoding)
            finally:
                self._style._fmt = fmt

    for handler in logging.root.handlers:
        handler.setFormatter(InfoFormatter(full_format))

def main()->None:
    _init_logger(VERBOSE)

    def print_block(block:Block)->None:
        try:
            print(block)
        except UnicodeEncodeError as err    :
            _logger.error(f"Error in  {block.tag} at level {block.level}")
            _logger.error(str(err))

    PATH = os.path.join(os.path.dirname(__file__), "..", r"legalcodex\data\I-3.3.xml")

    root :ET.Element = ET.parse(PATH).getroot()
    try:
        statute = Statute(root, 0)
        walk(statute, print_block)
    except UnsupportedBlockError as e:
        _logger.error(e)
        _logger.error(e.parent_content)
        _logger.exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
