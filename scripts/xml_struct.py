"""
Import an XML document.
Recursively walk the XML tree.

For each tag, build a set of sub-tags.

"""
from __future__ import annotations
import sys
import xml.etree.ElementTree as ET
from typing import Set, Generator


SUB_TAGS = set[str]


tags : dict[str, SUB_TAGS] = dict()







class Block:
    def parse()->None:
        pass



class SubBlock(Block):
    label: str
    children: list[Block]

    def __init__(self, element: ET.Element)->None:
        self.children = []

        if element.text:
            self.children.append(TextBlock(element.text.strip()))
            self.label = element.text.strip()

        for child in element:
            pass











class TextBlock(Block):
    text: str
    def __init__(self,text:str )->None:
        self.text = clean_text(text)

def get_blocs(element: ET.Element) -> Generator[Block, None, None]:

    if element.text:
        yield TextBlock(element.text)

    tag = element.tag
    block_type = TAG_TO_BLOCK.get(tag, TextBlock)
    yield block_type(element)


TAG_TO_BLOCK : dict[str, type[Block]] = {
    "Clause":               SubBlock,
    "FormulaParagraph":     SubBlock,
    "Heading":              SubBlock,
    "Paragraph":            SubBlock,
    "Provision":            SubBlock,
    "ScheduleFormHeading":  SubBlock,
    "Section":              SubBlock,
    "Subclause":            SubBlock,
    "Subparagraph":         SubBlock,
    "Subsection":           SubBlock,
    "Subsubclause":         SubBlock,
}





def walk(element: ET.Element)->None:
    tag = element.tag
    if tag not in tags:
        tags[tag] = set()
    sub_tags = tags[tag]
    for child in element:
        sub_tags.add(child.tag)
        walk(child)



def clean_text(text: str) -> str:
    """
    Clean up text by removing newlines and extra spaces.
    """
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    return text.strip()



def main()->None:
    file_name = r"legalcodex\data\I-3.3.xml"
    print("Loading:", file_name)
    tree = ET.parse(file_name)
    root = tree.getroot()
    walk(root)

    for tag, sub_tags in sorted(tags.items()):
        print(tag)
        for sub_tag in sorted(sub_tags):
            print(f"   {sub_tag}")
        print("")

    print("==============================")
    print()
    print("Tags with 'label' sub-tag:")
    for tag, sub_tags in sorted(tags.items()):
        if "Label" in sub_tags:
            print(tag)




if __name__ == "__main__":
    main()


