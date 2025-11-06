#type:ignore
import os
from typing import Generator

import logging

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
    from legalcodex.loaders.tax_code import load_tax_code
    load_tax_code()


if __name__ == "__main__":
    _init_logging()
    tax_code()