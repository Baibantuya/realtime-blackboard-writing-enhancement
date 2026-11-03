# Rebuild/validate BD metadata and synthesize only the monitor; never implement/program.
set here [file dirname [file normalize [info script]]]
set root [file dirname [file dirname $here]]
set out [file join $here integration]
if {[file exists $out]} {error "Retain previous integration evidence"}
file mkdir $out
set_param general.maxThreads 2
create_project review [file join $out p] -part xck26-sfvc784-2LV-c
set_property target_language Verilog [current_project]
set_property XPM_LIBRARIES {XPM_MEMORY} [current_project]
set_property board_part xilinx.com:kv260_som:part0:1.2 [current_project]
set_property board_connections {som240_1_connector xilinx.com:kv260_carrier:som240_1_connector:1.2} [current_project]
set repos {}
foreach core {r s w} {lappend repos [file join $root r5 h $core s impl ip]}
set_property ip_repo_paths $repos [current_project]
update_ip_catalog
foreach file [concat [glob [file join $root r5 src pl rtl *.v]] [glob [file join $root r5 src pl rtl *.sv]]] {
    if {[file tail $file] eq "axis_ae_status.v"} {set file [file join $here rtl axis_ae_status.v]}
    add_files -norecurse $file
}
set_property file_type SystemVerilog [get_files -quiet *.sv]
set ::origin_dir_loc [file join $out b]
source [file join $root r5 build design.tcl]
set_property CONFIG.PRIM_SOURCE No_buffer [get_bd_cells clk_wiz_0]
validate_bd_design
if {![string equal -nocase [get_property MODE [get_bd_intf_pins ae_status/s_axis]] Monitor]} {error "Monitor mode lost in integration"}
foreach p {s_axis_tdata s_axis_tvalid s_axis_tready s_axis_tuser} {
    if {[get_property DIR [get_bd_pins ae_status/$p]] ne "I"} {error "Observer pin drives video: $p"}
    if {[llength [get_bd_nets -of_objects [get_bd_pins ae_status/$p]]] != 1} {error "Observer connection missing: $p"}
}
save_bd_design
write_bd_tcl [file join $out design.tcl]
report_ip_status -file [file join $out ip_status.rpt]
puts "LOCAL6_FULL_BD_VALIDATED_NOT_IMPLEMENTED"
close_project
foreach mode {before after} {
    set rtl [file join $here [expr {$mode eq "before" ? "before" : "rtl"}]]
    create_project -in_memory -part xck26-sfvc784-2LV-c
    read_verilog [file join $rtl axis_ae_status.v]
    read_verilog -sv [list [file join $rtl axis_luma_meter.sv] [file join $rtl ae_controller.sv]]
    synth_design -top axis_ae_status -part xck26-sfvc784-2LV-c -mode out_of_context
    create_clock -name ae_clock -period 5.0 [get_ports aclk]
    report_utilization -file [file join $out ${mode}_utilization.rpt]
    report_timing_summary -file [file join $out ${mode}_timing.rpt]
    report_drc -file [file join $out ${mode}_drc.rpt]
    write_checkpoint [file join $out ${mode}.dcp]
    write_verilog -mode funcsim [file join $out ${mode}_netlist.v]
    close_project
}
puts "LOCAL6_AE_OOC_BOTH_COMPLETE"
exit
