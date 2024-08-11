"""
    Scan Chain creation and streaming script
    Created by: Yikuan Chen
    First version created on Feb 26 2024
"""

import csv

config_LO_MID_TX = {
    'scan_address': 30,
    'domain': 'LO_MID_TX',
    'channels': 1,
    'chain size': 30,
    'chain direction': 'in'
}

config_LO_IQ_RX = {
    'scan_address': 36,
    'domain': 'LO_IQ_RX',
    'channels': 1,
    'chain size': 36,
    'chain direction': 'in'
}

config_LO_IQ_TX = {
    'scan_address': 24,
    'domain': 'LO_IQ_TX',
    'channels': 1,
    'chain size': 24,
    'chain direction': 'in'
}

config_LO_FIRST = {
    'scan_address': 38,
    'domain': 'LO_FIRST',
    'channels': 1,
    'chain size': 38,
    'chain direction': 'in'
}

config_LO_SECOND = {
    'scan_address': 38,
    'domain': 'LO_SECOND',
    'channels': 1,
    'chain size': 38,
    'chain direction': 'in'
}

config_LO_MID_RX = {
    'scan_address': 30,
    'domain': 'LO_MID_RX',
    'channels': 1,
    'chain size': 30,
    'chain direction': 'in'
}

config_IREF = {
    'scan_address': 2,
    'domain': 'IREF',
    'channels': 1,
    'chain size': 2,
    'chain direction': 'in'
}

config_LO_IQ_VM = {
    'scan_address': 24,
    'domain': 'LO_IQ_VM',
    'channels': 1,
    'chain size': 24,
    'chain direction': 'in'
}

config_VM = {
    'scan_address': 148,
    'domain': 'VM',
    'channels': 1,
    'chain size': 148,
    'chain direction': 'in'
}

config_RX = {
    'scan_address': 79,
    'domain': 'RX',
    'channels': 1,
    'chain size': 79,
    'chain direction': 'in'
}

config_TX = {
    'scan_address': 148,
    'domain': 'TX',
    'channels': 1,
    'chain size': 148,
    'chain direction': 'in'
}

curr_msb = 0

# temporary
config = config_LO_MID_TX


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
        global config
        self.domain = config['domain']
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
        bit_list.append([name + '[' + str(((width - i - 1) if msb_first else i)) + ']', bits[i]])
    return bit_list


def reverse_bits(bits):
    return int(bits[::-1], 2)


# write the scan chain to csv format
curr_msb = 596

SCAN_LIST = []
# LO_MID_TX
config = config_LO_MID_TX
# SCAN_LIST.append(ScanBit('LO_MID_TX', 30, 0))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_QH_GM_BOT_L_BOT', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_QH_GM_BOT_L_TOP', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_THIRD_SPLIT_GM_BOT_L', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_DOUBLER_BOT_L', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_DOUBLER_PREDRIVER_BOT_L', 6, 0b001000))

# LO_IQ_RX
config = config_LO_IQ_RX
# SCAN_LIST.append(ScanBit('LO_IQ_RX', 36, 0))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF3_Q_GM_RX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF3_I_GM_RX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF2_Q_GM_RX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF2_I_GM_RX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF1_Q_GM_RX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF1_I_GM_RX0', 6, 0b001000))

# LO_IQ_TX
config = config_LO_IQ_TX
# SCAN_LIST.append(ScanBit('LO_IQ_TX', 24, 0))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF2_Q_GM_TX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF2_I_GM_TX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF1_Q_GM_TX0', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF1_I_GM_TX0', 6, 0b001000))

# LO_FIRST
config = config_LO_FIRST
# SCAN_LIST.append(ScanBit('LO_FIRST', 38, 0))
SCAN_LIST.append(ScanBit('LO_FIRST_ILO_CS_BUF_EN', 1, 0b1))
SCAN_LIST.append(ScanBit('LO_FIRST_VCM_ILO_CS', 6, 0b100000))
SCAN_LIST.append(ScanBit('LO_FIRST_ILO_INJ_BUF_EN', 1, 0b1))
SCAN_LIST.append(ScanBit('LO_FIRST_VCM_ILO_INJ', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_FIRST_IB_SECOND_SPLIT_RX_GM', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_FIRST_IB_SECOND_SPLIT_TX_GM', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_FIRST_IB_FIRST_SPLIT_GM', 6, 0b010000))
SCAN_LIST.append(ScanBit('LO_FIRST_IB_ILO_DRIVER', 6, 0b010000))

# LO_SECOND
config = config_LO_SECOND
# SCAN_LIST.append(ScanBit('LO_SECOND', 38, 0))
SCAN_LIST.append(ScanBit('LO_SECOND_ILO_CS_BUF_EN', 1, 0b1))
SCAN_LIST.append(ScanBit('LO_SECOND_VCM_ILO_CS', 6, 0b100000))
SCAN_LIST.append(ScanBit('LO_SECOND_ILO_INJ_BUF_EN', 1, 0b1))
SCAN_LIST.append(ScanBit('LO_SECOND_VCM_ILO_INJ', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_SECOND_IB_SECOND_SPLIT_RX_GM', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_SECOND_IB_SECOND_SPLIT_TX_GM', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_SECOND_IB_FIRST_SPLIT_GM', 6, 0b010000))
SCAN_LIST.append(ScanBit('LO_SECOND_IB_ILO_DRIVER', 6, 0b010000))

# LO_MID_RX
config = config_LO_MID_RX
# SCAN_LIST.append(ScanBit('LO_MID_RX', 30, 0))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_QH_GM_TOP_L_BOT', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_QH_GM_TOP_L_TOP', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_THIRD_SPLIT_GM_TOP_L', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_DOUBLER_TOP_L', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_DOUBLER_PREDRIVER_TOP_L', 6, 0b001000))

# IREF
config = config_IREF
SCAN_LIST.append(ScanBit('IREF', 2, 0b00))

# LO_IQ_VM
config = config_LO_IQ_VM
# SCAN_LIST.append(ScanBit('LO_IQ_VM', 24, 0))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF2_Q_GM_TX1', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF2_I_GM_TX1', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF1_Q_GM_TX1', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF1_I_GM_TX1', 6, 0b001000))

# Meng implemented the I-Q scan codes to be symmetrical, since she flips the I-scan code orders in her layout
config = config_VM
SCAN_LIST.append(ScanBit('VM_IB_CMIN_CTRL_I', 6, 0b000111))
SCAN_LIST.append(ScanBit('VM_IB_AMP2_CTRL_I', 6, 0b010110))
SCAN_LIST.append(ScanBit('VM_IB_VCM_REF_CTRL_I', 6, 0b010001))
SCAN_LIST.append(ScanBit('VM_IB_PA_S1_CTRL_I', 6, 0b100000, comment='621mV'))
SCAN_LIST.append(ScanBit('VM_IB_PA_S2_CTRL_I', 6, 0b110000, comment='505mV'))
SCAN_LIST.append(ScanBit('VM_IB_PA_S3_CTRL_I', 6, 0b100000, comment='606mV'))
SCAN_LIST.append(ScanBit('VM_IB_CMFB_EN_IE', 2, 0b10))
SCAN_LIST.append(ScanBit('VM_IDCOC_EN_IE', 3, 0b001))
SCAN_LIST.append(ScanBit('VM_CMFB_EN_IE', 1, 0b1))
SCAN_LIST.append(ScanBit('VM_DCOC_SN_IE', 1, 0b0))
SCAN_LIST.append(ScanBit('VM_DCOC_SP_IE', 1, 0b0))
SCAN_LIST.append(ScanBit('VM_VOLT_CTRL_IE', 32, 0b00111000110000001010000010011111))
SCAN_LIST.append(ScanBit('VM_VOLT_CTRL_QE', 32, 0b11111001000001010000001100011100, msb_first=False))
SCAN_LIST.append(ScanBit('VM_DCOC_SP_QE', 1, 0b0, msb_first=False))
SCAN_LIST.append(ScanBit('VM_DCOC_SN_QE', 1, 0b0, msb_first=False))
SCAN_LIST.append(ScanBit('VM_CMFB_EN_QE', 1, 0b1, msb_first=False))
SCAN_LIST.append(ScanBit('VM_IDCOC_EN_QE', 3, 0b100, msb_first=False))
SCAN_LIST.append(ScanBit('VM_IB_CMFB_EN_QE', 2, 0b01, msb_first=False))
SCAN_LIST.append(ScanBit('VM_IB_VCM_REF_CTRL_Q', 6, 0b100010, msb_first=False))
SCAN_LIST.append(ScanBit('VM_IB_AMP2_CTRL_Q', 6, 0b011010, msb_first=False))
SCAN_LIST.append(ScanBit('VM_IB_CMIN_CTRL_Q', 6, 0b111000, msb_first=False))
SCAN_LIST.append(ScanBit('VM_DCOC_CTRL_I', 7, 0b0000000, msb_first=False))
SCAN_LIST.append(ScanBit('VM_DCOC_CTRL_Q', 7, 0b0000000, msb_first=False))

# RX
config = config_RX
# SCAN_LIST.append(ScanBit('RX', 79, 0))
SCAN_LIST.append(ScanBit('Dummy', 13, 0b0000000000000))
SCAN_LIST.append(ScanBit('IB_RFAMP_I_0', 4, 0b0100))
SCAN_LIST.append(ScanBit('IB_RFAMP_Q_0', 4, 0b0100))
SCAN_LIST.append(ScanBit('VB_MIXER_Q_0', 6, 0b001000))
SCAN_LIST.append(ScanBit('VB_FC_Q_0', 6, 0b001000))
SCAN_LIST.append(ScanBit('VB_GC_Q_0', 6, 0b001000))
SCAN_LIST.append(ScanBit('IB_BBAMP_0', 6, 0b000110))
SCAN_LIST.append(ScanBit('IB_RFAMP1_0', 4, 0b0100))
SCAN_LIST.append(ScanBit('IB_RFAMP2_0', 4, 0b0100))
SCAN_LIST.append(ScanBit('VB_GC_I_0', 6, 0b000100))
SCAN_LIST.append(ScanBit('VB_FC_I_0', 6, 0b000100))
SCAN_LIST.append(ScanBit('VB_MIXER_I_0', 6, 0b000100))
SCAN_LIST.append(ScanBit('IB_CS_0', 4, 0b0100))
SCAN_LIST.append(ScanBit('IB_CG_0', 4, 0b0100))

# TX
# Meng implemented the I-Q scan codes to be symmetrical, since she flips the I-scan code orders in her layout
config = config_TX
SCAN_LIST.append(ScanBit('TX_IB_CMIN_CTRL_I', 6, 0b000111))
SCAN_LIST.append(ScanBit('TX_IB_AMP2_CTRL_I', 6, 0b010110))
SCAN_LIST.append(ScanBit('TX_IB_VCM_REF_CTRL_I', 6, 0b010001))
SCAN_LIST.append(ScanBit('TX_IB_PA_S1_CTRL_I', 6, 0b100000, comment='621mV'))
SCAN_LIST.append(ScanBit('TX_IB_PA_S2_CTRL_I', 6, 0b110000, comment='505mV'))
SCAN_LIST.append(ScanBit('TX_IB_PA_S3_CTRL_I', 6, 0b100000, comment='606mV'))
SCAN_LIST.append(ScanBit('TX_IB_CMFB_EN_IE', 2, 0b10))
SCAN_LIST.append(ScanBit('TX_IDCOC_EN_IE', 3, 0b001))
SCAN_LIST.append(ScanBit('TX_CMFB_EN_IE', 1, 0b1))
SCAN_LIST.append(ScanBit('TX_DCOC_SN_IE', 1, 0b0))
SCAN_LIST.append(ScanBit('TX_DCOC_SP_IE', 1, 0b0))
SCAN_LIST.append(ScanBit('TX_VOLT_CTRL_IE', 32, 0b00111000110000001010000010011111))
SCAN_LIST.append(ScanBit('TX_VOLT_CTRL_QE', 32, 0b11111001000001010000001100011100, msb_first=False))
SCAN_LIST.append(ScanBit('TX_DCOC_SP_QE', 1, 0b0, msb_first=False))
SCAN_LIST.append(ScanBit('TX_DCOC_SN_QE', 1, 0b0, msb_first=False))
SCAN_LIST.append(ScanBit('TX_CMFB_EN_QE', 1, 0b1, msb_first=False))
SCAN_LIST.append(ScanBit('TX_IDCOC_EN_QE', 3, 0b100, msb_first=False))
SCAN_LIST.append(ScanBit('TX_IB_CMFB_EN_QE', 2, 0b01, msb_first=False))
SCAN_LIST.append(ScanBit('TX_IB_VCM_REF_CTRL_Q', 6, 0b100010, msb_first=False))
SCAN_LIST.append(ScanBit('TX_IB_AMP2_CTRL_Q', 6, 0b011010, msb_first=False))
SCAN_LIST.append(ScanBit('TX_IB_CMIN_CTRL_Q', 6, 0b111000, msb_first=False))
SCAN_LIST.append(ScanBit('TX_DCOC_CTRL_I', 7, 0b0000000, msb_first=False))
SCAN_LIST.append(ScanBit('TX_DCOC_CTRL_Q', 7, 0b0000000, msb_first=False))

csv_name = 'Full_Scan_bits.csv'
with open(csv_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    # for key in config:
    #     csv_writer.writerow([key, config[key]])
    csv_writer.writerow(['LSB_Index',
                         'Domain',
                         'Signal_Name',
                         'Bit_Width',
                         'Decimal_Value',
                         'Bits',
                         'Comment'])

    for scan in SCAN_LIST:
        csv_writer.writerow([scan.lsb_index,
                             scan.domain,
                             scan.signal_name,
                             scan.bit_width,
                             scan.value,
                             scan.bits_string,
                             scan.comment])

# exit()

# turn the scan chain into unfolded 1-bit array
csv_name = 'Full_Scan_bits_unfolded.csv'
curr_index = 596
with open(csv_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(['Scan_Index',
                         'Domain',
                         'Bit_Name',
                         'Bit',
                         'Comment'])

    curr_index = 596
    for scan in SCAN_LIST:
        unfolded_list = unfold_bits(scan.signal_name, scan.bit_width, scan.msb_first, scan.bits_string)
        for row in unfolded_list:
            csv_writer.writerow([curr_index, scan.domain, row[0], row[1], scan.comment])
            curr_index -= 1
