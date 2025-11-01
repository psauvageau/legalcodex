"""
Handle loading of documents from file paths.

"""
import os
from typing import Callable, NewType, Dict


from .document import Document


Loader = Callable[[str], Document]


def load_document(document_path: str) -> Document:
    """
    Load and return the content of a document from the given file path.
    """
    ext = os.path.splitext(document_path)[1].lower()

    handlers: Dict[str, Loader] = {
        ".txt": load_text,
        ".epub": load_epub,
    }

    handler = handlers.get(ext, _default_handler)
    return handler(document_path)




def _default_handler(document_path: str) -> Document:
    raise ValueError(f"Unsupported document format: {document_path}")


def load_text(document_path: str) -> Document:
    """
    Load a text document from the given file path.
    """
    with open(document_path, "r", encoding="utf-8") as f:
        content = f.read()
    return Document(content)