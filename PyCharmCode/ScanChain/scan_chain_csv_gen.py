"""
    Scan Chain creation and streaming script
    Created by: Yikuan Chen
    First version created on Feb 26 2024
"""

import csv

config = {
    'scan_address': 148,
    'domain': 'TX',
    'channels': 2,
    'chain size': 148,
    'chain direction': 'in'
}

curr_msb = config['chain size'] - 1


# contains the metadata for a scan word
class ScanBit:
    def __init__(self, signal_name, bit_width, bits, msb_first=True, comment=''):
        """
        Custom type representing a scan bit.

        Args:
            signal_name (str): Name of the signal.
            bit_width (int): Width of the bit field.
            lsb_index (int): Index of the least significant bit (LSB).
            bits (int): Actual value of the bit field.
        """
        self.msb_first = msb_first
        self.signal_name = signal_name
        self.bit_width = bit_width
        global curr_msb
        self.lsb_index = curr_msb - bit_width + 1
        self.value = bits
        self.bits_string = '{:0{width}b}'.format(bits, width=bit_width)
        self.comment = comment
        curr_msb -= bit_width

    def set_val(self, val):
        self.value = val
        self.bits_string = '{:0{width}b}'.format(val, width=self.bit_width)

def unfold_bits(name, width, msb_first, bits):
    bit_list = []
    for i in range(width):
        bit_list.append([name + '[' + str(((width-i-1) if msb_first else i)) + ']', bits[i]])
    return bit_list


def reverse_bits(bits):
    return int(bits[::-1], 2)


# Meng implemented the I-Q scan codes to be symmetrical, since she flips the I-scan code orders in her layout
SCAN_LIST = []
#
# SCAN_LIST.append(ScanBit('DCOC_CTRL_Q', 7, 0b0000000))
# SCAN_LIST.append(ScanBit('DCOC_CTRL_I', 7, 0b0000000))
# SCAN_LIST.append(ScanBit('IB_CMIN_CTRL_Q', 6, 0b000111))
# SCAN_LIST.append(ScanBit('IB_AMP2_CTRL_Q', 6, 0b010110))
# SCAN_LIST.append(ScanBit('IB_VCM_REF_CTRL_Q', 6, 0b010001))
# SCAN_LIST.append(ScanBit('IB_CMFB_EN_QE', 2, 0b10))
# SCAN_LIST.append(ScanBit('IDCOC_EN_QE', 3, 0b001))
# SCAN_LIST.append(ScanBit('CMFB_EN_QE', 1, 0b1))
# SCAN_LIST.append(ScanBit('DCOC_SN_QE', 1, 0b0))
# SCAN_LIST.append(ScanBit('DCOC_SP_QE', 1, 0b0))
# SCAN_LIST.append(ScanBit('TX_VOLT_CTRL_QE', 32, 0b00111000110000001010000010011111))
# SCAN_LIST.append(ScanBit('TX_VOLT_CTRL_IE', 32, 0b11111001000001010000001100011100, msb_first=False))
# SCAN_LIST.append(ScanBit('DCOC_SP_IE', 1, 0b0, msb_first=False))
# SCAN_LIST.append(ScanBit('DCOC_SN_IE', 1, 0b0, msb_first=False))
# SCAN_LIST.append(ScanBit('CMFB_EN_IE', 1, 0b1, msb_first=False))
# SCAN_LIST.append(ScanBit('IDCOC_EN_IE', 3, 0b100, msb_first=False))
# SCAN_LIST.append(ScanBit('IB_CMFB_EN_IE', 2, 0b01, msb_first=False))
# SCAN_LIST.append(ScanBit('IB_PA_S3_CTRL_I', 6, 0b000011, msb_first=False, comment='606mV'))  # needs refine
# SCAN_LIST.append(ScanBit('IB_PA_S2_CTRL_I', 6, 0b000011, msb_first=False, comment='505mV'))  # needs refine
# SCAN_LIST.append(ScanBit('IB_PA_S1_CTRL_I', 6, 0b000001, msb_first=False, comment='621mV'))  # needs refine
# SCAN_LIST.append(ScanBit('IB_VCM_REF_CTRL_I', 6, 0b100010, msb_first=False))
# SCAN_LIST.append(ScanBit('IB_AMP2_CTRL_I', 6, 0b011010, msb_first=False))
# SCAN_LIST.append(ScanBit('IB_CMIN_CTRL_I', 6, 0b111000, msb_first=False))

SCAN_LIST.append(ScanBit('DCOC_CTRL_Q', 7, 0b1000000))
SCAN_LIST.append(ScanBit('DCOC_CTRL_I', 7, 0b0100000))
SCAN_LIST.append(ScanBit('IB_CMIN_CTRL_Q', 6, 0b000001))
SCAN_LIST.append(ScanBit('IB_AMP2_CTRL_Q', 6, 0b011101))
SCAN_LIST.append(ScanBit('IB_VCM_REF_CTRL_Q', 6, 0b011001))
SCAN_LIST.append(ScanBit('IB_CMFB_EN_QE', 2, 0b01))
SCAN_LIST.append(ScanBit('IDCOC_EN_QE', 3, 0b001))
SCAN_LIST.append(ScanBit('CMFB_EN_QE', 1, 0b1))
SCAN_LIST.append(ScanBit('DCOC_SN_QE', 1, 0b0))
SCAN_LIST.append(ScanBit('DCOC_SP_QE', 1, 0b0))
SCAN_LIST.append(ScanBit('TX_VOLT_CTRL_QE', 32, 0b01111011110110001000010011111111))
SCAN_LIST.append(ScanBit('TX_VOLT_CTRL_IE', 32, 0b11111111001000010001101111011110, msb_first=False))
SCAN_LIST.append(ScanBit('DCOC_SP_IE', 1, 0b1, msb_first=False))
SCAN_LIST.append(ScanBit('DCOC_SN_IE', 1, 0b0, msb_first=False))
SCAN_LIST.append(ScanBit('CMFB_EN_IE', 1, 0b1, msb_first=False))
SCAN_LIST.append(ScanBit('IDCOC_EN_IE', 3, 0b100, msb_first=False))
SCAN_LIST.append(ScanBit('IB_CMFB_EN_IE', 2, 0b01, msb_first=False))
SCAN_LIST.append(ScanBit('IB_PA_S3_CTRL_I', 6, 0b001010, msb_first=False))
SCAN_LIST.append(ScanBit('IB_PA_S2_CTRL_I', 6, 0b001010, msb_first=False))
SCAN_LIST.append(ScanBit('IB_PA_S1_CTRL_I', 6, 0b000001, msb_first=False))
SCAN_LIST.append(ScanBit('IB_VCM_REF_CTRL_I', 6, 0b100110, msb_first=False))
SCAN_LIST.append(ScanBit('IB_AMP2_CTRL_I', 6, 0b101110, msb_first=False))
SCAN_LIST.append(ScanBit('IB_CMIN_CTRL_I', 6, 0b100000, msb_first=False))

# write the scan chain to csv format
csv_name = 'Tx_Scan_bits_newTX.csv'
with open(csv_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    for key in config:
        csv_writer.writerow([key, config[key]])
    csv_writer.writerow(['LSB_Index',
                         'Signal_Name',
                         'Bit_Width',
                         'Decimal_Value',
                         'Bits',
                         'Comment'])
    for scan in SCAN_LIST:
        csv_writer.writerow([scan.lsb_index,
                             scan.signal_name,
                             scan.bit_width,
                             scan.value,
                             scan.bits_string,
                             scan.comment])

# turn the scan chain into unfolded 1-bit array
csv_name = 'Tx_Scan_bits_unfolded_newTX.csv'
curr_index = config['chain size'] - 1
with open(csv_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(['Scan_Index',
                         'Domain',
                         'Bit_Name',
                         'Bit',
                         'Comment'])
    for scan in SCAN_LIST:
        unfolded_list = unfold_bits(scan.signal_name, scan.bit_width, scan.msb_first, scan.bits_string)
        for row in unfolded_list:
            csv_writer.writerow([curr_index, config['domain'], row[0], row[1], scan.comment])
            curr_index -= 1
