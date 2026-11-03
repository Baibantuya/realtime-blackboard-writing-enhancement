# Read-only routed-netlist review; no constraints, waivers or netlist edits.
set here [file dirname [file normalize [info script]]]
set root [file dirname [file dirname $here]]
set out [file join $here structural]
if {[file exists $out]} {error "Retain previous structural evidence"}
file mkdir $out
set_param general.maxThreads 2
open_checkpoint [file join $root r5 i routed.dcp]
set fh [open [file join $root r5 i methodology.rpt] r]
set method [read $fh]; close $fh
set matches [regexp -all -inline {LUT cell ([^,\n]+), with} $method]
if {[llength $matches]!=8} {error "Expected four LUTAR objects"}
set fh [open [file join $out reset_structure.tsv] w]
puts $fh "kind\tobject\tref_or_property\tvalue"
proc cellrow {fh kind c} {
  puts $fh "$kind\t[get_property NAME $c]\tREF_NAME\t[get_property REF_NAME $c]"
  foreach prop {INIT ASYNC_REG} {
    if {[lsearch -exact [list_property $c] $prop]>=0} {puts $fh "$kind\t[get_property NAME $c]\t$prop\t[get_property $prop $c]"}
  }
}
foreach {matched name} $matches {
  set c [get_cells -quiet -hier -filter [format {NAME == "%s"} $name]]
  if {[llength $c]!=1} {error "Missing or ambiguous LUT $name"}
  cellrow $fh LUT $c
  foreach pin [get_pins -of_objects $c -filter {DIRECTION == IN}] {
    foreach driver [all_fanin -flat -startpoints_only -to $pin] {
      puts $fh "fanin\t[get_property NAME $pin]\tstart\t[get_property NAME $driver]"
      foreach d [get_cells -quiet -of_objects $driver] {cellrow $fh source $d}
    }
  }
  foreach op [get_pins -of_objects $c -filter {DIRECTION == OUT}] {
    set eps [all_fanout -flat -endpoints_only -from $op]
    if {[llength $eps]>500} {error "Unexpected unbounded reset fanout"}
    foreach ep $eps {
      puts $fh "fanout\t[get_property NAME $op]\tendpoint\t[get_property NAME $ep]"
      foreach sc [get_cells -quiet -of_objects $ep] {
        cellrow $fh sink $sc
        foreach cp [get_pins -of_objects $sc -filter {IS_CLOCK == 1}] {puts $fh "clock\t[get_property NAME $sc]\tclocks\t[get_clocks -quiet -of_objects $cp]"}
      }
    }
  }
}
close $fh
set fh [open [file join $out config_sync_structure.tsv] w]
puts $fh "kind\tobject\tref_or_property\tvalue"
set count 0
foreach c [get_cells -hier -filter {IS_PRIMITIVE == 1 && (NAME =~ *xpm_array_single_04* || NAME =~ *xpm_vcen* || NAME =~ *active_lanes_reg* || NAME =~ *vc_en_reg*)}] {
  incr count
  cellrow $fh config $c
  foreach p [get_pins -of_objects $c -filter {REF_PIN_NAME == D || IS_CLOCK == 1}] {
    set nets [get_nets -quiet -of_objects $p]
    set drv [get_pins -quiet -of_objects $nets -filter {DIRECTION == OUT}]
    puts $fh "pin\t[get_property NAME $p]\tdrivers\t$drv"
    if {[get_property IS_CLOCK $p]} {puts $fh "clock\t[get_property NAME $p]\tclocks\t[get_clocks -quiet -of_objects $p]"}
  }
}
close $fh
if {$count<18} {error "Expected configuration synchronizer cells absent"}
puts "LOCAL6_CDC_STRUCTURE_REVIEW_COMPLETE count=$count; no waivers or modifications"
close_design
exit
