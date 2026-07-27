from msbtlib.classes import FileHeader, ReaderBytes


def read_file_header(file_path: str) -> FileHeader:
  with open (file_path, "rb") as f:
    reader = ReaderBytes(f.read())

  magic_number = reader.read_bytes(8)
  endianness = reader.read_bytes(2)

  if endianness != b"\xFF\xFE":
    reader.set_endianness(False)

  return FileHeader (
    magic_number=magic_number,
    endianness=endianness,
    unknown_0=reader.read_bytes(2),
    message_encoding=reader.read_u8(),
    version=reader.read_u8(),
    number_of_blocks=reader.read_u16(),
    unknown_1=reader.read_bytes(2),
    file_size=reader.read_u32()
  )



def return_magic_number(file: str):
  with open(file, "rb") as f:
    result = f.read()

  return result[0:8]
