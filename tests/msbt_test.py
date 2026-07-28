import hashlib
from io import BytesIO
from pprint import pprint

from msbtlib.classes import BlockHeader, FileHeader
from msbtlib.msbt import read_block_header, read_file_header, return_magic_number


def test_read_magic_number():
  expected = b"MsgStdBn"

  assert expected == return_magic_number("./tests/data/example.msbt")

def test_return_file_header():
  file_path = "./tests/data/file_header.msbt"
  expected = FileHeader(
    magic_number=b"MsgStdBn",
    endianness=b"\xff\xfe",
    unknown_0=b"\x00\x00",
    message_encoding=1,
    version=1,
    number_of_blocks=1,
    unknown_1=b"\x00\x00",
    file_size=10000
  )

  with open(file_path, "wb") as f:
    f.write(expected.to_bytes())

  assert expected == read_file_header(file_path)

def test_read_block_header():
  file_path = "./tests/data/block_header.msbt"
  excepted = BlockHeader(
    block_type=b"LBL1",
    block_size=1000
  )

  with open(file_path, "wb") as f:
    f.write(excepted.to_bytes())

  assert excepted == read_block_header(file_path)

def test_file_header_to_bytes():
  excepted = b"MsgStdBn\xff\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

  assert excepted == FileHeader(b"MsgStdBn", b"\xff\xfe", b"\x00\x00", 0, 0, 0, b"\x00\x00", 0).to_bytes()