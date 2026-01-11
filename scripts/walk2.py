from __future__ import annotations
import sys
import os
import logging
import xml.etree.ElementTree as ET
from typing import Set, Generator, Optional, Callable, Iterable, Final
from abc import abstractmethod, ABC

_logger = logging.getLogger()

VERBOSE = True

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

    elem: ET.Element
    level:Final[int]

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

        if VERBOSE:
            if type(self) == Block:
                _logger.warning(f"TODO:  {self.tag}")
        #return f"{self.indent}<{self.tag}>"
        return ""

    def children(self)->Generator[Block,None,None]:
        try:
            for child in self._child_elements():
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

    def _child_elements(self)->Generator[ET.Element,None,None]:
        yield from self.elem

class _unsupported(Block):
    def __init__(self, elem: ET.Element, level:int)->None:
        raise UnsupportedBlockError(f"Block type not implemented: {elem.tag}")


class _LabelledBlock(Block):
    _DEFAULT_BLOCK = _unsupported
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
        self._text = list(_full_text(elem))

    def __str__(self) -> str:
        return self._formatted_text()


    def _formatted_text(self, max_column:int=_MAX_WIDTH)->str:
        indent = self.indent
        lines = _word_wrap(self._text, max_column - len(indent))
        if VERBOSE:
            lines = ["  " + l for l in lines ]
            lines = [f"<{self.tag}>"] + lines + [f"</{self.tag}>"]
        return "\n".join(f"{indent}{line}" for line in lines)


class Heading(_LabelledBlock):
    title: Optional[str]
    _BLOCKS = {
            "Label":        None,
            "TitleText":    None,
        }

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
        "Language":             None,
        "DefinedTermFr":        None,
        "DefinedTermEn":        None,
        "DefinitionRef":        None,
        "Emphasis":             None,
        "LeaderRightJustified": None,
        "Repealed":             None,
        "Sup":                  None,
        "XRefExternal":         None,
        "XRefInternal":         None,
    }


class _ContinuedBlock(Block):
    _DEFAULT_BLOCK = _unsupported
    _BLOCKS = {
          "Text": Text,
     }

class ContinuedClause(_ContinuedBlock): pass
class ContinuedDefinition(_ContinuedBlock): pass
class ContinuedParagraph(_ContinuedBlock): pass
class ContinuedSubparagraph(_ContinuedBlock): pass
class ContinuedSectionSubsection(_ContinuedBlock): pass
class ContinuedFormulaParagraph(_ContinuedBlock): pass
class ContinuedSubclause(_ContinuedBlock): pass

class FormulaTerm(_TextBlock):
    pass
class FormulaText(_TextBlock):
    pass
class FormulaConnector(_TextBlock):
    pass

class FormulaParagraph(_LabelledBlock):
    @staticmethod
    def _provision(elem: ET.Element, level:int)->Provision:
        return Provision(elem, level)

    @staticmethod
    def _formula_paragraph(elem: ET.Element, level:int)->Block:
        return FormulaParagraph(elem, level)

    @staticmethod
    def _formula_group(elem: ET.Element, level:int)->Block:
        return FormulaGroup(elem, level)

    _BLOCKS = {
        "ContinuedFormulaParagraph": ContinuedFormulaParagraph,
        "FormulaGroup": _formula_group,
        "FormulaParagraph": _formula_paragraph,
        "Label": None,
        "Provision": _provision,
        "Text": Text,
    }


class FormulaDefinition(Block):
    @staticmethod
    def _formula_group(elem: ET.Element, level:int)->Block:
        return FormulaGroup(elem, level)

    _DEFAULT_BLOCK = _unsupported
    _BLOCKS = {
        "ContinuedFormulaParagraph": ContinuedFormulaParagraph,
        "FormulaGroup": _formula_group,
        "FormulaParagraph": FormulaParagraph,
        "FormulaTerm": FormulaTerm,
        "Text": Text,
    }


class Formula(Block):
    _DEFAULT_BLOCK = _unsupported
    _BLOCKS = {
        "FormulaText": FormulaText,
    }


class FormulaGroup(Block):
   _DEFAULT_BLOCK = _unsupported
   _BLOCKS = {
       "Formula":                Formula,
       "FormulaConnector":       FormulaConnector,
       "FormulaDefinition":      FormulaDefinition,
   }






class ReadAsText(Block):
   _DEFAULT_BLOCK = _unsupported
   @staticmethod
   def _section(elem: ET.Element, level:int)->Section:
       return Section(elem, level)

   @staticmethod
   def _section_piece(elem: ET.Element, level:int)->SectionPiece:
         return SectionPiece(elem, level)

   _BLOCKS = {
        "FormulaDefinition": FormulaDefinition,
        "FormulaParagraph": FormulaParagraph,
        "Section": _section,
        "SectionPiece": _section_piece,
    }



class HistoricalNoteSubItem(_TextBlock):
    _BLOCKS = {
        "Sup":None,
    }

class HistoricalNote(_TextBlock):
    _BLOCKS = {
        "HistoricalNoteSubItem":HistoricalNoteSubItem,


    }

class Subsubclause(_LabelledBlock):
   _BLOCKS = {
        "Label": None,
        "ReadAsText": ReadAsText,
        "Text": Text,
    }

class MarginalNote(_TextBlock):
    _TEXT = True
    _BLOCKS = {
        "DefinedTermFr":None,
        "DefinitionRef":None,
        "HistoricalNote":HistoricalNote,
        "Language":None,
        "XRefExternal":None,
    }
    _DEFAULT_BLOCK = _unsupported


class Subclause(_LabelledBlock):
   _BLOCKS = {
    "ContinuedSubclause": ContinuedSubclause,
    "FormulaGroup": FormulaGroup,
    "Label": None,
    "ReadAsText": ReadAsText,
    "Subsubclause": Subsubclause,
    "Text": Text,
   }


class Clause(_LabelledBlock):
    _BLOCKS = {
        "ContinuedClause": ContinuedClause,
        "FormulaGroup": FormulaGroup,
        "Label": None,
        "ReadAsText": ReadAsText,
        "Subclause": Subclause,
        "Text": Text,
    }

class Subparagraph(_LabelledBlock):
   _BLOCKS = {
        "Clause":                   Clause,
        "ContinuedSubparagraph":    ContinuedSubparagraph,
        "FormulaGroup":             FormulaGroup,
        "Label":                    None,
        "ReadAsText":               ReadAsText,
        "Text":                     Text,
   }


class Paragraph(_LabelledBlock):
   _BLOCKS = {
        "ContinuedParagraph" : ContinuedParagraph,
        "FormulaDefinition" : FormulaDefinition,
        "FormulaGroup" : FormulaGroup,
        "Label" : None,
        "MarginalNote" : MarginalNote,
        "ReadAsText" : ReadAsText,
        "Subparagraph" : Subparagraph,
        "Text" : Text,
   }








class Provision(_LabelledBlock):

   @staticmethod
   def _provision(elem: ET.Element, level:int)->Block:
       return Provision(elem, level)

   _BLOCKS = {
        "Label": None,
        "Provision": _provision,
        "Text": Text,
   }


class Definition(Block):

    class TextDefinition(Block):
        _TEXT = True
        _DEFAULT_BLOCK = _unsupported

        _term: str
        _definition : str


        def __init__(self, elem: ET.Element, level:int)->None:
            super().__init__(elem, level)

            self._sub_elements = list(self.elem)
            assert len(self._sub_elements) > 0, "Definition missing sub-elements"
            assert self._sub_elements[0].tag == "DefinedTermFr", "Definition first sub-element is not DefinedTermFr"

            term_element = self._sub_elements[0]
            self._term = _get_text(term_element)

            definition :list[str] = [term_element.tail or ""]
            for sub_elem in self._sub_elements[1:]:
                definition.append(_get_text(sub_elem))

                tail = (sub_elem.tail or "").strip()
                if tail:
                    definition.append(tail)

            self._definition = " ".join(definition).strip()

        def _child_elements(self)->Generator[ET.Element,None,None]:
            yield from []

        def __str__(self) -> str:
            indent = self.indent
            return f'{indent}Definition: "{self._term}"\n' +\
                   "\n".join([f"{indent}  {line}"  for line in _word_wrap([self._definition])])




    _DEFAULT_BLOCK = _unsupported
    _BLOCKS = {
        "ContinuedDefinition": ContinuedDefinition,
        "FormulaDefinition": FormulaDefinition,
        "FormulaGroup": FormulaGroup,
        "Paragraph": Paragraph,
        "Provision": Provision,
        "Text": TextDefinition,
   }



class Subsection(_LabelledBlock):
    _BLOCKS = {
        "ContinuedSectionSubsection": ContinuedSectionSubsection,
        "Definition":                 Definition,
        "FormulaDefinition":          FormulaDefinition,
        "FormulaGroup":               FormulaGroup,
        "Label":                      None,
        "MarginalNote":               MarginalNote,
        "Paragraph":                  Paragraph,
        "Provision":                  Provision,
        "ReadAsText":                 ReadAsText,
        "Text":                       Text,
    }
    _DEFAULT_BLOCK = _unsupported



class Section(_LabelledBlock):

    _BLOCKS = {
        "AmendedText":                  Block,
        "ContinuedSectionSubsection":   ContinuedSectionSubsection,
        "Definition":                   Definition,
        "FormulaGroup":                 FormulaGroup,
        "HistoricalNote":               HistoricalNote,
        "Label":                        None,
        "MarginalNote":                 MarginalNote,
        "Paragraph":                    Paragraph,
        "ReadAsText":                   ReadAsText,
        "Subsection":                   Subsection,
        "Text":                         Text,
    }
    _DEFAULT_BLOCK = _unsupported



class SectionPiece(Block):
   _DEFAULT_BLOCK = _unsupported
   _BLOCKS = {
        "Clause":               Clause,
        "Definition":           Definition,
        "FormulaDefinition":    FormulaDefinition,
        "FormulaGroup":         FormulaGroup,
        "FormulaParagraph":     FormulaParagraph,
        "Paragraph":            Paragraph,
        "Provision":            Provision,
        "Subparagraph":         Subparagraph,
    }


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
    """
    Apply function f to block and all its children recursively.
    """
    f(block)
    for child in block.children():
        walk(child, f)



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

def _full_text(elem: ET.Element)->Iterable[str]:
    """
    Yield all text in an element, including tails.
    """
    if elem.text:
        yield elem.text
    for child in elem:
        yield from _full_text(child)
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


class UnsupportedBlockError(Exception):
    parent_element : Optional[ET.Element] = None

    @property
    def parent_content(self)->str:
        assert self.parent_element is not None
        return ET.tostring(self.parent_element, encoding="unicode")

def main()->None:
    _init_logger(VERBOSE)

    def print_block(block:Block)->None:
        try:
            s:str = str(block)
            if s:
                print(s)
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
