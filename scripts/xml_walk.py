from __future__ import annotations
import sys
import xml.etree.ElementTree as ET
from typing import Set, Generator, Optional, Callable
from abc import abstractmethod, ABC


class Block(ABC):


    @abstractmethod
    def lines(self)->Generator[str,None,None]:
        ...


WALK_FUNCTION = Callable[[ET.Element, int],Generator[Block,None,None]]

class TextBlock(Block):
    text: str
    def __init__(self,text:str )->None:
        self.text = text

    def lines(self)->Generator[str,None,None]:
        yield self.text


class LevelBlock(Block):
    label:Optional[str]
    level: int
    content : list[Block]

    def __init__(self, label:str, level:int)->None:
        self.label = label
        self.level = level
        self.content = []

    def lines(self)->Generator[str,None,None]:
        indent_str = "    " * self.level
        if self.label:
            yield f"{indent_str}{self.label}"
        for block in self.content:
            yield from block.lines()



def xml_walk(element: ET.Element, depth:int=0)->Generator[Block,None,None]:
    tag = element.tag

    walk_function = LEVEL_TAGS_TO_BLOCK.get(tag, text_walk)

    yield from walk_function(element, depth)



def text_walk(element: ET.Element, depth:int)->Generator[Block,None,None]:
    text = _clean_text(element.text)
    if text:
        yield TextBlock(text)

    for child in element:
        yield from xml_walk(child, depth+1)
        text = _clean_text(child.tail)
        if text:
            yield TextBlock(text)


def level_walk(element: ET.Element, depth:int)->Generator[Block,None,None]:

    label_element = element.find("Label")
    assert label_element is not None, f"Level element missing Label attribute: {ET.tostring(element, encoding='unicode')}"
    label = label_element.text.strip() if label_element.text else None

    block = LevelBlock(label, depth)

    block.content.extend(xml_walk(child, depth+1) for child in element)

    yield block





def _clean_text(text: Optional[str]) -> Optional[str]:
    """
    Clean up text by removing newlines and extra spaces.
    """
    if not text:
        return None

    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    return text.strip()



PATH = R"legalcodex\data\I-3.3.xml"

def main()->None:

    el = ET.parse(PATH).getroot()
    count = 0
    for block in xml_walk(el):
        for line in block.lines():
            print(line)
        count += 1
    print("Total blocks:", count)



#LEVEL_TAGS_TO_BLOCK : dict[str, WALK_FUNCTION] = {}


LEVEL_TAGS_TO_BLOCK : dict[str, WALK_FUNCTION] = {
    "Clause":               level_walk,
    "FormulaParagraph":     level_walk,
    "Heading":              level_walk,
    "Paragraph":            level_walk,
    "Provision":            level_walk,
    "ScheduleFormHeading":  level_walk,
    "Section":              level_walk,
    "Subclause":            level_walk,
    "Subparagraph":         level_walk,
    "Subsection":           level_walk,
    "Subsubclause":         level_walk,
}


if __name__ == "__main__":
    main()