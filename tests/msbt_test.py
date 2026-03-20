from msbtlib.msbt import Msbt
from msbtlib.msbt_writer import MsbtWrite
import hashlib
from pprint import pprint

def test_msbt_integrity():
    result = Msbt.from_msbt("./tests/data/example.msbt")
    output = MsbtWrite(result).get_output()

    with open("./tests/data/example.msbt", "rb") as f:
        input_hash = hashlib.sha256(f.read())
    
    output_hash = hashlib.sha256(output.read())

    assert input_hash.hexdigest() == output_hash.hexdigest()

def test_msbt_dict():
    msbt = Msbt.from_msbt("./tests/data/example.msbt")

    msbt_dict = MsbtWrite(msbt).to_dict()

    with open("./tests/data/example.msbt", "rb") as f:
        input_hash = hashlib.sha256(f.read())

    msbt_from_dict = Msbt.from_dict(msbt_dict)

    output = MsbtWrite(msbt_from_dict).get_output()

    output_hash = hashlib.sha256(output.read())

    assert input_hash.hexdigest() == output_hash.hexdigest()

def test_msbt_json():
    msbt = Msbt.from_msbt("./tests/data/example.msbt")

    msbt_json = MsbtWrite(msbt).to_json()

    print(msbt_json)

    with open("./tests/data/example.msbt", "rb") as f:
        input_hash = hashlib.sha256(f.read())

    msbt_from_json = Msbt.from_json(msbt_json)
    output = MsbtWrite(msbt_from_json).get_output()

    output_hash = hashlib.sha256(output.read())

    assert input_hash.hexdigest() == output_hash.hexdigest()

