import csv

# path = 'FMCP_pin_mini.csv'
path = 'FMCP_pin_full.csv'

with open(path) as file_obj:
    reader_obj = csv.reader(file_obj)

    # print XDC list
    for row in reader_obj:
        string = row[2].split('_')
        A_string = 'set_property PACKAGE_PIN'
        B_string_LVCMOS = 'set_property IOSTANDARD LVCMOS18 [get_ports'
        B_string_LVDS   = 'set_property IOSTANDARD LVDS [get_ports'
        FPGA_PIN = row[0]
        if string[0] != '':
            if string[0] == 'VM' or string[0] == 'TX':
                sig_name = f'{string[0]}_{string[1]}_OUT_pin[{string[2]}]'
                print(f'# FMCP_HSPC_{row[1]} at {FPGA_PIN}')
                print(f'{A_string} {FPGA_PIN} [get_ports {sig_name}];')
                print(f'{B_string_LVCMOS} {sig_name}];\n')
            elif string[0] == 'RX':
                if string[1] == 'DCO' or string[1] == 'OR':
                    sig_name = f'{string[0]}_{string[1]}_{string[2]}_pin'
                else:
                    sig_name = f'{string[0]}_{string[2]}_pin[{string[1]}]'
                print(f'# FMCP_HSPC_{row[1]} at {FPGA_PIN}')
                print(f'{A_string} {FPGA_PIN} [get_ports {sig_name}];')
                print(f'{B_string_LVDS} {sig_name}];\n')
            elif string[0] == 'EXT' or string[0] == 'JUMPER' :
                continue
                # sig_name = f'{row[2]_P}'
                # print(f'# FMCP_HSPC_{row[1]} at {FPGA_PIN}')
                # print(f'{A_string} {FPGA_PIN} [get_ports {sig_name}];')
                # print(f'{B_string_LVDS} {sig_name}];\n')
            else:
                sig_name = f'{row[2]}_OUT_pin'
                print(f'# FMCP_HSPC_{row[1]} at {FPGA_PIN}')
                print(f'{A_string} {FPGA_PIN} [get_ports {sig_name}];')
                print(f'{B_string_LVCMOS} {sig_name}];\n')

# module IO
for name in ['DAC_CLK_MAIN', 'DATA_CLK_MAIN','AWG_Trigger','ADC_CLK']:
    print(f'output wire {name}_OUT_pin,')
print(f'input wire [15:0] RX_P_pin,')
print(f'input wire [15:0] RX_N_pin,')
print(f'input wire RX_OR_P_pin,')
print(f'input wire RX_OR_N_pin,')
print(f'input wire RX_DCO_P_pin,')
print(f'input wire RX_DCO_N_pin,')
for name in ['TX', 'VM']:
    for quad in ['I', 'Q']:
        print(f'output wire [15:0] {name}_{quad}_I_OUT_pin,')

# internal signals
print('')
for name in ['DAC_CLK_MAIN', 'DATA_CLK_MAIN','AWG_Trigger','ADC_CLK']:
    print(f'wire {name}_OUT;')
print(f'wire [15:0] RX;')
print(f'wire RX_OR;')
print(f'wire RX_DCO;')
for name in ['TX', 'VM']:
    for quad in ['I', 'Q']:
        print(f'wire [15:0] {name}_{quad}_I_OUT;')


# output buffers
OBUF_string = 'OBUF #(.IOSTANDARD("LVCMOS18")) OBUF_'
print('')
for name in ['DAC_CLK_MAIN', 'DATA_CLK_MAIN','AWG_Trigger','ADC_CLK']:
    print(f'{OBUF_string}{name}(.O({name}_OUT_pin), .I({name}_OUT) );')

for name in ['TX', 'VM']:
    for quad in ['I','Q']:
        for i in range(16):
            print(f'{OBUF_string}{name}_{quad}_{i} (.O({name}_{quad}_OUT_pin[{i}]), .I({name}_{quad}_OUT[{i}]) );')

# input buffers
IBUF_string = 'IBUFDS #(.IOSTANDARD("LVDS")) IBUFDS_'
print('')
print(f'{IBUF_string}RX_OR (.O(RX_OR), .I(RX_OR_P_pin), .IB(RX_OR_N_pin) );')
print(f'{IBUF_string}RX_DCO (.O(RX_DCO), .I(RX_DCO_P_pin), .IB(RX_DCO_N_pin) );')
for i in range(16):
    print(f'{IBUF_string}RX_{i} (.O(RX[{i}]), .I(RX_P_pin[{i}]), .IB(RX_N_pin[{i}]) );')