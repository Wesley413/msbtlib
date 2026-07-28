import struct
from dataclasses import dataclass


@dataclass
class FileHeader:
  magic_number: bytes
  endianness: bytes
  unknown_0: bytes
  message_encoding: int
  version: int
  number_of_blocks: int
  unknown_1: bytes
  file_size: int

  def to_bytes(self) -> bytes:
    writer = WriterBytes()
    writer.write_bytes(self.magic_number)
    writer.write_bytes(self.endianness)

    if self.endianness != b"\xFF\xFE":
      writer.set_endianness(False)

    writer.write_bytes(self.unknown_0)
    writer.write_u8(self.message_encoding)
    writer.write_u8(self.version)
    writer.write_u16(self.number_of_blocks)
    writer.write_bytes(self.unknown_1)
    writer.write_u32(self.file_size)
    writer.align_bytes()

    return writer.bytes()

@dataclass
class BlockHeader:
  block_type: bytes
  block_size: int

  def to_bytes(self) -> bytes:
    writer = WriterBytes()

    writer.write_bytes(self.block_type)
    writer.write_u32(self.block_size)
    writer.align_bytes()

    return writer.bytes()

class ReaderBytes:
  def __init__(self, data: bytes, is_little: bool = True) -> None:
    self.data = data
    self.offset = 0
    self.endian = "<" if is_little else ">"
    
  def read_u8(self) -> int:
    value = struct.unpack_from(f"{self.endian}B", self.data, self.offset)[0]
    self.offset += 1
    return value

  def read_u16(self) -> int:
    value = struct.unpack_from(f"{self.endian}H", self.data, self.offset)[0]
    self.offset += 2
    return value
  
  def read_u32(self) -> int:
    value = struct.unpack_from(f"{self.endian}I", self.data, self.offset)[0]
    self.offset += 2
    return value

  def read_bytes(self, n: int) -> bytes:
    value = self.data[self.offset:self.offset+n]
    self.offset += n
    return value

  def set_endianness(self, is_little: bool):
    self.endian = "<" if is_little else ">"

  def align_bytes(self, alignment: int = 16):
    self.offset = (self.offset + alignment - 1) // alignment * alignment

class WriterBytes:
  def __init__(self, is_little: bool = True) -> None:
    self.buffer = bytearray()
    self.endian = "<" if is_little else ">"

  def write_bytes(self, bytes):
    self.buffer += bytes

  def write_u8(self, u8: int):
    self.buffer += struct.pack(self.endian + "B", u8)

  def write_u16(self, u16: int):
    self.buffer += struct.pack(self.endian + "H", u16)

  def write_u32(self, u32: int):
    self.buffer += struct.pack(self.endian + "I", u32)

  def set_endianness(self, is_little: bool):
    self.endian = "<" if is_little else ">"

  def align_bytes(self, alignment: int = 16):
    alignment = (len(self.buffer) + alignment - 1) // alignment * alignment
    alignment = alignment - len(self.buffer)
    self.buffer += b"\x00" * alignment

  def bytes(self) -> bytes:
    return bytes(self.buffer)
