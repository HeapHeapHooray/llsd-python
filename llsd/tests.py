# This code can be found at: https://github.com/HeapHeapHooray/llsd-python

from . import llsd
from . import parsingexceptions
import uuid
import datetime

def test_decorator(func):
    def test():
        func()
        print("Test passed succesfully.")
    return test

def parse(llsd_xml: str):
    return llsd.parse_llsd_serialized_as_xml(llsd_xml)

def assert_is_invalid_value(llsd_xml: str):
    try:
        parse(llsd_xml)
        raise AssertionError
    except parsingexceptions.InvalidValue:
        pass

@test_decorator
def test_undef():
    assert(type(parse("<llsd><undef></undef></llsd>")) == llsd.Undefined)
    assert(type(parse("<llsd><undef/></llsd>")) == llsd.Undefined)

@test_decorator
def test_boolean():
    assert(parse("<llsd><boolean>0</boolean></llsd>") == False)
    assert(parse("<llsd><boolean>1</boolean></llsd>") == True)
    assert(parse("<llsd><boolean>0.0</boolean></llsd>") == False)
    assert(parse("<llsd><boolean>1.0</boolean></llsd>") == True)
    assert(parse("<llsd><boolean>false</boolean></llsd>") == False)
    assert(parse("<llsd><boolean>true</boolean></llsd>") == True)
    assert(parse("<llsd><boolean></boolean></llsd>") == False)
    assert(parse("<llsd><boolean/></llsd>") == False)
    assert_is_invalid_value("<llsd><boolean>Invalid Value</boolean></llsd>")

@test_decorator
def test_integer():
    assert(parse("<llsd><integer>0</integer></llsd>") == 0)
    assert(parse("<llsd><integer>-300</integer></llsd>") == -300)
    assert(parse("<llsd><integer>+20</integer></llsd>") == 20)
    assert(parse("<llsd><integer></integer></llsd>") == 0)
    assert(parse("<llsd><integer/></llsd>") == 0)
    assert_is_invalid_value("<llsd><integer>2.0</integer></llsd>")
    assert_is_invalid_value("<llsd><integer>Invalid Value</integer></llsd>")

@test_decorator
def test_real():
    assert(parse("<llsd><real>0</real></llsd>") == 0.0)
    assert(parse("<llsd><real>0.0</real></llsd>") == 0.0)
    assert(parse("<llsd><real>121.5</real></llsd>") == 121.5)
    assert(parse("<llsd><real>-222.2</real></llsd>") == -222.2)
    assert_is_invalid_value("<llsd><real>1.2.3</real></llsd>")
    assert_is_invalid_value("<llsd><real>Invalid Value</real></llsd>")

@test_decorator
def test_uuid():
    assert(parse("<llsd><uuid>00000000-0000-0000-0000-000000000000</uuid></llsd>") == uuid.UUID("00000000-0000-0000-0000-000000000000"))
    assert(parse("<llsd><uuid></uuid></llsd>") == uuid.UUID("00000000-0000-0000-0000-000000000000"))
    assert(parse("<llsd><uuid/></llsd>") == uuid.UUID("00000000-0000-0000-0000-000000000000"))
    assert(parse("<llsd><uuid>C0FFEEEE-C0FF-EEC0-FFEE-C0FFEEC0FFEE</uuid></llsd>") == uuid.UUID("C0FFEEEE-C0FF-EEC0-FFEE-C0FFEEC0FFEE"))
    assert_is_invalid_value("<llsd><uuid>IN-VA-LID-VA-LUE</uuid></llsd>")

@test_decorator
def test_date():
    assert(parse("<llsd><date>2006-02-01T14:29:53.43Z</date></llsd>") == datetime.datetime(2006, 2, 1, 14, 29, 53, 430000))
    assert(parse("<llsd><date></date></llsd>") == datetime.datetime(1970, 1, 1))
    assert(parse("<llsd><date/></llsd>") == datetime.datetime(1970, 1, 1))
    assert_is_invalid_value("<llsd><date>2006-02-01T14:29::53.43Z</date></llsd>")
    assert_is_invalid_value("<llsd><date>2006-02-01T14:29:53..43Z</date></llsd>")
    assert_is_invalid_value("<llsd><date>2006--02-01T14:29:53.43Z</date></llsd>")
    assert_is_invalid_value("<llsd><date>2O06-02-01T14:29:53.43Z</date></llsd>")

@test_decorator
def test_map():
    assert(parse("""<llsd><map>
                             <key>test</key><boolean>1</boolean>
                             <key>test2</key><boolean>0.0</boolean>
                             </map></llsd>
                          """) == {"test": True,"test2": False})
    assert(parse("""<llsd><map>
                             <key>test</key><map>
                             <key>test</key><boolean>1</boolean>
                             <key>test2</key><boolean>0.0</boolean>
                             </map>
                             <key>test2</key><boolean>0.0</boolean>
                             </map></llsd>
                          """) == {"test": {"test": True,"test2": False},"test2": False})
    assert_is_invalid_value("""<llsd><map>
                             <key>test</key><boolean>1</boolean>
                             <integer>test2</integer><boolean>0.0</boolean>
                             </map></llsd>
                          """)
    assert_is_invalid_value("""<llsd><map>
                             <key>test</key><boolean>1</boolean>
                             <key>test</key><boolean>0.0</boolean>
                             </map></llsd>
                          """)

def test_all():
    print("Testing undefined type...")
    test_undef()
    print("Testing boolean type...")
    test_boolean()
    print("Testing integer type...")
    test_integer()
    print("Testing real type...")
    test_real()
    print("Testing uuid type...")
    test_uuid()
    print("Testing date type...")
    test_date()

    print("Testing map type...")
    test_map()

    print("All Tests passed succesfully.")
    
    
    
