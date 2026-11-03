# Recreate the final V24 BD with the matched integrated IP catalog.
set script_dir [file dirname [file normalize [info script]]]
set root [file dirname $script_dir]
if {![string match "2021.2*" [version -short]]} {error "Use Vivado 2021.2"}
set work [file join $script_dir work vivado]
set project_dir [file join $work system]
set reports [file join $work reports]
if {[file exists [file join $project_dir whiteboard_v24.xpr]]} {error "Existing project retained; choose a fresh build/work/vivado directory"}
file mkdir $reports
set_param general.maxThreads 8
create_project whiteboard_v24 $project_dir -part xck26-sfvc784-2LV-c
set_property target_language Verilog [current_project]
set_property XPM_LIBRARIES {XPM_MEMORY} [current_project]
if {![llength [get_board_parts -quiet xilinx.com:kv260_som:part0:1.2]]} {error "Install the Vivado2021.2 KV260 board files"}
set_property board_part xilinx.com:kv260_som:part0:1.2 [current_project]
set_property board_connections {som240_1_connector xilinx.com:kv260_carrier:som240_1_connector:1.2} [current_project]
set ip_base [file join $root src pl ip]
set_property ip_repo_paths [list [file join $ip_base rectify] [file join $ip_base restore] [file join $ip_base scene]] [current_project]
update_ip_catalog
set rtl [file join $root src pl rtl]
add_files -norecurse [concat [glob [file join $rtl *.v]] [glob [file join $rtl *.sv]]]
set_property file_type SystemVerilog [get_files -quiet *.sv]
source [file join $script_dir design_1_restore.bd.tcl]
validate_bd_design
save_bd_design
generate_target all [get_files design_1.bd]
make_wrapper -files [get_files design_1.bd] -top -import
set_property top design_1_wrapper [current_fileset]
add_files -fileset constrs_1 -norecurse [file join $script_dir design_1_pin.xdc]
update_compile_order -fileset sources_1
set_property -name {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} -value {-control_set_opt_threshold 16} -objects [get_runs synth_1]
set_property STEPS.OPT_DESIGN.ARGS.DIRECTIVE ExploreArea [get_runs impl_1]
set_property STEPS.PLACE_DESIGN.ARGS.DIRECTIVE AltSpreadLogic_high [get_runs impl_1]
set_property STEPS.PHYS_OPT_DESIGN.ARGS.DIRECTIVE AggressiveExplore [get_runs impl_1]
launch_runs synth_1 -jobs 8
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} {error "Synthesis failed"}
launch_runs impl_1 -to_step route_design -jobs 1
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {error "Implementation failed"}
open_run impl_1
# Repeat the actual original flow's duplicate Clock Wizard primary-clock correction.
set before [file join $reports timing_before_clock_fix.xdc]
set after [file join $reports timing_clock_fixed.xdc]
write_xdc -type timing -force $before
set f [open $before r];set content [read $f];close $f
set corrected {};set removed 0
foreach line [split $content "\n"] {
    set trimmed [string trim $line]
    if {$trimmed eq {create_clock -period 10.000 [get_ports -scoped_to_current_instance clk_in1]} ||
        $trimmed eq {set_input_jitter [get_clocks -of_objects [get_ports -scoped_to_current_instance clk_in1]] 0.100}} {
        incr removed
    } else {lappend corrected $line}
}
if {$removed == 2} {
    lappend corrected {current_instance -quiet}
    lappend corrected {set_input_jitter [get_clocks clk_pl_0] 0.100}
    set f [open $after w];puts $f [join $corrected "\n"];close $f
    reset_timing -invalid -clock_reservation
    read_xdc -no_add $after
    current_instance -quiet
} elseif {$removed != 0} {error "Unexpected partial duplicate-clock constraint removal"}
if {[llength [get_clocks -quiet design_1_i/clk_wiz_0/inst/clk_in1]]} {error "Duplicate Clock Wizard primary remains"}
report_clocks -file [file join $reports clocks.rpt]
report_timing_summary -check_timing_verbose -report_unconstrained -file [file join $reports timing.rpt]
report_timing -delay_type max -max_paths 20 -file [file join $reports setup20.rpt]
report_timing -delay_type min -max_paths 20 -file [file join $reports hold20.rpt]
report_utilization -file [file join $reports utilization.rpt]
report_drc -file [file join $reports drc.rpt]
report_cdc -file [file join $reports cdc.rpt]
set setup [get_timing_paths -delay_type max -max_paths 1]
set hold [get_timing_paths -delay_type min -max_paths 1]
if {![llength $setup] || ![llength $hold]} {error "Missing timing paths"}
set wns [get_property SLACK [lindex $setup 0]]
set whs [get_property SLACK [lindex $hold 0]]
set result PASS
if {$wns < 0 || $whs < 0} {set result FAIL}
set f [open [file join $reports timing_status.json] w]
puts $f [format {{"result":"%s","wns_ns":%s,"whs_ns":%s}} $result $wns $whs];close $f
write_checkpoint -force [file join $work routed.dcp]
if {$result eq "FAIL" && (![info exists ::env(WB_ALLOW_NEGATIVE_TIMING)] || $::env(WB_ALLOW_NEGATIVE_TIMING) ne "1")} {
    error "Negative timing retained in reports; set WB_ALLOW_NEGATIVE_TIMING=1 only to reproduce the documented experimental V24 export"
}
write_bitstream -force [file join $work imx219-fusion-v24.bit]
write_hw_platform -fixed -include_bit -force -file [file join $work whiteboard_v24.xsa]
write_bd_tcl -force [file join $reports design_1_restore.bd.tcl]
puts "V24_EXPORT_COMPLETE timing=$result WNS=$wns WHS=$whs"
