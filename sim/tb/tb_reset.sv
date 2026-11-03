`timescale 1ns/1ps
// Component-only simulation of the generated 2025.2 reset IP.
// Continuous 200 MHz clock; does not model MMCM, DPHY or board power-up.
module tb_reset;
  reg clk=0;
  always #2.5 clk=~clk;
  reg ext_n=0, locked=0;
  wire [0:0] peripheral_n;
  integer pulses=0;
  real low_start=0.0;
  real duration;
  design_1_rst_clk_wiz_0_200M_0 dut (
    .slowest_sync_clk(clk), .ext_reset_in(ext_n), .aux_reset_in(1'b1),
    .mb_debug_sys_rst(1'b0), .dcm_locked(locked), .mb_reset(),
    .bus_struct_reset(), .peripheral_reset(), .interconnect_aresetn(),
    .peripheral_aresetn(peripheral_n)
  );
  always @(negedge peripheral_n[0]) low_start=$realtime;
  always @(posedge peripheral_n[0]) begin
    duration=$realtime-low_start;
    $display("RESET_PULSE ns=%0.3f cycles200MHz=%0.3f end=%0.3f",duration,duration/5.0,$realtime);
    if (duration < 200.0) $fatal(1,"MIPI video reset pulse shorter than 40 dphy clock cycles");
    pulses=pulses+1;
  end
  task ext_pulse(input integer cycles);
    begin
      #1.3; ext_n=0; #(5.0*cycles); ext_n=1;
      #800;
      if(peripheral_n!==1'b1) $fatal(1,"Reset failed to release");
    end
  endtask
  task lock_pulse(input integer cycles);
    begin
      #1.7; locked=0; #(5.0*cycles); locked=1;
      #800;
      if(peripheral_n!==1'b1) $fatal(1,"Reset failed to release after lock returned");
    end
  endtask
  initial begin
    #100; ext_n=1; #37; locked=1; #800;
    ext_pulse(1); ext_pulse(2); ext_pulse(4); ext_pulse(8); ext_pulse(16); ext_pulse(80);
    lock_pulse(1); lock_pulse(4); lock_pulse(80);
    if(pulses<5) $fatal(1,"Too few output reset events observed");
    $display("PASS_RESET_COMPONENT_ONLY pulses=%0d; not board/DPHY proof",pulses);
    $finish;
  end
  initial begin #15000; $fatal(1,"Timeout"); end
endmodule
