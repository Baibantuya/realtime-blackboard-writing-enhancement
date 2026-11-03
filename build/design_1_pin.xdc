# Fan Speed Enable     HDA20     "som240_1_c24"
set_property BOARD_PIN som240_1_c24 [get_ports {fan_en_b}]
set_property IOSTANDARD LVCMOS33 [get_ports {fan_en_b}]
set_property SLEW SLOW           [get_ports {fan_en_b}]
set_property DRIVE 4             [get_ports {fan_en_b}]

# Raspi Camera Enable  HDA09     "som240_1_a15"
set_property BOARD_PIN som240_1_a15 [get_ports {rpi_cam_en}]
set_property IOSTANDARD LVCMOS33 [get_ports {rpi_cam_en}]
set_property SLEW SLOW           [get_ports {rpi_cam_en}]
set_property DRIVE 4             [get_ports {rpi_cam_en}]

# KV260 SOM 1.4 + carrier 1.3, Raspberry Pi camera interface.
# Connector pins: C12/C13 clock, B10/B11 data0, A9/A10 data1.
# BOARD_PIN names are supplied by the installed KV260 SOM board definition.
set_property BOARD_PIN som240_1_c12 [get_ports {mipi_csi_raspi_clk_p}]
set_property BOARD_PIN som240_1_c13 [get_ports {mipi_csi_raspi_clk_n}]
set_property BOARD_PIN som240_1_b10 [get_ports {mipi_csi_raspi_data_p[0]}]
set_property BOARD_PIN som240_1_b11 [get_ports {mipi_csi_raspi_data_n[0]}]
set_property BOARD_PIN som240_1_a9 [get_ports {mipi_csi_raspi_data_p[1]}]
set_property BOARD_PIN som240_1_a10 [get_ports {mipi_csi_raspi_data_n[1]}]
set_property IOSTANDARD MIPI_DPHY_DCI [get_ports {mipi_csi_raspi_*}]

# HDA IIC switch on bank 45 (same 3.3 V bank as fan_en_b/rpi_cam_en).
# Connector D16/D17 resolves through the board definition.
set_property BOARD_PIN som240_1_d16 [get_ports {hda_iic_switch_scl_io}]
set_property BOARD_PIN som240_1_d17 [get_ports {hda_iic_switch_sda_io}]
set_property IOSTANDARD LVCMOS33 [get_ports {hda_iic_switch_*}]

