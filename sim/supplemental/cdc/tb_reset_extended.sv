`timescale 1ns/1ps
// Component simulation only: ideal gated clock, not an MMCM/DPHY model.
module tb_reset_extended;
  reg clk=0, clock_enable=1;
  always #2.5 if(clock_enable) clk=~clk; else clk=0;
  reg ext_n=0, locked=0;
  wire [0:0] peripheral_n;
  integer pulses=0, low_edges=0, min_edges=100000;
  real low_start=0, duration;
  design_1_rst_clk_wiz_0_200M_0 dut (
    .slowest_sync_clk(clk), .ext_reset_in(ext_n), .aux_reset_in(1'b1),
    .mb_debug_sys_rst(1'b0), .dcm_locked(locked), .mb_reset(),
    .bus_struct_reset(), .peripheral_reset(), .interconnect_aresetn(),
    .peripheral_aresetn(peripheral_n)
  );
  always @(negedge peripheral_n[0]) begin low_start=$realtime; low_edges=0; end
  always @(posedge clk) if(peripheral_n[0]===1'b0) low_edges=low_edges+1;
  always @(posedge peripheral_n[0]) begin
    duration=$realtime-low_start;
    if(low_edges<40) $fatal(1,"Reset released before 40 active rising edges: %0d",low_edges);
    if(low_edges<min_edges) min_edges=low_edges;
    pulses=pulses+1;
    $display("RESET_EVENT count=%0d active_edges=%0d duration_ns=%0.3f",pulses,low_edges,duration);
  end
  task released;
    integer n;
    begin
      n=0;
      while(peripheral_n[0]!==1'b1 && n<200) begin @(posedge clk); #0.1; n=n+1; end
      if(peripheral_n[0]!==1'b1) $fatal(1,"Reset failed to release within 200 clocks");
      repeat(20) @(posedge clk);
    end
  endtask
  task ext_pulse(input integer cycles,input real phase);
    integer previous;
    begin
      previous=pulses;
      @(negedge clk); #(phase); ext_n=0;
      repeat(cycles) @(posedge clk);
      if(peripheral_n[0]!==1'b0) $fatal(1,"Long reset pulse not observed");
      #0.2; ext_n=1; released;
      if(pulses!=previous+1) $fatal(1,"Missing or extra external reset pulse");
    end
  endtask
  task lock_pulse(input integer cycles,input real phase);
    integer previous;
    begin
      previous=pulses;
      @(negedge clk); #(phase); locked=0;
      repeat(cycles) @(posedge clk);
      if(peripheral_n[0]!==1'b0) $fatal(1,"Lock loss not observed");
      #0.2; locked=1; released;
      if(pulses!=previous+1) $fatal(1,"Missing or extra lock reset pulse");
    end
  endtask
  task pause_during_reset(input integer use_lock);
    integer previous;
    begin
      previous=pulses;
      @(negedge clk); #0.3;
      if(use_lock) locked=0; else ext_n=0;
      repeat(24) @(posedge clk);
      #0.1; if(peripheral_n[0]!==1'b0) $fatal(1,"Reset not asserted before pause");
      @(negedge clk); clock_enable=0;
      #100; if(use_lock) locked=1; else ext_n=1;
      #500;
      if(peripheral_n[0]!==1'b0) $fatal(1,"Reset released while clock stopped");
      clock_enable=1; released;
      if(pulses!=previous+1) $fatal(1,"Paused reset event count mismatch");
    end
  endtask
  initial begin
    #200; ext_n=1; #37; locked=1; released;
    ext_pulse(20,0.1); ext_pulse(40,0.1); ext_pulse(80,0.1);
    ext_pulse(20,1.3); ext_pulse(40,1.3); ext_pulse(80,1.3);
    ext_pulse(20,2.4); ext_pulse(40,2.4); ext_pulse(80,2.4);
    ext_pulse(20,4.9); ext_pulse(40,4.9); ext_pulse(80,4.9);
    lock_pulse(20,1.1); lock_pulse(80,4.6);
    pause_during_reset(0); pause_during_reset(1);
    // Reset requested with clock already stopped; require observation on restart.
    @(negedge clk); clock_enable=0; #100; ext_n=0; #500;
    clock_enable=1; repeat(80) @(posedge clk); #0.1;
    if(peripheral_n[0]!==1'b0) $fatal(1,"Reset not observed after clock restart");
    ext_n=1; released;
    if(pulses!=18) $fatal(1,"Expected 18 reset events, got %0d",pulses);
    $display("PASS_RESET_EXTENDED_COMPONENT_ONLY pulses=%0d min_active_edges=%0d",pulses,min_edges);
    $finish;
  end
  initial begin #50000; $fatal(1,"Timeout"); end
endmodule
