from .msbt import Msbt
from io import BytesIO
from typing import Literal
import struct
from .classes import *

class MsbtWrite:
  def __init__(self, msbt: Msbt) -> None:
    self.msbt = msbt
    self.output = BytesIO()

    encode_type = str(self.msbt.header.encoding)
    endian_type = self.msbt.header.endianness


    endians = {
      "fffe": "little",
      "feff": "big"
    }

    encodes = {
      "0": "utf-8",
      "1": "utf-16",
      "2": "utf-32"
    }

    try:
      self.endian = endians[endian_type]
      self.endian_prefix = "<" if self.endian == "little" else ">"

    except KeyError:
      raise ValueError(f"Invalid MSBT encoding type: {endian_type}")

    try:
      self.encode = encodes[encode_type]
    except KeyError:
      raise ValueError(f"Invalid MSBT encoding type: {encode_type}")

    offset, filesize_offset = self._header_write(self.output)
    offset = self._lbl1_write(self.output, offset)
    offset_old = self._atr1_write(self.output, offset)
    offset = self._txt2_write(self.output, offset_old)

    self.output.seek(0)

    filesize = len(self.output.read())


    struct.pack_into("<I", self.output.getbuffer(), filesize_offset, filesize)

    # self.output.seek(0)
    # self.output.seek(offset_old)
    # print(self.output.read())
    # self.output.seek(offset)
    # print(hex(self.output.tell()))

    # with open("test.msbt", "wb") as f:
    #   self.output.seek(0)
    #   f.write(self.output.read())

  def get_output(self) -> BytesIO:
    self.output.seek(0)
    return self.output

  @classmethod
  def to_json(self, msbt: Msbt) -> None:
    raise Exception("Not Implemented")

  @classmethod
  def to_dict(self, msbt: Msbt) -> None:
    raise Exception("Not Implemented")


  @classmethod
  def to_yaml(self, msbt: Msbt) -> None:
    raise Exception("Not Implemented")


  def align_block(self, f: BytesIO, alignment=16, pad_byte=b'\xAB'):
    current_pos = f.tell()
    padding_size = (alignment - (current_pos % alignment)) % alignment
    f.write(pad_byte * padding_size)

  
  def _header_write(self, output: BytesIO, offset = 0) -> tuple:
    output.seek(offset)

    header_struct = struct.Struct(
        self.endian_prefix + "8s 2s H B B H H"
    )

    output.write(
        header_struct.pack(
            self.msbt.header.magic.encode("ascii"),
            bytes.fromhex(self.msbt.header.endianness),
            self.msbt.header.unknown1,
            self.msbt.header.encoding,
            self.msbt.header.version,
            self.msbt.header.number_blocks,
            self.msbt.header.unknown2
        )
    )

    
    filesize_offset = output.tell()
    output.write(b"\x00\x00\x00\x00") # filesize placeholder

    output.write(self.msbt.header.padding)

    self.align_block(output)

    return output.tell(), filesize_offset
  
  def _block_header_write(self, output: BytesIO, func):
    block_header_struct = struct.Struct(
      self.endian_prefix + "4s I 8s"
    )

    output.write(
      block_header_struct.pack(
        func.block_type.encode("ascii"),
        func.block_size,
        func.block_padding
      )
    )

  def _lbl1_write(self, output: BytesIO, offset = 0) -> int:
    output.seek(offset)
    self._block_header_write(output, self.msbt.lbl1)

    number_of_buckets = int(self.msbt.lbl1.hash["number_of_buckets"])
    buckets = self.msbt.lbl1.hash["buckets"]


    output.write(number_of_buckets.to_bytes(4, byteorder=self.endian))

    bucket_struct = struct.Struct(
        self.endian_prefix + "I I"
    )

    for bucket in buckets:
      output.write(
        bucket_struct.pack(
          bucket["number_of_labels"],
          bucket["offset"]
        )
      )


    for label in self.msbt.lbl1.labels:
      label_len = len(label["label_string"])

      label_struct = struct.Struct(
        self.endian_prefix + f"B {label_len}s I"
      )

      output.write(
        label_struct.pack(
          len(label["label_string"]),
          label["label_string"].encode("ascii"),
          label["label_index"]
        )
      )

    self.align_block(output)

    return output.tell()
  
  def _atr1_write(self, output: BytesIO, offset = 0):
    # TODO: BAD IMPLEMENTATION
    output.seek(offset)
    self._block_header_write(output, self.msbt.atr1)


    atributes_struct = struct.Struct(
      self.endian_prefix + "I I"
    )

    number_atributes = len(self.msbt.txt2.texts)

    output.write(
      atributes_struct.pack(
        number_atributes,
        self.msbt.atr1.bytes_per_atributes
        )
      )
    
    print(self.msbt.atr1.number_atributes)
    
    self.align_block(output)
        
    return output.tell()
  
  def _txt2_write(self, output: BytesIO, offset = 0):
    output.seek(offset)
    self._block_header_write(output, self.msbt.txt2)

    texts_struct = struct.Struct(
      self.endian_prefix + "I"
    )

    # TODO: POSSIVEL PROBLEMA
    output.write(
      texts_struct.pack(
        len(self.msbt.txt2.texts)
      )
    )

    initial_offset = len(self.msbt.txt2.texts) * 4 + 4

    current_offset = initial_offset

    offsets = []

    messages_bytes = b""
    messages_offset_bytes = b""

    for message in self.msbt.txt2.texts:
      messages_offset_bytes += current_offset.to_bytes(4, "little")
      offsets.append(current_offset)

      for element in message:
        if type(element) is Command:
          
          command_struct = struct.Struct(
            self.endian_prefix + f"2s H H H {len(element.param)}s"
          )
          
          command = command_struct.pack(
            b"\x0E\x00",
            element.group_id,
            element.group_index,
            element.param_size,
            element.param
          )
          current_offset += len(command)
        
          messages_bytes += command
        
        
        elif type(element) is Text:
          current_offset += len(element.text.encode('utf-16-le')) # TODO: FIX THIS
          # print(element.text)

          messages_bytes += element.text.encode('utf-16-le') # TODO: AND THIS AS WELL


      current_offset += len(b"\x00\x00")
      messages_bytes += b"\x00\x00"
      # print(len(b"\x00\x00"))

    output.write(messages_offset_bytes + messages_bytes)

    self.align_block(output)

    return output.tell()
