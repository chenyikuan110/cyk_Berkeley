import csv

path = 'FMCP_pin_mini.csv'

with open(path) as file_obj:
    reader_obj = csv.reader(file_obj)

    for row in reader_obj:
        string = row[2].split('_')

        if string[0] != '':
            if string[0] == 'VM' or string[0] == 'TX':
                print(f'output wire FMCP_HSPC_{row[1]}, // {string[0]}_{string[1]}[{string[2]}]')
            elif string[0][0] == 'D':
                print(f'output wire FMCP_HSPC_{row[1]}, // {string[0]}_{string[1]}_{string[2]}')
            else:
                print(f'output wire FMCP_HSPC_{row[1]}, // {row[2]}')

    for row in reader_obj:
        string = row[2].split('_')
        OBUF_string = 'OBUF #(.IOSTANDARD("LVCMOS18")) OBUF_'
        if string[0] != '':
            if string[0] == 'VM':
                print(f'{OBUF_string}{row[1]}(.O(FMCP_HSPC_{row[1]}), .I({string[0]}_{string[1]}_OUT[{string[2]}]));')
            elif string[0][0] == 'D':
                print(f'{OBUF_string}{row[1]}(.O(FMCP_HSPC_{row[1]}), .I({string[0]}_{string[1]}_{string[2]}_OUT));')
            else:
                print(f'{OBUF_string}{row[1]}(.O(FMCP_HSPC_{row[1]}), .I({row[2]}_OUT));')

    # XDC
    # for row in reader_obj:
    #     string = row[2].split('_')
    #     A_string = 'set_property PACKAGE_PIN'
    #     B_string = 'set_property IOSTANDARD  LVCMOS18 [get_ports'
    #     FPGA_PIN = row[0]
    #     if string[0] != '':
    #         if string[0] == 'VM':
    #             print(f'{A_string} {FPGA_PIN} [get_ports FMCP_HSPC_{row[1]}]; # {string[0]}_{string[1]}[{string[2]}]')
    #             print(f'{B_string} FMCP_HSPC_{row[1]}];\n')
    #         elif string[0][0] == 'D':
    #             print(f'{A_string} {FPGA_PIN} [get_ports FMCP_HSPC_{row[1]}]; # {string[0]}_{string[1]}_{string[2]}')
    #             print(f'{B_string} FMCP_HSPC_{row[1]}];\n')
    #         else:
    #             print(f'{A_string} {FPGA_PIN} [get_ports FMCP_HSPC_{row[1]}]; # {row[2]}')
    #             print(f'{B_string} FMCP_HSPC_{row[1]}];\n')