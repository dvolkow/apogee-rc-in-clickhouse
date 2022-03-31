import argparse
from copy import deepcopy
from typing import Any, List
from pprint import pprint
from astropy.io import fits
from wetllib.adapters import ClickHouseIO


arg_parser = argparse.ArgumentParser(description="Update boards images")
arg_parser.add_argument("-f", "--file", dest="filename", help="Source data filename (path).")
args = arg_parser.parse_args()


table_desc = ClickHouseIO.get_data('''
DESCRIBE TABLE apogee.rc
''', 'localhost')

scheme = {}
inv_scheme = {}
ints = {'Int16', 'Int32', 'Int64'}
floats = {'Float32', 'Float64'}
strings = {'String', 'LowCardinality(String)'}
int_arrays = {'Array(Int32)'}
float_arrays = {'Array(Float32)', 'Array(Float64)'}


for row in table_desc.itertuples(index=False):
    inv_scheme[row.name] = row.type
    if row.type not in scheme:
        scheme[row.type] = [row.name]
    else:
        scheme[row.type].append(row.name)


#pprint(scheme)
pprint(inv_scheme)


def to_int_array(value: Any) -> List[int]:
    res = []
    for v in value.ravel():
        res.append(int(v))
    return res


def to_float_array(value: Any) -> List[int]:
    res = []
    for v in value.ravel():
        res.append(float(v))
    return res


hdul = fits.open(args.filename)
header = hdul[1].header

counter = 0
hdr = []
labels = []
for i, row in enumerate(str(header).split('/')):
    if i < 8:
        continue

    if not 'label for field' in row:
        hdr.append(row)
        counter += 1


print(counter)


data = fits.getdata(args.filename)
result_list = []


for rownum, row in enumerate(data):
    print(f"#{rownum}: process...")
    value = {}
    for i, row_data in enumerate(row):
        name = str(str(hdr[i]).replace(' ', '').split("=")[-1]).replace("'", "").strip()
        if inv_scheme[name] in ints:
            row_data = int(row_data)
        if inv_scheme[name] in floats:
            row_data = float(row_data)
        if inv_scheme[name] in strings:
            row_data = str(row_data)
        if inv_scheme[name] in int_arrays:
            row_data = to_int_array(row_data)
        if inv_scheme[name] in float_arrays:
            row_data = to_float_array(row_data)

        value.update({name: row_data})
    result_list.append(value)


if len(result_list) > 0:
    ClickHouseIO.put_dict(result_list, 'apogee.rc', 'localhost', [key for key in result_list[0]])
