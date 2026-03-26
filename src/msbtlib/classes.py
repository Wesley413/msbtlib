class MsbtHeader:
  def __init__(self, magic: str, endianness: str, unknown1: int, encoding: int, version: int, number_blocks: int, unknown2: int, padding: int) -> None:
    self.magic = magic
    self.endianness = endianness
    self.unknown1 = unknown1
    self.encoding = encoding
    self.version = version
    self.number_blocks = number_blocks
    self.unknown2 = unknown2
    self.padding = padding

  def show_info(self):
    for var, val in vars(self).items():
      print(var, val)

  def to_dict(self):
    return {
      "magic": self.magic,
      "endianness": self.endianness,
      "unknown1": self.unknown1,
      "encoding": self.encoding,
      "version": self.version,
      "number_blocks": self.number_blocks,
      "unknown2": self.unknown2,
      "padding": self.padding
    }



class MsbtLbl1:
  def __init__(self, block_type: str, block_size: int, block_padding: int, hash: dict, labels) -> None:
    
    self.block_type = block_type
    self.block_size = block_size
    self.block_padding = block_padding
    self.hash = hash
    self.labels = labels

  def to_dict(self):
    return {
      "block_type": self.block_type,
      "block_size": self.block_size,
      "block_padding": self.block_padding,
      "hash": self.hash,
      "labels": self.labels
    }

class MsbtAtr1:
  def __init__(self, block_type: str, block_size: int, block_padding: int, number_atributes: int, bytes_per_atributes: int, atributes: list[bytes]) -> None:
    self.block_type = block_type
    self.block_size = block_size
    self.block_padding = block_padding
    self.number_atributes = number_atributes
    self.bytes_per_atributes = bytes_per_atributes
    self.atributes = atributes

  def to_dict(self):
    atributes: list[str] = [atribute.hex() for atribute in self.atributes]

    return {
      "block_type": self.block_type,
      "block_size": self.block_size,
      "block_padding": self.block_padding,
      "number_atributes": self.number_atributes,
      "bytes_per_atributes": self.bytes_per_atributes,
      "atributes": atributes
    }
  
class MsbtAto1:
  def __init__(self, block_type: str, block_size: int, block_padding: int, content: bytes) -> None:
    self.block_type = block_type
    self.block_size = block_size
    self.block_padding = block_padding
    self.content = content

class MsbtTxt2:
  def __init__(self, block_type: str, block_size: int, block_padding: int, texts: list[list]) -> None:
    self.block_type = block_type
    self.block_size = block_size
    self.block_padding = block_padding
    self.texts = texts

  def to_dict(self):
    texts_list = []
    for full_text in self.texts:
      full_text_list = []
      for text in full_text:
        if hasattr(text, "to_dict"):
          full_text_list.append(text.to_dict())
        else:
          full_text_list.append(text)

      texts_list.append(full_text_list)

    txt2_dict = {
      "block_type": self.block_type,
      "block_size": self.block_size,
      "block_padding": self.block_padding,
      "texts": texts_list
    }

    return txt2_dict

class Text:
  def __init__(self, text: str) -> None:
    self.text = text

  def __str__(self) -> str:
    return f"Text(\"{self.text}\")"
  
  def __repr__(self):
    return self.__str__()
  
  def to_dict(self):
    text_dict = {
      "type": "text",
      "text": self.text
    }
    return text_dict

class Command:
  def __init__(self, group_id: int, group_index: int, param_size: int, param: bytes) -> None:
    self.group_id = group_id
    self.group_index = group_index
    self.param_size = param_size
    self.param = param

  def __str__(self) -> str:
    return f"Command([{self.group_id}:{self.group_index}]: {self.param.hex()})"
  
  def __repr__(self):
    return self.__str__()
  
  def to_dict(self):
    command_dict = {
      "type": "command",
      "id": self.group_id,
      "index": self.group_index,
      "param_size": self.param_size,
      "param": self.param.hex()
    }
    return command_dict