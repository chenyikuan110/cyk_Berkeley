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
        self.bits_string = '{:0{width}b}'.format(val, width=self.bit_width)

    def set_off_val(self, off_val):
        self.off_bits = off_val
        self.off_bits_string = '{:0{width}b}'.format(off_val, width=self.bit_width)


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
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_QH_GM_BOT_L_BOT', 6, 0b100000))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_QH_GM_BOT_L_TOP', 6, 0b000000))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_THIRD_SPLIT_GM_BOT_L', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_DOUBLER_BOT_L', 6, 0b000110))
SCAN_LIST.append(ScanBit('LO_MID_TX_IB_DOUBLER_PREDRIVER_BOT_L', 6, 0b000100))

# LO_IQ_RX
config = config_LO_IQ_RX
# SCAN_LIST.append(ScanBit('LO_IQ_RX', 36, 0))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF3_Q_GM_RX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF3_I_GM_RX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF2_Q_GM_RX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF2_I_GM_RX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF1_Q_GM_RX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_RX_IB_BUF1_I_GM_RX0', 6, 0b000100))

# LO_IQ_TX
config = config_LO_IQ_TX
# SCAN_LIST.append(ScanBit('LO_IQ_TX', 24, 0))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF2_I_GM_TX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF2_Q_GM_TX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF1_I_GM_TX0', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_TX_IB_BUF1_Q_GM_TX0', 6, 0b000100))

# LO_FIRST
config = config_LO_FIRST
# SCAN_LIST.append(ScanBit('LO_FIRST', 38, 0))
SCAN_LIST.append(ScanBit('LO_FIRST_ILO_CS_BUF_EN', 1, 0b1)) # nominally, 3dB BW of the entire thing is 7.31-7.48GHz
SCAN_LIST.append(ScanBit('LO_FIRST_VCM_ILO_CS', 6, 0b100010)) # let's saturate LO, high lower f: 39 high higher f:31, 27 high gain for chirp
SCAN_LIST.append(ScanBit('LO_FIRST_ILO_INJ_BUF_EN', 1, 0b1))
SCAN_LIST.append(ScanBit('LO_FIRST_VCM_ILO_INJ', 6, 0b001100))
SCAN_LIST.append(ScanBit('LO_FIRST_IB_SECOND_SPLIT_RX_GM', 6, 0b000100)) # tied to VDD
SCAN_LIST.append(ScanBit('LO_FIRST_IB_SECOND_SPLIT_TX_GM', 6, 0b000100)) # tied to VDD
SCAN_LIST.append(ScanBit('LO_FIRST_IB_FIRST_SPLIT_GM', 6, 0b000101)) # tied to VDD
SCAN_LIST.append(ScanBit('LO_FIRST_IB_ILO_DRIVER', 6, 0b010000))

# LO_SECOND
config = config_LO_SECOND
# SCAN_LIST.append(ScanBit('LO_SECOND', 38, 0))
SCAN_LIST.append(ScanBit('LO_SECOND_ILO_CS_BUF_EN', 1, 0b1))
SCAN_LIST.append(ScanBit('LO_SECOND_VCM_ILO_CS', 6, 0b100010))
SCAN_LIST.append(ScanBit('LO_SECOND_ILO_INJ_BUF_EN', 1, 0b1))
SCAN_LIST.append(ScanBit('LO_SECOND_VCM_ILO_INJ', 6, 0b001100))
SCAN_LIST.append(ScanBit('LO_SECOND_IB_SECOND_SPLIT_RX_GM', 6, 0b000100)) # tied to VDD
SCAN_LIST.append(ScanBit('LO_SECOND_IB_SECOND_SPLIT_TX_GM', 6, 0b000100)) # tied to VDD
SCAN_LIST.append(ScanBit('LO_SECOND_IB_FIRST_SPLIT_GM', 6, 0b000101))
SCAN_LIST.append(ScanBit('LO_SECOND_IB_ILO_DRIVER', 6, 0b010000))

# LO_MID_RX
config = config_LO_MID_RX
# SCAN_LIST.append(ScanBit('LO_MID_RX', 30, 0))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_QH_GM_TOP_L_BOT', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_QH_GM_TOP_L_TOP', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_THIRD_SPLIT_GM_TOP_L', 6, 0b001000))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_DOUBLER_TOP_L', 6, 0b000110))
SCAN_LIST.append(ScanBit('LO_MID_RX_IB_DOUBLER_PREDRIVER_TOP_L', 6, 0b000100))

# IREF
config = config_IREF
SCAN_LIST.append(ScanBit('IREF', 2, 0b00))

# LO_IQ_VM
config = config_LO_IQ_VM
# SCAN_LIST.append(ScanBit('LO_IQ_VM', 24, 0))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF2_Q_GM_TX1', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF2_I_GM_TX1', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF1_Q_GM_TX1', 6, 0b000100))
SCAN_LIST.append(ScanBit('LO_IQ_VM_IB_BUF1_I_GM_TX1', 6, 0b000100))

# Meng implemented the I-Q scan codes to be symmetrical, since she flips the I-scan code orders in her layout
config = config_VM
SCAN_LIST.append(ScanBit('VM_IB_CMIN_CTRL_I',6,0b000111, off_bits=0b000001))
SCAN_LIST.append(ScanBit('VM_IB_AMP2_CTRL_I',6,0b010110, off_bits=0b000000)) # use 22  for Jose code
SCAN_LIST.append(ScanBit('VM_IB_VCM_REF_CTRL_I',6,0b011001)) # use 25 for Jose code
SCAN_LIST.append(ScanBit('VM_IB_PA_S1_CTRL_I',6,0b000000))
SCAN_LIST.append(ScanBit('VM_IB_PA_S2_CTRL_I',6,0b000000))
SCAN_LIST.append(ScanBit('VM_IB_PA_S3_CTRL_I',6,0b000000))
SCAN_LIST.append(ScanBit('VM_IB_CMFB_EN_IE_B',2,0b10, off_bits=0b11, msb_first=False))
SCAN_LIST.append(ScanBit('VM_IDCOC_EN_IE_B',3,0b001, off_bits=0b111, msb_first=False))
SCAN_LIST.append(ScanBit('VM_CMFB_EN_IE',1,0b1))
SCAN_LIST.append(ScanBit('VM_DCOC_SN_IE',1,0b0))
SCAN_LIST.append(ScanBit('VM_DCOC_SP_IE',1,0b0))
# SCAN_LIST.append(ScanBit('VM_TX_VOLT_CTRL_IE',32,0b01111011110110001000010011111111, off_bits=0b11111111111111111111100000000000, msb_first=False))
# SCAN_LIST.append(ScanBit('VM_TX_VOLT_CTRL_QE',32,0b11111111001000010001101111011110, off_bits=0b00000000000111111111111111111111))
SCAN_LIST.append(ScanBit('VM_gain_ctrl0_I',5,0b11111, off_bits=0b00000, msb_first=False))  # [0:4]
SCAN_LIST.append(ScanBit('VM_gain_ctrl_I',5,0b11111, off_bits=0b00000, msb_first=False))  # [5:9]
SCAN_LIST.append(ScanBit('VM_BVDD_tune_MID_I',1,0b0, off_bits=0b0, msb_first=False))  # [10]
SCAN_LIST.append(ScanBit('VM_freq_ctrl0_I',4,0b1100, off_bits=0b0000, msb_first=False))  # [11:14]
SCAN_LIST.append(ScanBit('VM_BVDD_tune_MSB_I',1,0b0, off_bits=0b0, msb_first=False))  # [15]
SCAN_LIST.append(ScanBit('VM_DCOC_CTRL_LSB_I',1,0b1, off_bits=0b0, msb_first=False))  # [16]
SCAN_LIST.append(ScanBit('VM_freq_ctrl_I',4,0b0000, off_bits=0b0000, msb_first=False))  # [17:20]
SCAN_LIST.append(ScanBit('VM_BVDD_tune_LSB_I',1,0b1, off_bits=0b0, msb_first=False))  # [21]
SCAN_LIST.append(ScanBit('VM_VMIXER_GATE_SW_I',5,0b00111, off_bits=0b00000, msb_first=False))  # [22:62]
SCAN_LIST.append(ScanBit('VM_VMIXER_BIAS_I',5,0b11111, off_bits=0b00000, msb_first=False))  # [27:31]

SCAN_LIST.append(ScanBit('VM_VMIXER_BIAS_Q',5,0b11111, off_bits=0b00000))  # [31:27]
SCAN_LIST.append(ScanBit('VM_VMIXER_GATE_SW_Q',5,0b11100, off_bits=0b00000))  # [26:22]
SCAN_LIST.append(ScanBit('VM_BVDD_tune_LSB_Q',1,0b1, off_bits=0b0))  # [21]
SCAN_LIST.append(ScanBit('VM_freq_ctrl_Q',4,0b0000, off_bits=0b0000))  # [20:17]
SCAN_LIST.append(ScanBit('VM_DCOC_CTRL_LSB_Q',1,0b1, off_bits=0b0))  # [16]
SCAN_LIST.append(ScanBit('VM_BVDD_tune_MSB_Q',1,0b0, off_bits=0b0))  # [15]
SCAN_LIST.append(ScanBit('VM_freq_ctrl0_Q',4,0b0011, off_bits=0b0000))  # [14:11]
SCAN_LIST.append(ScanBit('VM_BVDD_tune_MID_Q',1,0b0, off_bits=0b0))  # [10]
SCAN_LIST.append(ScanBit('VM_gain_ctrl_Q',5,0b11111, off_bits=0b00000))  # [9:5]
SCAN_LIST.append(ScanBit('VM_gain_ctrl0_Q',5,0b11111, off_bits=0b00000))  # [4:0]

SCAN_LIST.append(ScanBit('VM_DCOC_SP_QE',1,0b0))
SCAN_LIST.append(ScanBit('VM_DCOC_SN_QE',1,0b0))
SCAN_LIST.append(ScanBit('VM_CMFB_EN_QE',1,0b1))
SCAN_LIST.append(ScanBit('VM_IDCOC_EN_QE_B',3,0b010, off_bits=0b111))
SCAN_LIST.append(ScanBit('VM_IB_CMFB_EN_QE_B',2,0b10, off_bits=0b11))
SCAN_LIST.append(ScanBit('VM_IB_VCM_REF_CTRL_Q',6,0b100110, msb_first=False)) # use mirror 25->38
SCAN_LIST.append(ScanBit('VM_IB_AMP2_CTRL_Q',6,0b011010, off_bits=0b100000, msb_first=False)) # use mirror 22->26 for Jose code
SCAN_LIST.append(ScanBit('VM_IB_CMIN_CTRL_Q',6,0b111000, off_bits=0b100000, msb_first=False))
SCAN_LIST.append(ScanBit('VM_DCOC_CTRL_I',7,0b0000000))
SCAN_LIST.append(ScanBit('VM_DCOC_CTRL_Q',7,0b0000000))

# RX
config = config_RX
# SCAN_LIST.append(ScanBit('RX', 79, 0))
# nominal values optimal for one chip
SCAN_LIST.append(ScanBit('RX_VB_GC3_0', 3, 0b100)) # 3rd stage BB, 4 good
SCAN_LIST.append(ScanBit('RX_VB_GC2_0', 5, 0b00100)) # 2nd BB, 16 good
SCAN_LIST.append(ScanBit('RX_VB_GC1_0', 5, 0b00100)) # 1st BB, 1 good
SCAN_LIST.append(ScanBit('RX_IB_RFAMP_I_0', 4, 0b0100)) # mixer RF buffer I, 4, 5 same gain but 4 better HD3
SCAN_LIST.append(ScanBit('RX_IB_RFAMP_Q_0', 4, 0b0100)) # this is disabled on chip (no Q channel for RX)
SCAN_LIST.append(ScanBit('RX_VB_MIXER_Q_0', 6, 0b000100))  # this is disabled on chip (no Q channel for RX)
SCAN_LIST.append(ScanBit('RX_VB_FC_Q_0', 6, 0b000100))  # this is disabled on chip (no Q channel for RX)
SCAN_LIST.append(ScanBit('RX_VB_GC3_MSB1_0', 1, 0b0)) # MSB for 3rd stage BB
SCAN_LIST.append(ScanBit('RX_VB_GC4_Q_0', 5, 0b00100)) # 4th stage BB for I, each stage roughly has 7 dB
SCAN_LIST.append(ScanBit('RX_IB_BBAMP_0', 6, 0b000110)) # shared current bias for all BB stages
SCAN_LIST.append(ScanBit('RX_IB_RFAMP1_0', 4, 0b0100)) # LNA xfmr coupled stage
SCAN_LIST.append(ScanBit('RX_IB_RFAMP2_0', 4, 0b0100)) # splitter driver
SCAN_LIST.append(ScanBit('RX_VB_GC3_MSB0_0', 1, 0b0)) # 2nd-most significant bit for stage 3 of BB
SCAN_LIST.append(ScanBit('RX_VB_GC4_I_0', 5, 0b00100, msb_first=False)) # 4th stage BB for Q, each stage roughly has 7 dB
SCAN_LIST.append(ScanBit('RX_VB_FC_I_0', 6, 0b001000, msb_first=False)) # bandwidth control (BB active inductor)
SCAN_LIST.append(ScanBit('RX_VB_MIXER_I_0', 6, 0b001000, msb_first=False)) # -3dB loss in mixer roughly
SCAN_LIST.append(ScanBit('RX_IB_CS_0', 4, 0b0010)) # active balun CS
SCAN_LIST.append(ScanBit('RX_IB_CG_0', 4, 0b0010)) # active balun CG

# TX
# Meng implemented the I-Q scan codes to be symmetrical, since she flips the I-scan code orders in her layout
config = config_TX
SCAN_LIST.append(ScanBit('TX_IB_CMIN_CTRL_I',6,0b000111, off_bits=0b000001))
SCAN_LIST.append(ScanBit('TX_IB_AMP2_CTRL_I',6,0b010110, off_bits=0b000000)) # use 22  for Jose code
SCAN_LIST.append(ScanBit('TX_IB_VCM_REF_CTRL_I',6,0b011001)) # use 25 for Jose code
SCAN_LIST.append(ScanBit('TX_IB_PA_S1_CTRL_I',6,0b100000))
SCAN_LIST.append(ScanBit('TX_IB_PA_S2_CTRL_I',6,0b110000))
SCAN_LIST.append(ScanBit('TX_IB_PA_S3_CTRL_I',6,0b110000))
SCAN_LIST.append(ScanBit('TX_IB_CMFB_EN_IE_B',2,0b10, off_bits=0b11, msb_first=False))
SCAN_LIST.append(ScanBit('TX_IDCOC_EN_IE_B',3,0b001, off_bits=0b111, msb_first=False))
SCAN_LIST.append(ScanBit('TX_CMFB_EN_IE',1,0b1))
SCAN_LIST.append(ScanBit('TX_DCOC_SN_IE',1,0b0))
SCAN_LIST.append(ScanBit('TX_DCOC_SP_IE',1,0b0))
# SCAN_LIST.append(ScanBit('TX_TX_VOLT_CTRL_IE',32,0b_01001_01101_0_0101_1_0_1001_0_11010_01011, off_bits=0b11111111111111111111100000000000, msb_first=False)) # 2715935201 gives a magically good result
# SCAN_LIST.append(ScanBit('TX_TX_VOLT_CTRL_QE',32,0b_11010_01011_0_1001_0_1_1010_0_10110_10010, off_bits=0b00000_00000_0_1110_1_1_1111_1_11111_11111))
# 0b_00111_00111_0_0110_0_0_0110_0_00111_00000 from txq of TX_CONFIG.csv (Meng) this should be used as I-channel here
# 0b_00111_00111_0_0110_0_0_0110_0_00111_11111(mixer_bias) from txq of TX_CONFIG.csv (Meng, labelled as default) this should be used as I-channel here

# 0b_11111_11111_0_1100_0_1_0000_1_00111_11111(mixer_bias) from txq of TX_CONFIG_JOSE_UNIQUE_SIGNAMES.csv (Jose) this should be used as I-channel here
# 0b_11111(mixer_bias)_11100_1_0000_1_0_0011_0_11111_11111 from txi of TX_CONFIG_JOSE_UNIQUE_SIGNAMES.csv (Jose) this should be used as Q-channel here
# SCAN_LIST.append(ScanBit('TX_TX_VOLT_CTRL_IE',32,0b_00000111000011000011001110011100, off_bits=0b11111111111111111111100000000000, msb_first=True)) # 2715935201 gives a magically good result
SCAN_LIST.append(ScanBit('TX_gain_ctrl0_I',5,0b11111, off_bits=0b00000, msb_first=False))  # [0:4]
SCAN_LIST.append(ScanBit('TX_gain_ctrl_I',5,0b11111, off_bits=0b00000, msb_first=False))  # [5:9]
SCAN_LIST.append(ScanBit('TX_BVDD_tune_MID_I',1,0b0, off_bits=0b0, msb_first=False))  # [10]
SCAN_LIST.append(ScanBit('TX_freq_ctrl0_I',4,0b1100, off_bits=0b0000, msb_first=False))  # [11:14]
SCAN_LIST.append(ScanBit('TX_BVDD_tune_MSB_I',1,0b0, off_bits=0b0, msb_first=False))  # [15]
SCAN_LIST.append(ScanBit('TX_DCOC_CTRL_LSB_I',1,0b1, off_bits=0b0, msb_first=False))  # [16]
SCAN_LIST.append(ScanBit('TX_freq_ctrl_I',4,0b0000, off_bits=0b0000, msb_first=False))  # [17:20]
SCAN_LIST.append(ScanBit('TX_BVDD_tune_LSB_I',1,0b1, off_bits=0b0, msb_first=False))  # [21]
SCAN_LIST.append(ScanBit('TX_VMIXER_GATE_SW_I',5,0b00111, off_bits=0b00000, msb_first=False))  # [22:62]
SCAN_LIST.append(ScanBit('TX_VMIXER_BIAS_I',5,0b11111, off_bits=0b00000, msb_first=False))  # [27:31]

SCAN_LIST.append(ScanBit('TX_VMIXER_BIAS_Q',5,0b11111, off_bits=0b00000))  # [31:27]
SCAN_LIST.append(ScanBit('TX_VMIXER_GATE_SW_Q',5,0b11100, off_bits=0b00000))  # [26:22]
SCAN_LIST.append(ScanBit('TX_BVDD_tune_LSB_Q',1,0b1, off_bits=0b0))  # [21]
SCAN_LIST.append(ScanBit('TX_freq_ctrl_Q',4,0b0000, off_bits=0b0000))  # [20:17]
SCAN_LIST.append(ScanBit('TX_DCOC_CTRL_LSB_Q',1,0b1, off_bits=0b0))  # [16]
SCAN_LIST.append(ScanBit('TX_BVDD_tune_MSB_Q',1,0b0, off_bits=0b0))  # [15]
SCAN_LIST.append(ScanBit('TX_freq_ctrl0_Q',4,0b0011, off_bits=0b0000))  # [14:11]
SCAN_LIST.append(ScanBit('TX_BVDD_tune_MID_Q',1,0b0, off_bits=0b0))  # [10]
SCAN_LIST.append(ScanBit('TX_gain_ctrl_Q',5,0b11111, off_bits=0b00000))  # [9:5]
SCAN_LIST.append(ScanBit('TX_gain_ctrl0_Q',5,0b11111, off_bits=0b00000))  # [4:0]

SCAN_LIST.append(ScanBit('TX_DCOC_SP_QE',1,0b0))
SCAN_LIST.append(ScanBit('TX_DCOC_SN_QE',1,0b0))
SCAN_LIST.append(ScanBit('TX_CMFB_EN_QE',1,0b1))
SCAN_LIST.append(ScanBit('TX_IDCOC_EN_QE_B',3,0b010, off_bits=0b111))
SCAN_LIST.append(ScanBit('TX_IB_CMFB_EN_QE_B',2,0b10, off_bits=0b11))
SCAN_LIST.append(ScanBit('TX_IB_VCM_REF_CTRL_Q',6,0b100110, msb_first=False)) # use mirror 25->38
SCAN_LIST.append(ScanBit('TX_IB_AMP2_CTRL_Q',6,0b011010, off_bits=0b100000, msb_first=False)) # use mirror 22->26 for Jose code
SCAN_LIST.append(ScanBit('TX_IB_CMIN_CTRL_Q',6,0b111000, off_bits=0b100000, msb_first=False))
SCAN_LIST.append(ScanBit('TX_DCOC_CTRL_I',7,0b0000000))
SCAN_LIST.append(ScanBit('TX_DCOC_CTRL_Q',7,0b0000000))

# the serialization result goes from last appended number first, from right digit to left digit
# scan_data[0:6] aka tx_ctrl[147:141] will be 1,0,0,0,0,0,0, this is TX_DCOC_CTRL_Q[0:6]
# scan_data[136:141] aka tx_ctrl[11:6] will be 1,0,1,1,1,0, thsi is TX_IB_AMP2_CTRL_I[0:5]

# scan_data[0] on chip will be 1 in this case, aka, TX_scan[147] will be 1,
# aka, DCOC_CTRL_Q[0] will be 1

csv_name = 'Full_Scan_bits_newTX.csv'
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
                         'Off_Bits',
                         'Comment'])

    for scan in SCAN_LIST:
        csv_writer.writerow([scan.lsb_index,
                             scan.domain,
                             scan.signal_name,
                             scan.bit_width,
                             scan.value,
                             scan.bits_string,
                             scan.off_bits,
                             scan.comment])

# exit()

# turn the scan chain into unfolded 1-bit array
csv_name = 'Full_Scan_bits_newTX_unfolded.csv'
curr_index = 596
with open(csv_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(['Scan_Index',
                         'Domain',
                         'Bit_Name',
                         'Bit',
                         'Off_Bit',
                         'Comment'])

    curr_index = 596
    for scan in SCAN_LIST:
        unfolded_list = unfold_bits(scan.signal_name, scan.bit_width, scan.msb_first, scan.bits_string)
        off_bit_list = unfold_bits(scan.signal_name, scan.bit_width, scan.msb_first, scan.off_bits_string)
        for i, row in enumerate(list(unfolded_list)):
            csv_writer.writerow([curr_index, scan.domain, row[0], row[1], off_bit_list[i][1], scan.comment])
            curr_index -= 1
