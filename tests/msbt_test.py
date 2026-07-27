from msbtlib.msbt import return_magic_number, read_file_header
from msbtlib.classes import FileHeader
import hashlib
from io import BytesIO
from pprint import pprint


def test_read_magic_number():
  expected = b"MsgStdBn"

  assert expected == return_magic_number("./tests/data/example.msbt")

def test_return_file_header():
  expected = FileHeader(
    b"MsgStdBn",
    b"\xff\xfe",
    b"\x00\x00",
    1,
    1,
    1,
    b"\x00\x00",
    10000)

  assert expected == read_file_header("./tests/data/example.msbt")

def test_file_header_to_bytes():
  excepted = b"MsgStdBn\xff\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

  assert excepted == FileHeader(b"MsgStdBn", b"\xff\xfe", b"\x00\x00", 0, 0, 0, b"\x00\x00", 0).to_bytes()