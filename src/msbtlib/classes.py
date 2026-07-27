from dataclasses import dataclass
import struct


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

  def bytes(self) -> bytes:
    return bytes(self.buffer)
