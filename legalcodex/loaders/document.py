"""
Define document format
"""



class Document:
    """
    Represents a loaded document with its content.
    """

    def __init__(self, content: str) -> None:
        self._content = content


    @property
    def content(self) -> str:
        """
        Get the content of the document.
        """
        return self._content