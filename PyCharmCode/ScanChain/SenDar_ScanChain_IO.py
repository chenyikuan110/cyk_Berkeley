# Created by Yikuan Chen
# serial write part modified from code provided by Rami Hijab

import textwrap
import serial
import time
import numpy as np
import csv

port = 'COM5'  # COM9 for arduino uno, COM5 for arduino due
baudrate = 9600
scanchain_size = 648
scan_data_size = 597

# Arduino Command (Serial)
CMD_WRITE = b'ascwrite\n'
CMD_LOAD = b'ascload\n'
CMD_READ = b'ascread\n'
MSG_WRITE = 'Executing ASC Write'
MSG_WRITE_ERROR = 'Error in the ASC Write'
MSG_WRITE_COMPLETE = 'ASC Write Complete'
MSG_LOAD = 'Executing ASC Load'

csv_name = 'Full_Scan_bits_newTX_unfolded.csv'


class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


config_FULL = {
    'scan_address': 647,
    'domain': 'FULL',
    'channels': 1,
    'chain size': 647,
    'chain direction': 'in'
}

config = config_FULL
curr_msb = 0


class ScanBit:
    def __init__(self, signal_name, bit_width, bits, off_bits=0, msb_first=True, comment=''):
        """
        Custom type representing a scan bit.

        Args:
            signal_name (str): Name of the signal.
            bit_width (int): Width of the bit field.
            lsb_index (int): Index of the least significant bit (LSB).
            bits (int): Actual value of the bit field.
        """
        global config
        self.domain = config['domain']
        self.msb_first = msb_first
        self.signal_name = signal_name
        self.bit_width = bit_width
        global curr_msb
        self.lsb_index = curr_msb - bit_width + 1
        self.value = bits
        self.default_val = bits  # one-time set
        self.off_bits = off_bits # some bits are active low
        self.bits_string = '{:0{width}b}'.format(bits, width=bit_width)
        self.off_bits_string = '{:0{width}b}'.format(off_bits, width=bit_width)
        self.comment = comment
        curr_msb -= bit_width

    def set_val(self, val):
        self.value = val
        bits_string = '{:0{width}b}'.format(val, width=self.bit_width)
        self.bits_string = bits_string  # if self.msb_first else bits_string[::-1]

    def get_val(self):
        return self.value

    def get_def_val(self):
        return self.default_val

    def set_off_val(self, off_val):
        self.off_bits = off_val
        self.off_bits_string = '{:0{width}b}'.format(off_val, width=self.bit_width)


def print_msg(msg):
    if 'Error' in msg:
        print(bcolors.WARNING + msg + bcolors.ENDC)
    else:
        print(bcolors.OKGREEN + msg + bcolors.ENDC)


def error_msg(msg):
    print(bcolors.WARNING + msg + bcolors.ENDC)


# Read the entire serial buffer (msg from Arduino)
def read_buffer(s):
    # tdata = s.read() # set a blocking read
    time.sleep(0.05)
    size = s.in_waiting
    msg = s.read(size)
    # msg = tdata+msg
    print('>> reading ' + str(len(msg.decode('utf-8').rstrip('\r\n'))) + " bytes from Serial buffer...")
    return msg.decode('utf-8').rstrip('\r\n')


def unfold_bits(width, bits):
    bit_list = []
    for i in range(width):
        bit_list.append(int(bits[i]))
    return bit_list


# turn csv into ScanBit data struct
def csv_to_ScanBit(reader_obj):
    scan_count = 0
    # scan_buffer = []
    SCAN_LIST = []
    var_name = ''
    bits = []
    off_bits = []
    count = 0

    # Send string to uC and program into IC
    print("\nStarting Write to Scan Buffer...\n")

    curr_bit_index = 0
    recorded_bit_index = 0
    for row in list(reader_obj):
        msb_first = True
        temp = row[2].split('[')

        if temp[0] == 'Bit_Name':
            continue  # skipping the header row

        curr_bit_index = int(temp[1].split(']')[0])
        if var_name != temp[0]:  # new var name
            if bits != []:  # wrap up the previous loaded bit group
                if recorded_bit_index > 0:
                    msb_first = False
                val = 0
                off_val = 0
                # print(var_name, bits, count)
                for i in range(count):
                    # print(i, bits[i], 2**(count-i-1))
                    val += bits[i] * (2 ** (count - i - 1))
                    off_val += off_bits[i] * (2 ** (count - i - 1))
                # print(var_name, count, val, '{:0{width}b}'.format(val, width=count))
                # SCAN_LIST.append(ScanBit('DCOC_SN_QE', 1, 0b0))
                SCAN_LIST.append(ScanBit(var_name, count, int(val), off_bits=int(off_val), msb_first=msb_first))
                print(f'Wrote to buffer \'{var_name: >35}[{count-recorded_bit_index -1}:{recorded_bit_index}]\' with 0b{val:>0{count}b},'
                      f' Unsigned Decimal Val = {val},'
                      f' Off value Decimal = {off_val}, '
                      f' msb_first={1 if msb_first else 0}.')

            var_name = temp[0]  # get the name of the new bit group

            count = 0
            bits = []
            off_bits = []

        recorded_bit_index = curr_bit_index
        # append the new bit
        bits.append(int(row[3]))
        off_bits.append(int(row[4]))
        scan_count += 1
        count += 1

    # wrap up the last one
    msb_first = True
    if bits != []:
        if recorded_bit_index > 0:
            msb_first = False
        val = 0
        off_val = 0
        # print(var_name, bits, count)
        for i in range(count):
            # print(i, bits[i], 2**(count-i-1))
            val += bits[i] * (2 ** (count - i - 1))
            off_val += off_bits[i] * (2 ** (count - i - 1))
        # print(var_name, count, val, '{:0{width}b}'.format(val, width=count))
        SCAN_LIST.append(ScanBit(var_name, count, int(val), off_bits=int(off_val), msb_first=msb_first))
        print(f'Wrote to buffer \'{var_name: >35}[{count - recorded_bit_index -1}:{recorded_bit_index}]\' with 0b{val:>0{count}b},'
              f' Unsigned Decimal Val = {val}, '
              f' Off value Decimal = {off_val}, '
              f'msb_first={1 if msb_first else 0}.')

    print('\nScan buffer preparation finished, ' + str(scan_count) + ' bits loaded.')
    # return scan_count, scan_buffer, SCAN_LIST
    return scan_count, SCAN_LIST


# write value
def scan_write(ser, scan_string):
    # actual scan write
    msg = ''
    while msg != MSG_WRITE_COMPLETE:
        while msg != MSG_WRITE:
            # print('inner loop MSG: ' + msg + '.')
            ser.write(CMD_WRITE)
            time.sleep(0.5)
            msg = read_buffer(ser)

        # print("got MSG \'"+ msg + "\', Writing...")
        time.sleep(0.5)
        ser.write(scan_string.encode('utf-8'))
        time.sleep(0.5)
        msg = read_buffer(ser)
        # print("MSG :" + msg)

    print_msg(msg)

    # Execute the load command to latch values inside chip
    print("Starting Load")
    ser.write(CMD_LOAD)
    # time.sleep(0.01)
    print_msg(read_buffer(ser))


# Read All Scan bits from chip
def scan_read(ser):
    # Read back the scan chain contents
    print("Starting Read")
    ser.write(CMD_READ)
    time.sleep(1)
    read_data = read_buffer(ser)
    return read_data


# Format the array of ScanBit objects to a single scanbit string
def scan_format(scan_count, SCAN_LIST):
    scan_buffer = []
    for scan in reversed(list(SCAN_LIST)):
        unfolded_list = unfold_bits(scan.bit_width, scan.bits_string)
        for bit_array in reversed(list(unfolded_list)):
            scan_buffer.append(bit_array)
    padding_zeros = [0 for n in range(scanchain_size - scan_count)]
    scan_arr = np.array(scan_buffer)
    scan_arr = np.concatenate((scan_arr, padding_zeros))
    scan_arr = np.subtract(np.ones(scanchain_size), scan_arr)
    # scan_arr = [1 for n in range(scanchain_size)]
    # scan_arr[-1] = int(np.round(np.random.rand()))

    print(str(len(padding_zeros)) + ' padding 0 bits padded, total message size is '
          + str(len(scan_arr)) + ' bits, begin writing...\n')
    scan_string = "".join(map(lambda x: str(int(x)), scan_arr))
    return scan_string


# Write and Read
def scan_write_and_read(ser, scan_count, SCAN_LIST):
    scan_string = scan_format(scan_count, SCAN_LIST)

    # print(scan_string.encode('utf-8'))

    # Write
    scan_write(ser, scan_string)

    # Read
    read_data = scan_read(ser)

    if scan_string == read_data:
        print("SUCCESS: Read matches write")
        print_msg('[Expecting]:')
        print_msg(textwrap.fill(scan_string, width=100))
        print_msg('[Got]:')
        print_msg(textwrap.fill(read_data, width=100))
    else:
        error_msg("FAILURE: Read/write comparison incorrect")
        error_msg('[Expecting]:')
        error_msg(textwrap.fill(scan_string, width=100))
        error_msg('[Got]:')
        error_msg(textwrap.fill(read_data, width=100))

    print('\nEnd of Scan Write.')


# Open the CSV file in read mode
def scan_init():
    # ser.set_buffer_size(rx_size=2000, tx_size=2000)
    time.sleep(0.1)
    # load up the scan buffer
    with open(csv_name) as file_obj:
        reader_obj = csv.reader(file_obj)
        scan_count, SCAN_LIST = csv_to_ScanBit(reader_obj)

    return scan_count, SCAN_LIST


# Modify value in the scan chain
def modify_val(SCAN_LIST, signal_name, val):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        found_object.set_val(val)
        bit_index = f'{signal_name}[{found_object.bit_width - 1}:{0}]' if found_object.msb_first \
            else f'{signal_name}[{0}:{found_object.bit_width - 1}]'
        print(f'Updated value for {bit_index: >35} = {found_object.value: >15}, bit = {found_object.bits_string}')
        # print(f"Updated value for {signal_name}: {found_object.value}")
    else:
        print(f"No object found with name '{signal_name}'")


# set scan chain values to off_bits
def turn_off(SCAN_LIST, signal_name):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        found_object.set_val(found_object.off_bits)
        bit_index = f'{signal_name}[{found_object.bit_width - 1}:{0}]' if found_object.msb_first \
            else f'{signal_name}[{0}:{found_object.bit_width - 1}]'
        print(f'Updated value for {bit_index: >35} = {found_object.value: >15}, bit = {found_object.bits_string}')
    else:
        print(f"No object found with name '{signal_name}'")


def fetch_val(SCAN_LIST, signal_name):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        val = found_object.get_val()
        print(f"Stored value for {signal_name}: {val}")
        return val, found_object.msb_first
    else:
        print(f"No object found with name '{signal_name}'")
        return 0xDEADBEEF,


def fetch_def_val(SCAN_LIST, signal_name):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        def_val = found_object.get_def_val()
        print(f"Stored def value for {signal_name}: {def_val}")
        return def_val, found_object.msb_first
    else:
        print(f"No object found with name '{signal_name}'")
        return 0xDEADBEEF, 0xDEADBEEF


# Main
if __name__ == "__main__":
    curr_msb = scan_data_size-1
    with serial.Serial(port, baudrate=baudrate, timeout=None) as my_ser:
        my_scan_count, my_SCAN_LIST = scan_init()
        scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)

        # target_name = 'TX_DCOC_CTRL_Q'
        # old_val = fetch_val(my_SCAN_LIST, target_name)
        # new_value = 0b0011111
        #
        # # modify the scan chain value and re-write the chain
        # modify_val(my_SCAN_LIST, target_name, new_value)
        #
        # old_val = fetch_val(my_SCAN_LIST, target_name)
        # scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
        stop_flag = False
        while stop_flag == False:
            task = input("Enter Command:\n")
            task = task.split()
            if len(task)<1:
                continue
            if task[0] == 'q':
                stop_flag = True
            if task[0] == 'reset':
                my_scan_count, my_SCAN_LIST = scan_init()
                scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'step':
                for scans in my_SCAN_LIST:
                    cmd_name = scans.signal_name
                    modify_val(my_SCAN_LIST, cmd_name, 0)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'zz': # turn off, set to nominal vals
                for scans in my_SCAN_LIST:
                    cmd_name = scans.signal_name
                    # modify_val(my_SCAN_LIST, cmd_name, 0)
                    turn_off(my_SCAN_LIST, cmd_name)
                scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'zero':
                scan_arr = [0 for n in range(scanchain_size)]
                scan_arr = np.subtract(np.ones(scanchain_size), scan_arr)
                print('Writing all zeros to the scanchain\n')
                scan_string = "".join(map(lambda x: str(int(x)), scan_arr))
                scan_write(my_ser, scan_string)
            if task[0] == 'ones':
                scan_arr = [1 for n in range(scanchain_size)]
                scan_arr = np.subtract(np.ones(scanchain_size), scan_arr)
                print('Writing all ones to the scanchain\n')
                scan_string = "".join(map(lambda x: str(int(x)), scan_arr))
                scan_write(my_ser, scan_string)
            if task[0] == 'set':
                if len(task) != 3:
                    continue
                cmd_name = task[1]
                if task[2] == 'def':
                    val, msb_first = fetch_def_val(my_SCAN_LIST, cmd_name)
                elif task[2] == 'off':
                    turn_off(my_SCAN_LIST, cmd_name)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
                    continue
                else:
                    val = task[2]
                old_val, msb_first = fetch_val(my_SCAN_LIST, cmd_name)
                print(f'Value for {cmd_name} is {old_val}, msb_first = {msb_first}')
                modify_val(my_SCAN_LIST, cmd_name, int(val))
                new_val, msb_first = fetch_val(my_SCAN_LIST, cmd_name)
                print(f'Value for {cmd_name} is {new_val}, msb_first = {msb_first}')
                scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'get':
                cmd_name = task[1]
                val, msb_first = fetch_val(my_SCAN_LIST, cmd_name)
                print(f'Value for {cmd_name} is {val}, msb_first = {msb_first}')
            if task[0] == 'LO' or task[0] == 'RX' or task[0] == 'VM' or task[0] =='TX':
                if task[1] == 'on' or task[1] == 'off':
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:2] == task[0]:
                            modify_val(my_SCAN_LIST, cmd_name, scans.default_val if task[1] == 'on' else scans.off_bits)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
                elif task[1] == 'ls':
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:2] == task[0]:
                            bit_index = f'{cmd_name}[{scans.bit_width-1}:{0}]' if scans.msb_first \
                                else f'{cmd_name}[{0}:{scans.bit_width-1}]'
                            print(f'{bit_index: >35} = {scans.value: >15}, bit = {scans.bits_string}')
                elif task[1] == 'step':
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:2] == task[0]:
                            modify_val(my_SCAN_LIST, cmd_name, scans.off_bits)
                            scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'PA':
                if task[1] == 'on' or task[1] == 'off':
                    # TX_IB_PA
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:8] == 'TX_IB_PA':
                            modify_val(my_SCAN_LIST, cmd_name, scans.default_val if task[1] == 'on' else scans.off_bits)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'TX_DCOC':
                if task[1] == 'on' or task[1] == 'off':
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:9] == 'TX_DCOC_S':
                            modify_val(my_SCAN_LIST, cmd_name, 1 if task[1] == 'on' else scans.off_bits)
                        elif cmd_name[0:13] == 'TX_DCOC_CTRL_':
                            modify_val(my_SCAN_LIST, cmd_name, 32 if task[1] == 'on' else scans.off_bits)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'VM_DCOC':
                if task[1] == 'on' or task[1] == 'off':
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:9] == 'VM_DCOC_S':
                            modify_val(my_SCAN_LIST, cmd_name, 1 if task[1] == 'on' else scans.off_bits)
                        elif cmd_name[0:13] == 'VM_DCOC_CTRL_':
                            modify_val(my_SCAN_LIST, cmd_name, 32 if task[1] == 'on' else scans.off_bits)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
