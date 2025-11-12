#type:ignore
import os
from typing import Generator

import logging

import xml.etree.ElementTree as ET

#from ebooklib import epub
#import ebooklib




#from legalcodex.embedding import embed_document



_logger = logging.getLogger()

def _init_logging():

    #level = logging.DEBUG
    level = logging.INFO


    format = "%(levelname)-8s %(module)-15s : %(message)s"
    logging.basicConfig(level=level, format=format)


def tax_code()->None:
    from legalcodex.loaders.tax_code import load_tax_code, TextBlock
    load_tax_code()



def test_text():
    def to_text_recursive(element: ET.Element)->Generator[str,None,None]:
        if element.text:
            yield element.text
        for child in element:
            yield from to_text_recursive(child)
            if child.tail:
                yield child.tail

    el = ET.fromstring("<Text> A <DefinedTermFr> B <b> C </b> D <i> E </i> F </DefinedTermFr> G </Text>")
    parts = list(to_text_recursive(el))
    for p in parts:
        print(">>", p)










if __name__ == "__main__":
    _init_logging()
    tax_code()
    #test_text(  )