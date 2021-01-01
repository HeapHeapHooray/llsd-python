# This code can be found at: https://github.com/HeapHeapHooray/llsd-python

# This code is based on the answer by Duncan Harris for the
# following stackoverflow question:
# https://stackoverflow.com/questions/6949395/is-there-a-way-to-get-a-line-number-from-an-elementtree-element


import sys

sys.modules['_elementtree'] = None
import xml.etree.ElementTree as ElementTree

# Here we create a specialized XML parser that adds
# line and column position data to the elements of the XML
# I guess you can call it a hack.
class SpecializedParser(ElementTree.XMLParser):
    def _start(self, *args, **kwargs):
        element = super(self.__class__, self)._start(*args, **kwargs)
        element.start_line_number = self.parser.CurrentLineNumber
        element.start_column_number = self.parser.CurrentColumnNumber
        element.start_byte_index = self.parser.CurrentByteIndex
        return element

    def _end(self, *args, **kwargs):
        element = super(self.__class__, self)._end(*args, **kwargs)
        element.end_line_number = self.parser.CurrentLineNumber
        element.end_column_number = self.parser.CurrentColumnNumber
        element.end_byte_index = self.parser.CurrentByteIndex
        return element

from typing import Tuple,List

class Element:
    def __init__(self,element: ElementTree.Element):
        self._element = element
    def get_children(self) -> List["Element"]:
        return [Element(element) for element in list(self._element)]
    def get_text(self) -> str:
        return self._element.text if self._element.text != None else ""
    def get_tag(self) -> str:
        return self._element.tag
    def get_attributes(self) -> dict:
        return dict(self._element.attrib)
    def get_start_position(self) -> Tuple[int]:
        return (self._element.start_line_number,
                self._element.start_column_number+1)
    def get_end_position(self) -> Tuple[int]:
        return (self._element.end_line_number,
                self._element.end_column_number+1)
    def get_start_position_as_string(self) -> str:
        position = self.get_start_position()
        return "Line: "+str(position[0]) \
               +" Column: "+str(position[1])
    def get_end_position_as_string(self) -> str:
        position = self.get_end_position()
        return "Line: "+str(position[0]) \
               +" Column: "+str(position[1])

def parse_xml(xml: str) -> Element:
    return Element(ElementTree.fromstring(xml,parser=SpecializedParser()))

