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

class ReaderBytes:
  def __init__(self, data: bytes, is_little: bool = True) -> None:
    self.data = data
    self.offset = 0
    self.endian = "<" if is_little else ">"

  def set_endianness(self, is_little: bool):
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