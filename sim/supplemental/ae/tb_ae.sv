`timescale 1ns/1ps
module tb_ae;
  reg clk=0; always #2.5 clk=~clk;
  reg resetn=0,valid=0,ready=0,user=0;
  reg [23:0] data=0;
  wire [31:0] status, reference_status;
  integer frames=0,cycles=0;
  axis_ae_status #(.FRAME_PIXELS(64)) dut (
    .aclk(clk),.aresetn(resetn),.s_axis_tdata(data),.s_axis_tvalid(valid),
    .s_axis_tready(ready),.s_axis_tuser(user),.status(status));
  axis_ae_status_reference #(.FRAME_PIXELS(64)) reference_dut (
    .aclk(clk),.aresetn(resetn),.s_axis_tdata(data),.s_axis_tvalid(valid),
    .s_axis_tready(ready),.s_axis_tuser(user),.status(reference_status));
  always @(posedge clk) begin
    #0.1;
    cycles=cycles+1;
    if(status !== reference_status) $fatal(1,"Attribute change altered behavior at cycle %0d",cycles);
    if(resetn && dut.frame_valid) frames=frames+1;
  end
  task automatic frame(input [7:0] gray,input integer stall_pattern,input integer expected_exposure);
    integer i,j,before_frames;
    begin
      before_frames=frames;
      for(i=0;i<64;i=i+1) begin
        @(negedge clk);valid=1;user=(i==0);data={gray,gray,gray};ready=0;
        for(j=0;j<((i+stall_pattern)%4);j=j+1) @(negedge clk);
        ready=1;
      end
      @(negedge clk);valid=0;ready=0;user=0;data=24'hffffff;
      repeat(24) @(negedge clk);
      if(frames != before_frames+1) $fatal(1,"Unexpected frame count under backpressure");
      if(status[31:24] !== gray) $fatal(1,"Mean includes unaccepted pixels: %0d expected %0d",status[31:24],gray);
      if(status[23:16] !== 0 || status[15:0] !== expected_exposure) $fatal(1,"Unexpected exposure update: %h",status);
      $display("PASS_AE_FRAME gray=%0d exposure=%0d",gray,status[15:0]);
    end
  endtask
  task automatic reset;
    begin
      @(negedge clk);resetn=0;valid=0;ready=0;user=0;
      repeat(4) @(negedge clk);
      if(status !== 32'd600) $fatal(1,"Reset state mismatch");
      resetn=1;
    end
  endtask
  integer i;
  initial begin
    reset();
    frame(16,0,676);
    frame(112,1,676);
    frame(240,2,592);
    // A stalled SOF must not start a new frame or alter the stable output.
    @(negedge clk);valid=1;ready=0;user=1;data=0;
    repeat(20) @(negedge clk);
    if(status !== {8'd240,8'd0,16'd592}) $fatal(1,"Stalled SOF changed output");
    $display("PASS_AE_STALLED_SOF");
    // Reset while a partial frame is present; subsequent frame starts clean.
    for(i=0;i<20;i=i+1) begin
      @(negedge clk);valid=1;ready=1;user=(i==0);data=0;
    end
    reset();
    frame(112,3,600);
    if(frames != 4) $fatal(1,"Spurious frame after partial-frame reset");
    $display("PASS_AE_MONITOR_BEHAVIOR frames=%0d cycles=%0d",frames,cycles);
    $finish;
  end
  initial begin #20000;$fatal(1,"Timeout");end
endmodule
