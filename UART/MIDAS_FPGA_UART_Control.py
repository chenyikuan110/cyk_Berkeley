#!/usr/bin/env python3
# modified from eecs151 final project hex_to_serial script
import os
import serial
import math
import sys
import time
import csv


# helper
def get_check_bits(ser):
    bits_received = []
    for ii in (range(58, 69)):  # there are bit 58 to 68 for bit select
        addr = ii
        addr_1 = int(math.floor(addr / 10))
        addr_0 = int(addr - addr_1 * 10)

        ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
        # time.sleep(0.001)
        result = int(ser.read())
        bits_received.append(result)
    return bits_received

def set_check_bits(ser, bit_index):
    for ii in (range(58, 69)):  # there are bit 58 to 68 for bit select
        addr = ii
        addr_1 = int(math.floor(addr / 10))
        addr_0 = int(addr - addr_1 * 10)

        ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
        # time.sleep(0.001)
        result = int(ser.read())
        if(result == 1 and (ii-58) != bit_index):
            addr = ii
            addr_1 = int(math.floor(addr / 10))
            addr_0 = int(addr - addr_1 * 10)
            ser.write(bytearray([49, 48 + addr_1, 48 + addr_0, 0]))
            time.sleep(0.001)  # must have this minimum sleep, other wise FSM could get stuck
            # print('[getting]', result, 'from address', addr)

    addr = bit_index+58
    addr_1 = int(math.floor(addr / 10))
    addr_0 = int(addr - addr_1 * 10)
    ser.write(bytearray([49, 48 + addr_1, 48 + addr_0, 1]))
    time.sleep(0.001)  # must have this minimum sleep, other wise FSM could get stuck

    # verify
    bits_received = get_check_bits(ser)
    print('Bit select [10:0] set to', list(reversed(bits_received)),'i.e. ',bits_received.index(1),'is being checked')


def get_delay(ser, dac_or_data, r_or_l, stage=0):
    offset = 0
    bit_len = 12
    if dac_or_data == 'dac' and r_or_l == 'l':
        offset = 24
    if dac_or_data == 'dac' and r_or_l == 'r':
        offset = 41
    if dac_or_data == 'data' and r_or_l == 'r':
        offset = 12
    stage_string = ''
    if stage > 0:
        stage_string = 'stage[' + str(stage) + ']'
        if stage == 2:
            bit_len = 5
        elif stage == 1:
            offset += 5

    bits_received = []
    for count in (range(offset, offset+bit_len)):  # there are bit 0 to 57 for delay param
        addr = count
        addr_1 = int(math.floor(addr / 10))
        addr_0 = int(addr - addr_1 * 10)

        ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
        # time.sleep(0.001)
        result = int(ser.read())
        # print('[getting]', result, 'from address', addr)
        bits_received.append(result)
        # time.sleep(0.001)
    delay_bits = []
    delay_dec_one_hot = 0
    for ii in reversed(range(0, bit_len)):
        delay_bits.append(bits_received[ii])
        delay_dec_one_hot = delay_dec_one_hot + int(bits_received[ii]) * (ii)
    print('delay of', dac_or_data, r_or_l, 'side', stage_string,
          'is',delay_dec_one_hot,' == (one hot):', delay_bits)
    return delay_bits, delay_dec_one_hot


# helper
def set_delay(ser, dac_or_data, r_or_l, stage=0, delay_val=1):
    offset = 0
    bit_len = 12
    if dac_or_data == 'dac' and r_or_l == 'l':
        offset = 24
    if dac_or_data == 'dac' and r_or_l == 'r':
        offset = 41
    if dac_or_data == 'data' and r_or_l == 'r':
        offset = 12
    stage_string = ''
    if stage > 0:
        stage_string = 'stage[' + str(stage) + ']'
        if stage == 2:
            bit_len = 5
        elif stage == 1:
            offset += 5
    if(delay_val >= bit_len):
        print("error: cannot set one-hot delay beyond",bit_len-1)
        return
    bit_send = []
    # one-hot convert
    for ii in range(0, bit_len):
        # bit_send.append(int(delay_val % 2))
        # delay_val = int(delay_val / 2)
        bit_send.append(0 if ii != delay_val else 1)
    print('setting delay of', dac_or_data, r_or_l, 'side', stage_string,
          'to:', list(reversed(bit_send)))

    # send
    for ii in (range(0 + offset, bit_len + offset)):
        addr = ii
        addr_1 = int(math.floor(addr / 10))
        addr_0 = int(addr - addr_1 * 10)
        ser.write(bytearray([49, 48 + addr_1, 48 + addr_0, bit_send[ii - offset]]))
        time.sleep(0.001) # must have this minimum sleep, other wise FSM could get stuck
    # print('delay bits sent to addr offset from', offset)
    time.sleep(0.1)

    bits_received = []
    # verify
    print('Verifying delay setting...')
    get_delay(ser, dac_or_data, r_or_l, stage)

def dump(ser, bool_print=1):
    bits_received = []
    for count in range(100):  # there are bit 0 to 87
        addr = count
        addr_1 = int(math.floor(addr / 10))
        addr_0 = int(addr - addr_1 * 10)

        ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
        time.sleep(0.01)
        result = int(ser.read())
        if bool_print:
            print('[getting]', result, 'from address', addr)
        bits_received.append(result)
        time.sleep(0.01)
    return bits_received


def info(ser):
    bits_received = dump(ser, 0)
    addr_bits = []
    addr_dec = 0
    for i in reversed(range(88, 95)):
        addr_bits.append(bits_received[i])
        addr_dec = addr_dec + int(bits_received[i]) * (2 ** (i - 88))
    scan_out_buffed = bits_received[97]
    # scan address
    print('scan_addr is:', addr_bits, 'or decimal:', addr_dec)

    # scan-out bit
    print('scan_out_buffed is:', scan_out_buffed)

    # CLK delayline (unfortunately, no data delayline direcltly controllable from scan)
    for part in ['data', 'dac']:
        for side in ['r', 'l']:
            for stage in [1, 2]:
                if part == 'data':
                    stage = 0
                    get_delay(ser, part, side, 0)
                    break
                get_delay(ser, part, side, stage)

    # data latch read-out (right before feeding into DAC)
    _bits_received = get_check_bits(ser)
    print('Bit select [10:0] set to', list(reversed(_bits_received)), 'i.e. ', _bits_received.index(1),
          'is being checked')

    # CDR circuit reset status
    _reset = bits_received[69]
    print('CDR reset bit is', _reset)

    # IF filter coeff
    _bits = []
    _bits_dec = 0
    for i in reversed(range(70, 73)):
        _bits.append(bits_received[i])
        _bits_dec = _bits_dec + int(bits_received[i]) * (2 ** (i - 70))
    print('IF filter coeff is:', _bits, 'or decimal:', _bits_dec)

    # Filter Swing Control
    _bits = []
    _bits_dec = 0
    for i in reversed(range(73, 76)):
        _bits.append(bits_received[i])
        _bits_dec = _bits_dec + int(bits_received[i]) * (2 ** (i - 73))
    print('IF filter swing L is:', _bits, 'or decimal:', _bits_dec)

    _bits = []
    _bits_dec = 0
    for i in reversed(range(76, 79)):
        _bits.append(bits_received[i])
        _bits_dec = _bits_dec + int(bits_received[i]) * (2 ** (i - 76))
    print('IF filter swing R is:', _bits, 'or decimal:', _bits_dec)

    # CMFB enable
    _CMFB_en = bits_received[79]
    print('CMFB enable bit is', _CMFB_en)

    # Band selection
    _Band = bits_received[80]
    print(('Upper' if _Band==1 else 'Lower'), 'Band is selected')

    # CMFB enable
    _IF_Bypass = bits_received[81]
    print('IF bypass enable bit is', _IF_Bypass)







##Windows
if os.name == 'nt':
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = 'COM6'  # CHANGE THIS COM PORT
    ser.open()
else:
    ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 115200

# input("Open a serial program in another terminal, then hit Enter")

if len(sys.argv) == 2:
    # file writing mode
    # there should be a file that contains up to 128 scan bit
    # with open(sys.argv[1], "r") as f:
    #    program = f.readlines()
    # if ('@' in program[0]):
    #    program = program[1:] # remove first line '@0'
    # program = [inst.rstrip() for inst in program]
    # size = len(program)*4 # in bytes
    file = open(sys.argv[1], 'r', encoding='utf-8')
    csv_reader = csv.reader(file)
    bits = []
    count = 0
    for row in csv_reader:
        # print(row)
        bits.append([count, int(row[1])])
        count += 1
    # print(rows)

    for count in range(88):  # there are bit 0 to 87
        addr = bits[count][0]
        addr_1 = int(math.floor(addr / 10))
        addr_0 = int(addr - addr_1 * 10)
        print('[sending ASCII]', bits[count][1], 'to address', addr, ':', 49, 48 + addr_1, 48 + addr_0, bits[count][1])
        ser.write(bytearray([49, 48 + addr_1, 48 + addr_0, bits[count][1]]))
        time.sleep(0.01)

    print('Verifying...')
    err_count = 0
    for count in range(88):  # there are bit 0 to 87
        addr = bits[count][0]
        addr_1 = int(math.floor(addr / 10))
        addr_0 = int(addr - addr_1 * 10)

        ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
        time.sleep(0.01)
        result = int(ser.read())
        print('[getting]', result, 'from address', addr)
        time.sleep(0.01)
        if (result != bits[count][1]):
            err_count += 1

    print("Verification done! Total error is", err_count)
    exit()

elif len(sys.argv) == 1:
    quit_flag = 0
    while (quit_flag == 0):
        task = input('\n\n>> usage:<w/r> <addr> <bit>, or dump to read all, for example, '
                     'to write 1 into addr<8>, type w 8 1, or type q to quit\r\n')
        task = task.split()
        if (task == []):
            continue
        elif (task[0] == 'w'):
            if (len(task) != 3):
                print(">> error: usage:<w> <addr> <bit>")
                continue
            addr = int(task[1])
            if (addr >= 100):
                print(">> error: scan address must be within 0 to 99.\r\n")
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
        elif (task[0] == 'r'):
            if (len(task) != 2):
                print(">> error: usage:<r> <addr>")
                continue
            addr = int(task[1])
            if (addr >= 100):
                print(">> error: scan address must be within 0 to 99.\r\n")
                continue
            addr_1 = int(math.floor(addr / 10))
            addr_0 = int(addr - addr_1 * 10)

            ser.write(bytearray([48, 48 + addr_1, 48 + addr_0]))
            time.sleep(0.01)
            result = int(ser.read())
            print('[getting]', result, 'from address', addr)
            time.sleep(0.01)
        elif task[0] == 'dump':
            print("Dumping the scan chain bits...\n")
            dump(ser,1)
        elif task[0] =='info':
            print("Reading the scan chain bits...\n")
            info(ser)
        elif task[0] == 'getdelay' or task[0] == 'get_delay':
            if (len(task) == 3):
                if (task[1] == 'dac'):
                    print(">> error: delay usage:getdelay <dac/data> <r/l> <#stage if arg[1] is dac>")
                    continue
                get_delay(ser, 'data', task[2])
            elif (len(task) == 4):
                if (task[1] == 'data'):
                    print(">> error: delay usage:getdelay <dac/data> <r/l> <#stage if arg[1] is dac>")
                    continue
                get_delay(ser, 'dac', task[2], int(task[3]))
            else:
                print(">> error: delay usage:getdelay <dac/data> <r/l> <#stage if arg[1] is dac>")
                continue
        elif task[0] == 'setdelay' or task[0] == 'set_delay':
            if (len(task) == 4):
                if (task[1] == 'dac'):
                    print(">> error: delay usage:setdelay <dac/data> <r/l> <#stage if arg[1] is dac> <val> ")
                    continue
                set_delay(ser, 'data', task[2], 0, int(task[3]))
            elif (len(task) == 5):
                if (task[1] == 'data'):
                    print(">> error: delay usage:setdelay <dac/data> <r/l> <#stage if arg[1] is dac> <val> ")
                    continue
                set_delay(ser, 'dac', task[2], int(task[3]), int(task[4]))
        elif task[0] == 'check_bit' or task[0] == 'checkbit':
            if(int(task[1])<0 or int(task[1])>10):
                print("error, can check bit[0:9], and 10 is to ground this output pin!")
                continue
            set_check_bits(ser, int(task[1]))
        elif task[0] == 'q':
            quit_flag = 1
        else:
            print(">> error: usage:<w/r> <addr> <bit>")

print(">>Done")
