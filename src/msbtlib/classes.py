class MsbtHeader:
  def __init__(self, magic: str, endianness: str, unknown1: int, encoding: int, version: int, number_blocks: int, unknown2: int, filesize: int, padding: bytes) -> None:
    self.magic = magic
    self.endianness = endianness
    self.unknown1 = unknown1
    self.encoding = encoding
    self.version = version
    self.number_blocks = number_blocks
    self.unknown2 = unknown2
    self.filesize = filesize
    self.padding = padding

  def show_info(self):
    for var, val in vars(self).items():
      print(var, val)



class MsbtLbl1:
  def __init__(self, block_type: str, block_size: int, block_padding: bytes, hash: dict, labels) -> None:
    
    self.block_type = block_type
    self.block_size = block_size
    self.block_padding = block_padding
    self.hash = hash
    self.labels = labels

class MsbtAtr1:
  def __init__(self, block_type: str, block_size: int, block_padding: bytes, number_atributes: int, bytes_per_atributes: int) -> None:
    self.block_type = block_type
    self.block_size = block_size
    self.block_padding = block_padding
    self.number_atributes = number_atributes
    self.bytes_per_atributes = bytes_per_atributes

class MsbtTxt2:
  def __init__(self, block_type: str, block_size: int, block_padding: bytes, texts: list) -> None:
    self.block_type = block_type
    self.block_size = block_size
    self.block_padding = block_padding
    self.texts = texts

class Text:
  def __init__(self, text: str) -> None:
    self.text = text

  def __str__(self) -> str:
    return f"\"{self.text}\""
  
  def __repr__(self):
    return self.__str__()

class Command:
  def __init__(self, group_id: int, group_index: int, param_size: int, param: bytes) -> None:
    self.group_id = group_id
    self.group_index = group_index
    self.param_size = param_size
    self.param = param

  def __str__(self) -> str:
    return f"({self.group_id}:{self.group_index}): {self.param.hex()}"
  
  def __repr__(self):
    return self.__str__()