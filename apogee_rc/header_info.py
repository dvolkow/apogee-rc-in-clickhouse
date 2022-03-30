import argparse
from astropy.io import fits
from wetllib.adapters import ClickHouseIO


arg_parser = argparse.ArgumentParser(description="Update boards images")
arg_parser.add_argument("-f", "--file", dest="filename", help="Source data filename (path).")
args = arg_parser.parse_args()


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


for row in data:
    for i, row_data in enumerate(row):
        print("-----")
        print(hdr[i])
        print(row_data)
    break
