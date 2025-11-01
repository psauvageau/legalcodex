"""
Load an E-Pub document
"""

import logging
import zipfile
 import xml.etree.ElementTree as ET


from .document import Document


_logger = logging.getLogger()





def load_epub(document_path: str) -> Document:
    """
    Load an EPUB document from the given file path.
    """
    from dbg import load_epub_text

    texts = []
    for text in load_epub_text(document_path):
        texts.append(text)

    content = "\n".join(texts)
    return Document(content)


class EPubAccessor:
    """
    Hold the zip file and provide access to its contents.
    """
    def __init__(self, epub_path: str) -> None:
        self._zip = zipfile.ZipFile(epub_path, 'r')
        self._files = list(self._zip.infolist())

        for file in self._files:
            _logger.debug("Found file in EPUB: %s", file.filename)

        toc_files = [f for f in self._files if _get_extension(f.filename) == '.ncx']
        assert len(toc_files) == 1, "Expected exactly one TOC file (.ncx)"
        self._toc_file = toc_files[0]

        with self._zip.open(toc_files[0]) as f:
            self._






def parse_toc(xml_document:str) -> ET.Element:











def _get_extension(file_path: str)->str:
    """
    Get the file extension in lowercase.
    """
    _, ext = os.path.splitext(file_path)
    return ext.lower()