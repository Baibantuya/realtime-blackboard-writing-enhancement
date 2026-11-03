# Isolated non-project implementation from the reviewed 2025.2 synthesis DCP.
# Never writes bit/XSA, never edits either existing project, never waives timing.
set here [file dirname [file dirname [file normalize [info script]]]]
set out [file join $here i]
if {[file exists $out]} {error "Existing implementation evidence retained"}
if {![string match 2025.2* [version -short]]} {error "Expected 2025.2"}
file mkdir $out
set_param general.maxThreads 4
set status [open [file join $out stages.tsv] w]
puts $status "stage\tresult\ttime"; flush $status
proc stage {name script checkpoint} {
    global status out
    puts $status "$name\tRUNNING\t[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}]"; flush $status
    if {[catch {uplevel 1 $script} message options]} {
        puts $status "$name\tFAILED\t$message"; flush $status
        return -options $options $message
    }
    puts $status "$name\tCOMPLETE\t[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}]"; flush $status
    if {$checkpoint ne ""} {write_checkpoint [file join $out $checkpoint]}
}
stage open {open_checkpoint [file join $here v reports synthesized.dcp]} ""
if {![string equal -nocase [get_property PART [current_design]] xck26-sfvc784-2LV-c]} {error "Unexpected target part"}
foreach n {clk_out1_design_1_clk_wiz_0_0 clk_out2_video_design_1_clk_wiz_0_0 clk_out3_phy_design_1_clk_wiz_0_0} {
    if {[get_property PERIOD [get_clocks $n]] != 5.0} {error "Clock changed: $n"}
}
stage constraints {
    read_xdc [file join $here build clock_source_jitter.xdc]
    source [file join $here build tighten_mipi_exception.tcl]
    tighten_mipi_exception [file join $out mipi_constraints]
} ""
report_clocks -file [file join $out before_implementation_clocks.rpt]
stage opt {opt_design -directive ExploreArea} optimized.dcp
report_drc -file [file join $out post_opt_drc.rpt]
stage place {place_design -directive AltSpreadLogic_high} placed.dcp
report_timing_summary -check_timing_verbose -report_unconstrained -file [file join $out post_place_timing.rpt]
stage phys_opt {phys_opt_design -directive AggressiveExplore} physopt.dcp
stage route {route_design} routed.dcp
report_route_status -file [file join $out route_status.rpt]
report_utilization -file [file join $out utilization.rpt]
report_utilization -hierarchical -hierarchical_depth 3 -file [file join $out utilization_hierarchy.rpt]
report_control_sets -verbose -file [file join $out control_sets.rpt]
report_timing_summary -check_timing_verbose -report_unconstrained -file [file join $out timing.rpt]
report_timing -delay_type max -max_paths 30 -file [file join $out setup30.rpt]
report_timing -delay_type min -max_paths 30 -file [file join $out hold30.rpt]
report_drc -file [file join $out drc.rpt]
report_methodology -file [file join $out methodology.rpt]
report_cdc -details -all_checks_per_endpoint -file [file join $out cdc.rpt]
report_clocks -file [file join $out clocks.rpt]
report_clock_interaction -file [file join $out interactions.rpt]
report_bus_skew -file [file join $out bus_skew.rpt]
write_xdc -type timing [file join $out timing_constraints.xdc]
puts $status "reports\tCOMPLETE\t[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}]"
close $status
puts "IMPLEMENTATION_FLOW_COMPLETE_REVIEW_REPORTS_FOR_SIGNOFF"
close_design
