from io import BytesIO

def align_block_write(f: BytesIO, alignment=16, pad_byte=b'\xAB'):
  current_pos = f.tell()
  padding_size = (alignment - (current_pos % alignment)) % alignment
  f.write(pad_byte * padding_size)

def align_block_skip(f, alignment=16):
  current_pos = f.tell()
  padding_size = (alignment - (current_pos % alignment)) % alignment
  return padding_size

def skip(f, skip_size: int):
  f.seek(skip_size, 1)
  return skip_size