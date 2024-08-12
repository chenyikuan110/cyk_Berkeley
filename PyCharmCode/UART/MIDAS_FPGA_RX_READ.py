#!/usr/bin/env python3
# modified from eecs151 final project hex_to_serial script
import os
import serial
import math
import sys
import time
import csv


##Windows
if os.name == 'nt':
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = 'COM6' # CHANGE THIS COM PORT
    ser.open()
else:
    ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 115200


#input("Open a serial program in another terminal, then hit Enter")
write_to_csv = 0
if len(sys.argv) == 2:

    file = open(sys.argv[1], 'w', encoding='utf-8')
    csv_writer = csv.writer(file)
    write_to_csv = 1
    data = []

count = 0
print('Reading...')
for count in range(8):
    result_raw = ser.read()
    result_bin = int.from_bytes(result_raw, byteorder=sys.byteorder)
    result_bin = bin(result_bin)
    #result = binascii.hexlify(bytearray(result_raw))
    #result = count.to_bytes(8, byteorder='little')
    print(count, result_raw, result_bin[2:].zfill(8))
    #print('[getting]', hex(int.from_bytes(result, byteorder='little')), '   ,count[',count,']')
    time.sleep(0.01)
    if write_to_csv == 1:
        data.append([count, result_raw])
    #count += 1

if write_to_csv == 1:
    csv_writer.writerow(data)


exit()

print(">>Done")
