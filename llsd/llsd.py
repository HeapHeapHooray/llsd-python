# This code can be found at: https://github.com/HeapHeapHooray/llsd-python

from . import xmlparser
from . import parsingexceptions
from . import utils
import uuid
import datetime
import re
from typing import Union

class Undefined:
    pass

class Binary:
    def __init__(self,encoding: str,data: str):
        self.encoding = encoding
        self.data = data

class URI:
    def __init__(self,data: str):
        self.data = data

def parse_llsd_serialized_as_xml(llsd_xml: str) -> Union[Undefined,bool,int,float,str,uuid.UUID,datetime.datetime,URI,Binary,dict,list]:
    root = xmlparser.parse_xml(llsd_xml)

    if root.get_tag().lower() != "llsd":
        raise parsingexceptions.LLSDTagNotFound('"llsd" tag was expected at {}.'.format(root.get_start_position_as_string()))

    children = root.get_children()

# Here we treat the data contained in "llsd" as a list
# but that will likely never happen and it will just contain a single element.
    parsed_data = [_parse_type(element) for element in children]

# If theres just a single element in "llsd" we return the parsed data as
# a single element.
    if len(parsed_data) == 1:
        return parsed_data[0]
    
    if len(parsed_data) < 1:
        return None

    return parsed_data

def _parse_type(element: xmlparser.Element) -> Union[Undefined,bool,int,float,str,uuid.UUID,datetime.datetime,URI,Binary,dict,list]:
    type_tag = element.get_tag().lower()

# Atomic Types - as defined in: http://wiki.secondlife.com/wiki/LLSD#Atomic_Types

    if type_tag in ["undef"]:
        return Undefined()
    if type_tag in ["boolean"]:
        return _parse_boolean(element)
    if type_tag in ["integer"]:
        return _parse_integer(element)
    if type_tag in ["real"]:
        return _parse_real(element)
    if type_tag in ["string"]:
        return _parse_string(element)
    if type_tag in ["uuid"]:
        return _parse_uuid(element)
    if type_tag in ["date"]:
        return _parse_date(element)
    if type_tag in ["uri"]:
        return _parse_uri(element)
    if type_tag in ["binary"]:
        return _parse_binary(element)

# Containers - as defined in: http://wiki.secondlife.com/wiki/LLSD#Containers

    if type_tag in ["map"]:
        return _parse_map(element)
    if type_tag in ["array"]:
        return _parse_array(element)

    raise parsingexceptions.UnexpectedType('Found an unexpected type "{}" at {}.'.format(element.get_tag(),
                                                                                element.get_start_position_as_string()))
    
def _parse_boolean(element: xmlparser.Element) -> bool:
    text_data = element.get_text().lower()

    if text_data in ["0","0.0","false",""]:
        return False
    if text_data in ["1","1.0","true"]:
        return True

    raise parsingexceptions.InvalidValue('Found an invalid value "{}" while parsing a boolean type at {}.'.format(element.get_text(),
                                                                                                         element.get_start_position_as_string()))

def _parse_integer(element: xmlparser.Element) -> int:
    if element.get_text() == "":
        return 0
    extracted_integer = 0
    try:
        extracted_integer = int(element.get_text())
    except ValueError:
        raise parsingexceptions.InvalidValue('Found an invalid value "{}" while parsing an integer type at {}.'.format(element.get_text(),
                                                                                                              element.get_start_position_as_string()))

    return extracted_integer

def _parse_real(element: xmlparser.Element) -> float:
    if element.get_text() == "":
        return 0.0
    extracted_float = 0.0
    try:
        extracted_float = float(element.get_text())
    except ValueError:
        raise parsingexceptions.InvalidValue('Found an invalid value "{}" while parsing a real type at {}.'.format(element.get_text(),
                                                                                                          element.get_start_position_as_string()))

    return extracted_float

def _parse_string(element: xmlparser.Element) -> str:
    return element.get_text()

def _parse_uuid(element: xmlparser.Element) -> str:
    if element.get_text() == "":
        return uuid.UUID("00000000-0000-0000-0000-000000000000")
    
    try:
        extracted_uuid = uuid.UUID(element.get_text())
    except ValueError:
        raise parsingexceptions.InvalidValue('Found an invalid value "{}" while parsing an uuid type at {}.'.format(element.get_text(),
                                                                                                           element.get_start_position_as_string()))

    return extracted_uuid

def _parse_date(element: xmlparser.Element) -> datetime.datetime:
# Based on Linden Lab's implementation of "_parse_datestr" in https://bitbucket.org/lindenlab/llbase/src/master/llbase/llsd.py
    
# if the element's text is an empty string, then, return UNIX epoch time.
    if element.get_text() == "":
        return datetime.datetime(1970, 1, 1)

    date_regex = re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T"
                            r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
                            r"(?P<second_float>(\.\d+)?)Z")

    match = re.match(date_regex,element.get_text())
    if not match:
        raise parsingexceptions.InvalidValue('Found an invalid value "{}" while parsing a date type at {}.'.format(element.get_text(),
                                                                                                          element.get_start_position_as_string()))

    year = int(match.group('year'))
    month = int(match.group('month'))
    day = int(match.group('day'))
    hour = int(match.group('hour'))
    minute = int(match.group('minute'))
    second = int(match.group('second'))
    seconds_float = match.group('second_float')
    usec = 0
    if seconds_float:
        usec = int(float('0' + seconds_float) * 1e6)
        
    return datetime.datetime(year, month, day, hour, minute, second, usec)

def _parse_uri(element: xmlparser.Element) -> URI:
    return URI(element.get_text())
 
def _parse_binary(element: xmlparser.Element) -> Binary:
    attributes = element.get_attributes()
    encoding = attributes.get("encoding")
    if encoding == None:
        encoding = "base64"

    return Binary(encoding=encoding,data=element.get_text())

def _parse_map(element: xmlparser.Element) -> dict:
    children = element.get_children()

    if utils.is_odd(len(children)):
        raise parsingexceptions.InvalidValue("The map at {} is invalid, the elements count is odd, therefore, it can't be organized into key-value pairs.".format(element.get_start_position_as_string()))

    output_dict = {}

# The llsd-xml map has the key-value pairs as a list of elements in the following way:
# [key,value,key,value,key,value...]
# The utils.pairwise function returns a zip iterable that unrolls in the following list:
# [(key,value),(key,value),(key,value)...]

    for key,value in utils.pairwise(children):
        if key.get_tag().lower() != "key":
            raise parsingexceptions.InvalidValue('The map at {} is invalid, it was expected a "key" tag at {} but was "{}" instead.'.format(element.get_start_position_as_string(),
                                                                                                                                            key.get_start_position_as_string(),
                                                                                                                                            key.get_tag()))
        key_data = _parse_string(key)
        if key_data in output_dict.keys():
            raise parsingexceptions.InvalidValue("The map at {} is invalid, there is a repeated key at {}.".format(element.get_start_position_as_string(),
                                                                                                                  key.get_start_position_as_string()))
        output_dict[key_data] = _parse_type(value)

    return output_dict

def _parse_array(element: xmlparser.Element) -> list:
    return [_parse_type(child) for child in element.get_children()]

