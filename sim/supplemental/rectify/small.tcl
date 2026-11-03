set here [file dirname [file normalize [info script]]]
cd $here
if {![string match 2025.2* [version -short]]} {error "Expected 2025.2"}
if {[file exists p]} {error "Preserve previous HLS project"}
open_project p
set_top board_rectify_rgb
add_files src/board_rectify_rgb.cpp -cflags "-std=c++14 -Isrc -DWB_HLS"
add_files -tb tb/test_rectify.cpp -cflags "-std=c++14 -Isrc -DWB_SMALL_TEST"
open_solution s -flow_target vivado
set_part xck26-sfvc784-2LV-c
create_clock -period 5.0 -name default
config_rtl -reset control
config_interface -m_axi_addr64=false
csim_design
csynth_design
cosim_design -rtl verilog -trace_level none
puts "LOCAL6_RECTIFY_SMALL_C_RTL_COMPLETE"
exit
