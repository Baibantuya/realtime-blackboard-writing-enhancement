set here [file dirname [file normalize [info script]]]
set mode [lindex $argv 0]
if {$mode ni {before after}} {error "Expected before or after"}
if {![string match 2025.2* [version -short]]} {error "Expected 2025.2"}
set out [file join $here $mode-probe]
if {[file exists $out]} {error "Retain previous probe"}
file mkdir $out
set rtl [file join $here [expr {$mode eq "before" ? "before" : "rtl"}]]
set_param general.maxThreads 2
create_project ae_probe [file join $out p] -part xck26-sfvc784-2LV-c
add_files [list [file join $rtl axis_ae_status.v] [file join $rtl axis_luma_meter.sv] [file join $rtl ae_controller.sv]]
update_compile_order -fileset sources_1
create_bd_design tap
create_bd_cell -type module -reference axis_ae_status ae_status
set f [open [file join $out interface.tsv] w]
puts $f "name\tmode\tvlnv"
foreach p [get_bd_intf_pins -of_objects [get_bd_cells ae_status]] {
    puts $f "$p\t[get_property MODE $p]\t[get_property VLNV $p]"
}
close $f
set f [open [file join $out pins.tsv] w]
foreach p [lsort [get_bd_pins -of_objects [get_bd_cells ae_status]]] {
    puts $f "$p\t[get_property DIR $p]"
}
close $f
if {$mode eq "after"} {
    if {![string equal -nocase [get_property MODE [get_bd_intf_pins ae_status/s_axis]] Monitor]} {error "Tap is not a monitor"}
    foreach p {s_axis_tdata s_axis_tvalid s_axis_tready s_axis_tuser} {
        if {[get_property DIR [get_bd_pins ae_status/$p]] ne "I"} {error "Tap changed direction: $p"}
    }
}
save_bd_design
write_bd_tcl [file join $out design.tcl]
puts "LOCAL6_AE_INTERFACE_${mode}_COMPLETE"
close_project
exit
