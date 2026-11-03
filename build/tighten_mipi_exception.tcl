# Adopted only in isolated impl2, based on diagnostic3 results.
# Read with an open design, then call tighten_mipi_exception <new evidence dir>.
namespace eval reviewed_mipi {
proc clock_signature {path} {
    set f [open $path w]; set rows {}
    foreach c [lsort [get_clocks]] {
        set pins [lsort [get_property SOURCE_PINS $c]]
        if {[llength $pins] == 0} {error "Clock has no physical source pins: $c"}
        set master [get_property MASTER_CLOCK $c]; set masterpins {}
        if {$master ne ""} {set masterpins [lsort [get_property SOURCE_PINS [get_clocks $master]]]}
        set row [list $pins $masterpins]
        foreach p {PERIOD WAVEFORM IS_GENERATED DIVIDE_BY MULTIPLY_BY EDGES EDGE_SHIFT PHASE INPUT_JITTER} {
            if {[lsearch -exact [list_property $c] $p] >= 0} {lappend row [list $p [get_property $p $c]]}
        }
        puts $f [list $c $master $row]
        lappend rows $row
    }
    close $f
    return [lsort $rows]
}

proc tighten {out} {
if {[file exists $out]} {error "Preserve earlier constraint evidence"}
file mkdir $out
update_timing
set clocks_before {}
set clocks_before [clock_signature [file join $out clock_definitions_before.txt]]
write_xdc -type timing [file join $out original.xdc]
set f [open [file join $out original.xdc] r]; set original [read $f]; close $f
# These two automatically renamed PHY clocks must not be referenced by name.
if {[string first {clkoutphy_out} $original] >= 0} {error "Export refers to auto-clock labels; do not allow a rename"}
set lines {}; set removed 0
set target {set_clock_groups -asynchronous -group [get_clocks *FIFO_WRCLK_OUT] -group [get_clocks -of_objects [get_ports -scoped_to_current_instance video_aclk]]}
foreach line [split $original "\n"] {
    if {[string trim $line] eq $target} {incr removed} else {lappend lines $line}
}
if {$removed != 1} {error "Expected exactly one identified broad clock group, got $removed"}
set f [open [file join $out stricter_diagnostic.xdc] w]; puts $f [join $lines "\n"]; close $f
reset_timing -invalid -clock_reservation
read_xdc -no_add [file join $out stricter_diagnostic.xdc]
current_instance -quiet
update_timing
set clocks_after {}
set clocks_after [clock_signature [file join $out clock_definitions_after.txt]]
set f [open [file join $out clock_lists.txt] w]; puts $f "before: $clocks_before\nafter: $clocks_after"; close $f
if {$clocks_before ne $clocks_after} {error "Diagnostic changed clock definitions"}

puts "STRICTER_MIPI_CONSTRAINT_APPLIED_CLOCK_SIGNATURES_UNCHANGED"
}
}
proc tighten_mipi_exception {out} {reviewed_mipi::tighten $out}
