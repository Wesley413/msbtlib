from msbtlib.msbt import Msbt
from msbtlib.msbt_writer import MsbtWrite
import hashlib

def test_msbt_integrity():

    

    result = Msbt.from_msbt("./tests/data/example.msbt")
    output = MsbtWrite(result).get_output()

    with open("./tests/data/example.msbt", "rb") as f:
        input_hash = hashlib.sha256(f.read())
    
    output_hash = hashlib.sha256(output.read())

    assert input_hash.hexdigest() == output_hash.hexdigest()