#!/usr/bin/env python3
# modified from eecs151 final project hex_to_serial script
import os
import serial
import math
import sys
import time
import numpy as np
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
dict_cmd = {
    'TX_DAC_frequency_word' :[0,2]
    ,'TX_DAC_initial_phase' :[2,2]
    ,'TX_IQ_phase_diff'     :[4,2]
    ,'TX_Mult_enable'       :[6,1]
    ,'TX_Mult_gain'         :[7,3]
    ,'VM_DAC_frequency_word':[10,2]
    ,'VM_DAC_initial_phase' :[12,2]
    ,'VM_IQ_phase_diff'     :[14,2]
    ,'VM_Mult_enable'       :[16,1]
    ,'VM_Mult_gain'         :[17,3]
}

# reset value
def reset_all():
    addr = []
    val = []
    for cmd_keys, cmd_vals in dict_cmd.items():
        addr_, ignore, val_ = parse_cmd(cmd_keys, 0)
        addr.append(addr_)
        val.append(val_)
    return np.concatenate(addr), np.concatenate(val)


def int_to_bytes(num, width):
    byte_array = []
    if num < 0:
        num = 2 ** (8*width) + num
    for ii in range(width):
        byte_array.append(num & 0X00FF)
        num = int(num >> 8)
    return byte_array

def parse_cmd(cmd, val):
    start_addr = dict_cmd[cmd][0]
    width = dict_cmd[cmd][1]
    address = [n for n in reversed(range(start_addr, start_addr+width))]

    print(cmd, val, address, int_to_bytes(val, width))

    return address, int_to_bytes(val, width)

if len(sys.argv) == 1:
    quit_flag = 0
    while quit_flag == 0:
        task = input('>> usage:VAR_NAME VAL, for example, '
                     'to write 8192 into TX_Mult_gain, type TX_Mult_gain 8192, or type q to quit\r\n')
        task = task.split()
        if len(task) == 2:
            if task[0] == 'reset' and task[1] == 'all':
                addr, val = reset_all()
            elif task[1] == 'reset':
                addr, ignore, val = parse_cmd(task[0], 0)
            else:
                addr, val, ignore = parse_cmd(task[0], int(task[1]))
            for i in range(len(addr)):
                msg = '[sending] ' + str(val[i]) + ' to address ' \
                      + str(addr[i]) + ': ' + str(49) + ' ' + str(addr[i]) + ' ' + str(val[i])
                print(msg)
                ser.write(bytearray([49, addr[i], val[i]]))
                time.sleep(0.01)

        elif len(task) == 1:
            if task[0] == 'q':
                quit_flag = 1
        else:
            print(">> error: usage:<w/r> <addr> <bit>")

print(">>Done")
