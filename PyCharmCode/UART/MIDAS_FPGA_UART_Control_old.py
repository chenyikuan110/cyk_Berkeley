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

if len(sys.argv) == 2:
    # file writing mode
    # there should be a file that contains up to 128 scan bit
    #with open(sys.argv[1], "r") as f:
    #    program = f.readlines()
    #if ('@' in program[0]):
    #    program = program[1:] # remove first line '@0'
    #program = [inst.rstrip() for inst in program]
    # size = len(program)*4 # in bytes
    file = open(sys.argv[1], 'r', encoding='utf-8')
    csv_reader = csv.reader(file)
    bits = []
    count = 0
    for row in csv_reader:
        #print(row)
        bits.append([count, int(row[1])])
        count += 1
    #print(rows)


    for count in range(88): # there are bit 0 to 87
        addr = bits[count][0]
        addr_1 = int(math.floor(addr/10))
        addr_0 = int(addr-addr_1*10)
        print('[sending ASCII]',bits[count][1],'to address', addr, ':', 49, 48+addr_1, 48+addr_0, bits[count][1])
        ser.write(bytearray([49, 48+addr_1, 48+addr_0, bits[count][1]]))
        time.sleep(0.01)

    print('Verifying...')
    err_count = 0
    for count in range(88): # there are bit 0 to 87
        addr = bits[count][0]
        addr_1 = int(math.floor(addr/10))
        addr_0 = int(addr-addr_1*10)

        ser.write(bytearray([48, 48+addr_1, 48+addr_0]))
        time.sleep(0.01)
        result = int(ser.read())
        print('[getting]', result, 'from address', addr)
        time.sleep(0.01)
        if(result != bits[count][1]):
            err_count += 1

    print("Verification done! Total error is", err_count)
    exit()

elif len(sys.argv) == 1:
    quit_flag = 0
    while(quit_flag == 0):
        task = input('>> usage:<w/r> <addr> <bit>, for example, '
                     'to write 1 into addr<8>, type w 8 1, or type q to quit\r\n')
        task = task.split()
        if(len(task) == 3):
            if(task[0] != 'w'):
                print(">> error: usage:<w/r> <addr> <bit>")
            addr = int(task[1])
            if(addr >= 88):
                print(">> error: scan address must be within 0 to 87.\r\n")
                continue
            addr_1 = int(math.floor(addr / 10))
            addr_0 = int(addr - addr_1 * 10)
            val = int(task[2])
            print('[sending ASCII]', val, 'to address', addr, ':', 49, 48 + addr_1, 48 + addr_0, val)
            ser.write(bytearray([49, 48 + addr_1, 48 + addr_0, val]))

            ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
            time.sleep(0.01)
            result = int(ser.read())
            print('[getting]', result, 'from address', addr)
            time.sleep(0.01)
        elif (len(task) == 2):
            if (task[0] != 'r'):
                print(">> error: usage:<w/r> <addr> <bit>")
            addr = int(task[1])
            if (addr >= 88):
                print(">> error: scan address must be within 0 to 87.\r\n")
                continue
            addr_1 = int(math.floor(addr / 10))
            addr_0 = int(addr - addr_1 * 10)

            ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
            time.sleep(0.01)
            result = int(ser.read())
            print('[getting]', result, 'from address', addr)
            time.sleep(0.01)
        elif task[0] == 'q':
            quit_flag = 1
        else:
            print(">> error: usage:<w/r> <addr> <bit>")

print(">>Done")
