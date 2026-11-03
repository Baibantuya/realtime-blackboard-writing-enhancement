# Export a reviewed, routed candidate only. This is not board/CDC signoff.
# Usage: -tclargs impl5 OR p5. Retain failed exports instead of overwriting.
set here [file dirname [file normalize [info script]]]
if {[llength $argv] != 1 || [lsearch -exact {impl5 p5} [lindex $argv 0]] < 0} {
    error "Select the reviewed routed candidate: impl5 or p5"
}
set selected [lindex $argv 0]
set input [file join $here $selected routed.dcp]
set out [file join $here hardware_candidate5]
if {![string match 2025.2* [version -short]]} {error "Expected Vivado 2025.2"}
if {![file isfile $input] || [file exists $out]} {error "Missing checkpoint or retained export already exists"}
file mkdir $out
set_param general.maxThreads 4
set status [open [file join $out stages.tsv] w]
puts $status "stage\tresult\ttime"; flush $status
set source_record [open [file join $out source.txt] w]
puts $source_record $selected
close $source_record
open_checkpoint $input
if {![string equal -nocase [get_property PART [current_design]] xck26-sfvc784-2LV-c]} {error "Wrong part"}
foreach n {clk_out1_design_1_clk_wiz_0_0 clk_out2_video_design_1_clk_wiz_0_0 clk_out3_phy_design_1_clk_wiz_0_0} {
    if {[get_property PERIOD [get_clocks $n]] != 5.0} {error "Clock changed: $n"}
}
set timing [report_timing_summary -check_timing_verbose -report_unconstrained -return_string]
set tf [open [file join $out timing.rpt] w]; puts $tf $timing; close $tf
if {![regexp -line {^[ \t]*WNS\(ns\)[^\n]*\n[^\n]*\n([^\n]+)} $timing whole row]} {error "Cannot parse timing report"}
set metrics [regexp -all -inline {\S+} $row]
if {[llength $metrics] != 12} {error "Unexpected timing columns"}
foreach i {0 4 8} {if {[lindex $metrics $i] < 0} {error "Negative setup, hold, or pulse slack"}}
foreach i {1 2 5 6 9 10} {if {[lindex $metrics $i] != 0} {error "Nonzero timing violation total/count"}}
# Refuse export when any synchronous endpoints lack timing coverage.
foreach check {no_clock unconstrained_internal_endpoints} {
    set pattern [format {^[0-9]+\. checking %s \(([0-9]+)\)} $check]
    if {![regexp -line $pattern $timing whole count]} {error "Missing timing coverage check: $check"}
    if {$count != 0} {error "Unconstrained timing check: $check"}
}
set routes [report_route_status -return_string]
set rf [open [file join $out route_status.rpt] w]; puts $rf $routes; close $rf
foreach {label variable} {{routable nets} routable {fully routed nets} routed {nets with routing errors} errors} {
    set pattern [format {# of %s\.* *: *([0-9]+)} $label]
    if {![regexp $pattern $routes whole $variable]} {error "Missing route metric: $label"}
}
if {$routable == 0 || $routable != $routed || $errors != 0} {error "Incomplete or erroneous routing"}
report_drc -file [file join $out drc.rpt]
puts $status "numeric_and_route_gate\tPASS\t[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}]"; flush $status
set name imx219-v24-2025-2-c5
puts $status "bitstream\tRUNNING\t[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}]"; flush $status
write_bitstream [file join $out ${name}.bit]
puts $status "bitstream\tCOMPLETE\t[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}]"; flush $status
write_hw_platform -fixed -include_bit -file [file join $out ${name}.xsa]
puts $status "xsa\tCOMPLETE\t[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}]"; flush $status
close $status
puts "HARDWARE_EXPORT_COMPLETE_CDC_AND_BOARD_PENDING"
close_design
