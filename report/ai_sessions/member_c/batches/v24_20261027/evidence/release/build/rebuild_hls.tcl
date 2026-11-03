# Portable V24 HLS entry. Run manually; never part of board startup.
set script_dir [file dirname [file normalize [info script]]]
set root [file dirname $script_dir]
set core scene
set mode export
if {$argc > 0} {set core [lindex $argv 0]}
if {$argc > 1} {set mode [lindex $argv 1]}
if {$core ni {scene restore}} {error "core must be scene or restore; rectify uses the matched prebuilt IP"}
if {$mode ni {csim synth cosim export}} {error "mode must be csim, synth, cosim or export"}
if {![string match "2021.2*" [version -short]]} {error "Use Vitis HLS 2021.2"}
source [file join $script_dir tool_patch automg_patch_20220104.tcl]
set hls [file join $root src pl hls]
set work [file join $script_dir work hls]
file mkdir $work
cd $work
if {$core eq "scene"} {
    open_project -reset board_scene_quantize_hls
    set_top board_scene_quantize
    add_files [file join $hls board_scene_quantize.cpp] -cflags "-std=c++11"
    add_files -tb [file join $root sim tb test_scene_hls.cpp] -cflags "-std=c++11 -I$hls"
} else {
    open_project -reset whiteboard_restore_v6_hls
    set_top whiteboard_restore
    add_files [file join $hls whiteboard_restore.cpp] -cflags "-std=c++14"
    add_files [file join $hls guarded_state.cpp] -cflags "-std=c++14"
    add_files -tb [file join $root sim tb test_scene_rebase565.cpp] -cflags "-std=c++14 -I$hls"
}
open_solution -reset solution1
set_part xck26-sfvc784-2LV-c
create_clock -period 5.0 -name default
config_rtl -reset control
config_op add -impl dsp
if {$core eq "scene"} {
    config_interface -m_axi_addr64=false
} else {
    config_compile -pipeline_loops 0
    config_interface -m_axi_addr64=true
}
if {$mode in {csim cosim}} {csim_design}
if {$mode ne "csim"} {csynth_design}
if {$mode eq "cosim"} {cosim_design -rtl verilog}
if {$mode eq "export"} {export_design -format ip_catalog -vendor whiteboard.org -library hls -version 1.0}
exit
