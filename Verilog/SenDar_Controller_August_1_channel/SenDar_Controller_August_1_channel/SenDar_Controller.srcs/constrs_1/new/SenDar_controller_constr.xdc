# Clock ISC85411A/U21.1 & 21.2
set_property PACKAGE_PIN D12           [get_ports CLK_250MHZ_CLK1_N] ;# Bank  41 VCCO - VCC1V2_FPGA - IO_L13N_T2L_N1_GC_QBC_41
set_property PACKAGE_PIN E12           [get_ports CLK_250MHZ_CLK1_P] ;# Bank  41 VCCO - VCC1V2_FPGA - IO_L13P_T2L_N0_GC_QBC_41
set_property IOSTANDARD  DIFF_SSTL12    [get_ports CLK_250MHZ_CLK1_N] ;# Bank  41 VCCO - VCC1V2_FPGA - IO_L13N_T2L_N1_GC_QBC_41
set_property IOSTANDARD  DIFF_SSTL12    [get_ports CLK_250MHZ_CLK1_P] ;# Bank  41 VCCO - VCC1V2_FPGA - IO_L13P_T2L_N0_GC_QBC_41
create_clock -name CLK_250MHZ_CLK1_P -period 4.0 [get_ports CLK_250MHZ_CLK1_P];

# Buttons
set_property PACKAGE_PIN BD23     [get_ports reset_input] ;# Bank  64 VCCO - VCC1V8_FPGA - IO_L5P_T0U_N8_AD14P_64 GPIO_SW_Center - 7
set_property IOSTANDARD  LVCMOS18 [get_ports reset_input] ;# Bank  64 VCCO - VCC1V8_FPGA - IO_L5P_T0U_N8_AD14P_64

set_property PACKAGE_PIN BE23     [get_ports s_axis_config_tvalid_in] ;# Bank  64 VCCO - VCC1V8_FPGA - IO_L5P_T0U_N8_AD14P_64 GPIO_SW_East - 9
set_property IOSTANDARD  LVCMOS18 [get_ports s_axis_config_tvalid_in] ;# Bank  64 VCCO - VCC1V8_FPGA - IO_L5P_T0U_N8_AD14P_64

# Switches
set_property PACKAGE_PIN G16 [get_ports {transmission_mode_in}]; #gpio_switch2
set_property IOSTANDARD LVCMOS12 [get_ports {transmission_mode_in}];

set_property PACKAGE_PIN B17 [get_ports {data_flow_en_in}]; #gpio_switch1 (bottom)
set_property IOSTANDARD LVCMOS12 [get_ports {data_flow_en_in}];

# LEDs
set_property PACKAGE_PIN AY30     [get_ports GPIO_LED2] ;# Bank  40 VCCO - VCC1V2_FPGA - IO_T1U_N12_40 - s_axis_data_tready
set_property IOSTANDARD  LVCMOS12 [get_ports GPIO_LED2] ;# Bank  40 VCCO - VCC1V2_FPGA - IO_T1U_N12_40
set_property DRIVE 8 [get_ports GPIO_LED2] ;

set_property PACKAGE_PIN AV34     [get_ports GPIO_LED1] ;# Bank  40 VCCO - VCC1V2_FPGA - IO_T2U_N12_40 - s_axis_config_tready
set_property IOSTANDARD  LVCMOS12 [get_ports GPIO_LED1] ;# Bank  40 VCCO - VCC1V2_FPGA - IO_T2U_N12_40
set_property DRIVE 8 [get_ports GPIO_LED1] ;

set_property PACKAGE_PIN AT32     [get_ports GPIO_LED0] ;# Bank  40 VCCO - VCC1V2_FPGA - IO_L19N_T3L_N1_DBC_AD9N_40 - data_flow_en
set_property IOSTANDARD  LVCMOS12 [get_ports GPIO_LED0] ;# Bank  40 VCCO - VCC1V2_FPGA - IO_L19N_T3L_N1_DBC_AD9N_40
set_property DRIVE 8 [get_ports GPIO_LED0] ;


# UART signals
set_property PACKAGE_PIN AW25 [get_ports FPGA_SERIAL_RX_PIN];
set_property IOSTANDARD LVCMOS18 [get_ports FPGA_SERIAL_RX_PIN];

set_property PACKAGE_PIN BB21 [get_ports FPGA_SERIAL_TX_PIN];
set_property IOSTANDARD LVCMOS18 [get_ports FPGA_SERIAL_TX_PIN];