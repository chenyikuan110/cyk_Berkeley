"""
    Scan Chain creation and streaming script
    Created by: Yikuan Chen
    First version created on Feb 26 2024
"""

import csv

curr_msb = 0

config_LO = {
    'scan_address': 60,
    'domain': 'LO',
    'channels': 1,
    'chain size': 60,
    'chain direction': 'in'
}

config_RX = {
    'scan_address': 240,
    'domain': 'RX',
    'channels': 1,
    'chain size': 240,
    'chain direction': 'in'
}

config_TX = {
    'scan_address': 240,
    'domain': 'TX',
    'channels': 1,
    'chain size': 240,
    'chain direction': 'in'
}

config_Padding = {
    'scan_address': 100,
    'domain': 'Padding',
    'channels': 1,
    'chain size': 100,
    'chain direction': 'in'
}

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


def unfold_bits(name, width, msb_first, bits):
    bit_list = []
    for i in range(width):
        bit_list.append([name + '[' + str(((width - i - 1) if msb_first else i)) + ']', bits[i]])
    return bit_list


def reverse_bits(bits):
    return int(bits[::-1], 2)


# write the scan chain to csv format
curr_msb = 639

SCAN_LIST = []

# TX
config = config_Padding
SCAN_LIST.append(ScanBit('extra_padding', 100, 0b0))

config = config_TX
SCAN_LIST.append(ScanBit('tx_padding', 18, 0b0))
SCAN_LIST.append(ScanBit('i_bias_tx_comm_amp_s3', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_comm_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_comm_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split1_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split1_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch3_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch3_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch4_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch4_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch1_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch1_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch2_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_split2_ch2_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_ch4_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_ch4_amp_s3', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch4_amp_s2', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch4_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('cntr_tx_ch4_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch4_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_tx_ch4_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch4_ps_q_p', 3, 0b000))
SCAN_LIST.append(ScanBit('i_bias_tx_ch3_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_ch3_amp_s3', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch3_amp_s2', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch3_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('cntr_tx_ch3_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch3_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_tx_ch3_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch3_ps_q_p', 3, 0b000))
SCAN_LIST.append(ScanBit('i_bias_tx_ch2_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_ch2_amp_s3', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch2_amp_s2', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch2_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('cntr_tx_ch2_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch2_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_tx_ch2_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch2_ps_q_p', 3, 0b000))
SCAN_LIST.append(ScanBit('i_bias_tx_ch1_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_tx_ch1_pa_s3', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch1_pa_s2', 6, 0b001010))
SCAN_LIST.append(ScanBit('i_bias_tx_ch1_pa_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('cntr_tx_ch1_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch1_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_tx_ch1_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_tx_ch1_ps_q_p', 3, 0b000))

# RX
config = config_RX
SCAN_LIST.append(ScanBit('rx_padding', 30, 0b0))
SCAN_LIST.append(ScanBit('i_bias_rx_comm_amp_s3', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_comm_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_comm_amp_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch4_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch4_amp_s4', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch4_amp_s3', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch4_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch4_amp_s1_cs', 6, 0b001000))
SCAN_LIST.append(ScanBit('i_bias_rx_ch4_amp_s1_cg', 6, 0b001000))
SCAN_LIST.append(ScanBit('cntr_rx_ch4_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch4_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_rx_ch4_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch4_ps_q_p', 3, 0b000))
SCAN_LIST.append(ScanBit('i_bias_rx_ch3_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch3_amp_s4', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch3_amp_s3', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch3_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch3_amp_s1_cs', 6, 0b001000))
SCAN_LIST.append(ScanBit('i_bias_rx_ch3_amp_s1_cg', 6, 0b001000))
SCAN_LIST.append(ScanBit('cntr_rx_ch3_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch3_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_rx_ch3_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch3_ps_q_p', 3, 0b000))
SCAN_LIST.append(ScanBit('i_bias_rx_ch2_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch2_amp_s4', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch2_amp_s3', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch2_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch2_amp_s1_cs', 6, 0b001000))
SCAN_LIST.append(ScanBit('i_bias_rx_ch2_amp_s1_cg', 6, 0b001000))
SCAN_LIST.append(ScanBit('cntr_rx_ch2_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch2_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_rx_ch2_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch2_ps_q_p', 3, 0b000))
SCAN_LIST.append(ScanBit('i_bias_rx_ch1_ps', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch1_amp_s4', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch1_amp_s3', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch1_amp_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_rx_ch1_amp_s1_cs', 6, 0b001000))
SCAN_LIST.append(ScanBit('i_bias_rx_ch1_amp_s1_cg', 6, 0b001000))
SCAN_LIST.append(ScanBit('cntr_rx_ch1_ps_i_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch1_ps_i_p', 3, 0b111))
SCAN_LIST.append(ScanBit('cntr_rx_ch1_ps_q_n', 3, 0b000))
SCAN_LIST.append(ScanBit('cntr_rx_ch1_ps_q_p', 3, 0b000))


# LO
config = config_LO
SCAN_LIST.append(ScanBit('lo_padding', 11, 0b0))
SCAN_LIST.append(ScanBit('i_bias_dac_mixer_amp', 6, 0b000010))
SCAN_LIST.append(ScanBit('i_bias_lo_quad_28g', 6, 0b010001))
SCAN_LIST.append(ScanBit('i_bias_lo_amp_28g', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_lo_quad_115g', 6, 0b010001))
SCAN_LIST.append(ScanBit('i_bias_lo_amp_115g_s1', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_lo_amp_115g_s2', 6, 0b001100))
SCAN_LIST.append(ScanBit('i_bias_lo_amp_115g_s3', 6, 0b001100))
SCAN_LIST.append(ScanBit('v_dac_mixer_amp_en', 1, 0b1))
SCAN_LIST.append(ScanBit('v_dac_mixer', 6, 0b001100))


csv_name = 'Cobra_Full_Scan_bits.csv'
with open(csv_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    # for key in config:
    #     csv_writer.writerow([key, config[key]])
    csv_writer.writerow(['LSB_Index',
                         'MSB_Index',
                         'Domain',
                         'Signal_Name',
                         'Bit_Width',
                         'Decimal_Value',
                         'Bits',
                         'Comment'])

    for scan in SCAN_LIST:
        csv_writer.writerow([scan.lsb_index,
                             int(scan.lsb_index+scan.bit_width-1),
                             scan.domain,
                             scan.signal_name,
                             scan.bit_width,
                             scan.value,
                             scan.bits_string,
                             scan.comment])

# exit()

# turn the scan chain into unfolded 1-bit array
csv_name = 'Cobra_Full_Scan_bits_unfolded.csv'
curr_index = 639
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
            csv_writer.writerow([curr_index, scan.domain, row[0], row[1], scan.comment])
            curr_index -= 1
