from typing import Union
from pathlib import Path
import struct
from io import BufferedReader, BytesIO
from .classes import MsbtHeader, MsbtLbl1, MsbtAtr1, MsbtTxt2, MsbtAto1, MsbtTsy1, Text, Command
from .utils import align_block_skip, skip
from typing import Self
import json
from pprint import pprint