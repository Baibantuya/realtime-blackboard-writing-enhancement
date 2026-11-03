set root [file dirname [file dirname [file normalize [info script]]]]
file mkdir [file join $root h]
cd [file join $root h]
if {![string match 2025.2* [version -short]]} {error "Expected Vitis HLS 2025.2"}
set out [file join $root h w]
if {[file exists $out]} {error "Use a fresh source-only copy; preserve earlier build"}
set source [file join $root src pl hls]
open_project $out
set_top whiteboard_restore
add_files [file join $source whiteboard_restore.cpp] -cflags "-std=c++14 -I$source "
add_files [file join $source guarded_state.cpp] -cflags "-std=c++14"
add_files -tb [file join $root sim tb test_scene_rebase565.cpp] -cflags "-std=c++14 -I$source"
open_solution s -flow_target vivado
set_part xck26-sfvc784-2LV-c
create_clock -period 5.0 -name default
config_rtl -reset control
config_op add -impl dsp
config_compile -pipeline_loops 0
config_interface -m_axi_addr64=true
csim_design
csynth_design
cosim_design -rtl verilog
export_design -format ip_catalog -vendor whiteboard.org -library hls -version 1.0
puts "CLEAN_HLS_W_COMPLETE"
exit
