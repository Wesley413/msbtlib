from typing import Union
from pathlib import Path
import struct
from io import BufferedReader, BytesIO
from .classes import MsbtHeader, MsbtLbl1, MsbtAtr1, MsbtTxt2, MsbtAto1, MsbtTsy1, Text, Command
from .utils import align_block_skip, skip
from typing import Self
import json
from pprint import pprint

class Msbt:
  def _deserialize_element(self, data: dict):
    type_ = data.get("type")

    if type_ == "text":

      if "text" not in data:
        raise ValueError("Missing 'text' field")
      
      return Text(data["text"])
    if type_ == "command":

      try:
        param_bytes = bytes.fromhex(data["param"])
      except ValueError as e:
        raise ValueError(f"Invalid hex in command param: {data['param']}") from e
      
      return Command(
        data["id"],
        data["index"],
        data["param_size"],
        param_bytes
      )
    
    raise ValueError(f"Unknown type: {type_}")

  def parse_from_dict(self, msbt_dict: dict):
    header = msbt_dict["header"]
    lbl1 = msbt_dict["lbl1"]
    lbl1 = msbt_dict["atr1"]
    txt2 = msbt_dict["txt2"]

    self.header = MsbtHeader(**msbt_dict["header"])
    self.lbl1 = MsbtLbl1(**msbt_dict["lbl1"])
    self.atr1 = MsbtAtr1(**msbt_dict["atr1"])


    if "texts" not in txt2:
      raise ValueError("txt2.texts field missing")

    texts = [
      [self._deserialize_element(item) for item in full_text]
      for full_text in txt2["texts"]
    ]

    self.txt2 = MsbtTxt2(
      txt2["block_type"], 
      txt2["block_size"], 
      txt2["block_padding"], 
      texts)
    

  def parse_from_msbt(self, msbt_file: BufferedReader):
    magic = msbt_file.read(8).decode("ascii")
    endianness = msbt_file.read(2).hex()

    if endianness == 'fffe':
      ENDIANNESS = "<"
    elif endianness == 'feff':
      ENDIANNESS = ">"

    unsigned_short = struct.Struct(f"{ENDIANNESS}H")
    unsigned_char = struct.Struct(f"{ENDIANNESS}B")
    unsigned_int = struct.Struct(f"{ENDIANNESS}I")


    unknown1 = unsigned_short.unpack(msbt_file.read(2))[0]
    encoding = unsigned_char.unpack(msbt_file.read(1))[0]
    version = unsigned_char.unpack(msbt_file.read(1))[0]
    number_blocks = unsigned_short.unpack(msbt_file.read(2))[0]
    unknown2 = unsigned_short.unpack(msbt_file.read(2))[0]
    filesize = unsigned_int.unpack(msbt_file.read(4))[0]
    padding = skip(msbt_file, 10)

    if magic != "MsgStdBn":
      raise Exception("Invalid MSBT file")
    elif endianness != 'fffe':
      raise Exception("Big Endian Not Implemented")

    # TODO: REFACTOR <
    self.header = MsbtHeader(magic, endianness, unknown1, encoding, version, number_blocks, unknown2, padding)
    

    block_offset = msbt_file.tell()

    while filesize - msbt_file.tell() >= 4:
      msbt_file.seek(block_offset)
      block_type = msbt_file.read(4)

      if block_type == b'LBL1':
        block_offset = self._parse_lbl1(msbt_file, block_offset)
      elif block_type == b'TXT2':
        block_offset = self._parse_txt2(msbt_file, block_offset)
      elif block_type == b'ATR1':
        block_offset = self._parse_art1(msbt_file, block_offset)
      elif block_type == b'TSY1':
        block_offset = self._parse_tsy1(msbt_file, block_offset)
      elif block_type == b'ATO1':
        block_offset = self._parse_ato1(msbt_file, block_offset)
      else:
        break

  def _show_hex_address(self, reader: BufferedReader):
    print(f"Offset: 0x{reader.tell():08X}")

  def _parse_block_header(self, reader: BufferedReader, offset: int) -> tuple:
    reader.seek(offset)

    block_type = reader.read(4).decode("ascii")
    raw_block_size = reader.read(4)
    block_size = struct.unpack("<I", raw_block_size)[0]
    padding = skip(reader, 8)
    
    return block_type, block_size, padding, reader.tell()
  
  

  def _parse_txt2(self, reader: BufferedReader, offset: int) -> int:
    block_type, block_size, padding, offset = self._parse_block_header(reader, offset)

    # print(reader.tell())

    # start_offset = reader.tell()

    message_number = struct.unpack("<I", reader.read(4))[0]

    texts = []

    # skip(reader, message_number * 4)
    # print(reader.tell())

    
    def read_u16_or_default(reader, default=0xFFFF):
      try:
        data = reader.read(2)
        if len(data) < 2:
          return default
        return struct.unpack("<H", data)[0]
      except struct.error:
        return default

    for count in range(0, message_number):
      print(f"\nMessage {count}")
      messages = []
      message_offset = struct.unpack("<I", reader.read(4))[0]
      local_offset = reader.tell()
      message_offset_next = struct.unpack("<I", reader.read(4))[0]
      
      message = b""
      reader.seek(message_offset + offset)
      print(message_offset + offset)
      
      content = BytesIO(reader.read(message_offset_next - message_offset))
      print(content.read())
      content.seek(0)

      while True:
        char = content.read(2)

        if char == b"\x00\x00" or char == b"":
          if message != b"":
            messages.append(Text(message.decode("utf-16")))
          break
        if char == b"\x0E\x00":
          if message != b"":
            messages.append(Text(message.decode("utf-16")))
            message = b""
          tag_group_id = read_u16_or_default(content)
          tag_group_index = read_u16_or_default(content)
          parameter_size = read_u16_or_default(content)

          param = content.read(parameter_size)

          # TODO: BAD IMPLEMENTATION
          if b"\xAB" in param:
            param = b''
          
          print(tag_group_id, tag_group_index, parameter_size, param)
          
          messages.append(Command(tag_group_id, tag_group_index, parameter_size, param))
        else:
          message += char

      texts.append(messages)
      
      last_offset = reader.tell()
      reader.seek(local_offset)

    self.txt2 = MsbtTxt2(block_type, block_size, padding, texts)

    pprint(texts)
    # breakpoint()

    return last_offset
  
  def _parse_ato1(self, reader: BufferedReader, offset: int):
    block_type, block_size, padding, offset = self._parse_block_header(reader, offset)
    content = reader.read(block_size)

    self.ato1 = MsbtAto1(block_type, block_size, padding, content)

    return reader.tell() + align_block_skip(reader)
  
  def _parse_tsy1(self, reader: BufferedReader, offset: int) -> int:
    block_type, block_size, padding, offset = self._parse_block_header(reader, offset)

    styles = list()

    for _ in range(0, int(block_size / 4)):
      styles.append(reader.read(4))

    self.tsy1 = MsbtTsy1(block_type, block_size, padding, styles)

    return reader.tell() + align_block_skip(reader)
    

  def _parse_art1(self, reader: BufferedReader, offset: int) -> int:
    block_type, block_size, padding, offset = self._parse_block_header(reader, offset)

    number_attributes = struct.unpack("<I", reader.read(4))[0]
    bytes_per_attributes = struct.unpack("<I", reader.read(4))[0]

    attributes = list()

    for _ in range(0, number_attributes):
      attributes.append(reader.read(bytes_per_attributes))

    self.atr1 = MsbtAtr1(block_type, block_size, padding, number_attributes, bytes_per_attributes, attributes)

    return reader.tell() + align_block_skip(reader)


  def _parse_lbl1(self, reader: BufferedReader, offset: int) -> int:
    reader.seek(offset)
    block_type, block_size, padding, offset = self._parse_block_header(reader, offset)

    block_data = reader.read(block_size)
    hash_map, labels = self._parse_lbl1_block(BytesIO(block_data), block_size)

    self.lbl1 = MsbtLbl1(block_type, block_size, padding, hash_map, labels)

    return reader.tell() + align_block_skip(reader)


    

  def _parse_lbl1_block(self, reader: BytesIO, block_size: int) -> tuple:
    bucket_number = struct.unpack("<I", reader.read(4))[0]

    hash_table = {"number_of_buckets": bucket_number}
    buckets = []

    for _ in range(1, bucket_number + 1):
      number_of_labels, offset = struct.unpack("<II", reader.read(8))
      buckets.append({
        "number_of_labels": number_of_labels,
        "offset": offset
      })

    hash_table["buckets"] = buckets
    labels = []

    remaning_bytes = block_size - reader.tell()

    while remaning_bytes >= 5:
      label_length = struct.unpack("<B", reader.read(1))[0]

      if remaning_bytes < label_length + 4:
        raise Exception("bad lbl1")

      label_string = reader.read(label_length).decode("utf-8")
      label_index = struct.unpack("<I", reader.read(4))[0]

      labels.append({
        "label_string": label_string,
        "label_index": label_index
      })

      remaning_bytes = block_size - reader.tell()

    return (hash_table, labels)


  @classmethod
  def from_msbt(cls, file_path: Union[str, Path]) -> Self:
    with open(file_path, "rb") as f:      
      msbt = cls()
      msbt.parse_from_msbt(f)

    return msbt

     
  
  @classmethod
  def from_json(cls, json_data: str) -> Self:
    msbt = cls()
    msbt.parse_from_dict(json.loads(json_data))

    return msbt

  @classmethod
  def from_dict(cls, msbt_dict: dict) -> Self:
    msbt = cls()
    msbt.parse_from_dict(msbt_dict)
    
    return msbt