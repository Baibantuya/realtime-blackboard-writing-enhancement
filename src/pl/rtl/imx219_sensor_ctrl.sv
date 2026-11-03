// IMX219 register sequencer and frame-boundary AE writer.
// Mode values follow imx219_1080p30_regs(1).h. Verify the camera module and
// clock/lane wiring before enabling the sensor. The integrated Linux flow uses
// the kernel driver as its only I2C master; this sequencer is a standalone path.
module imx219_sensor_ctrl #(parameter integer CLK_HZ=100_000_000) (
    input wire clk, input wire resetn,
    input wire ae_update, input wire [15:0] ae_exposure, input wire [7:0] ae_gain,
    output reg init_done, output reg busy,
    output wire sensor_resetn, output wire i2c_scl, inout wire i2c_sda
);
    reg launch; reg [15:0] wr_addr; reg [7:0] wr_data;
    wire wr_done, wr_busy, wr_nack;
    reg [6:0] index;
    reg [15:0] exp_latched; reg [7:0] gain_latched;
    reg inflight; reg [1:0] ae_step;
    reg [19:0] startup_count;
    reg startup_done;
    reg sensor_reset_release;
    assign sensor_resetn=sensor_reset_release;
    imx219_i2c_write #(.CLK_HZ(CLK_HZ),.I2C_HZ(100_000)) i2c (
      .clk(clk),.resetn(resetn),.start(launch),.reg_addr(wr_addr),.reg_data(wr_data),
      .busy(wr_busy),.done(wr_done),.nack(wr_nack),.scl(i2c_scl),.sda(i2c_sda));

    task automatic select_init(input [6:0] n);
      begin
        case(n)
          0:  begin wr_addr=16'h0100; wr_data=8'h00; end // standby
          1:  begin wr_addr=16'h30EB; wr_data=8'h05; end
          2:  begin wr_addr=16'h30EB; wr_data=8'h0C; end
          3:  begin wr_addr=16'h300A; wr_data=8'hFF; end
          4:  begin wr_addr=16'h300B; wr_data=8'hFF; end
          5:  begin wr_addr=16'h30EB; wr_data=8'h05; end
          6:  begin wr_addr=16'h30EB; wr_data=8'h09; end
          7:  begin wr_addr=16'h0114; wr_data=8'h01; end
          8:  begin wr_addr=16'h0128; wr_data=8'h00; end
          9:  begin wr_addr=16'h012A; wr_data=8'h18; end // as supplied: INCK register 0x1800
          10: begin wr_addr=16'h012B; wr_data=8'h00; end
          11: begin wr_addr=16'h0162; wr_data=8'h0D; end
          12: begin wr_addr=16'h0163; wr_data=8'h78; end
          13: begin wr_addr=16'h0164; wr_data=8'h02; end
          14: begin wr_addr=16'h0165; wr_data=8'hA8; end
          15: begin wr_addr=16'h0166; wr_data=8'h0A; end
          16: begin wr_addr=16'h0167; wr_data=8'h27; end
          17: begin wr_addr=16'h0168; wr_data=8'h02; end
          18: begin wr_addr=16'h0169; wr_data=8'hB4; end
          19: begin wr_addr=16'h016A; wr_data=8'h06; end
          20: begin wr_addr=16'h016B; wr_data=8'hEB; end
          21: begin wr_addr=16'h016C; wr_data=8'h07; end // 1920 pixels
          22: begin wr_addr=16'h016D; wr_data=8'h80; end
          23: begin wr_addr=16'h016E; wr_data=8'h04; end // 1080 lines
          24: begin wr_addr=16'h016F; wr_data=8'h38; end
          25: begin wr_addr=16'h0170; wr_data=8'h01; end
          26: begin wr_addr=16'h0171; wr_data=8'h01; end
          27: begin wr_addr=16'h0174; wr_data=8'h00; end
          28: begin wr_addr=16'h0175; wr_data=8'h00; end
          29: begin wr_addr=16'h0301; wr_data=8'h05; end
          30: begin wr_addr=16'h0303; wr_data=8'h01; end
          31: begin wr_addr=16'h0304; wr_data=8'h03; end
          32: begin wr_addr=16'h0305; wr_data=8'h03; end
          33: begin wr_addr=16'h0306; wr_data=8'h00; end
          34: begin wr_addr=16'h0307; wr_data=8'h39; end
          35: begin wr_addr=16'h030B; wr_data=8'h01; end
          36: begin wr_addr=16'h030C; wr_data=8'h00; end
          37: begin wr_addr=16'h030D; wr_data=8'h72; end
          38: begin wr_addr=16'h0624; wr_data=8'h07; end
          39: begin wr_addr=16'h0625; wr_data=8'h80; end
          40: begin wr_addr=16'h0626; wr_data=8'h04; end
          41: begin wr_addr=16'h0627; wr_data=8'h38; end
          42: begin wr_addr=16'h455E; wr_data=8'h00; end
          43: begin wr_addr=16'h471E; wr_data=8'h4B; end
          44: begin wr_addr=16'h4767; wr_data=8'h0F; end
          45: begin wr_addr=16'h4750; wr_data=8'h14; end
          46: begin wr_addr=16'h4540; wr_data=8'h00; end
          47: begin wr_addr=16'h47B4; wr_data=8'h14; end
          48: begin wr_addr=16'h4713; wr_data=8'h30; end
          49: begin wr_addr=16'h478B; wr_data=8'h10; end
          50: begin wr_addr=16'h478F; wr_data=8'h10; end
          51: begin wr_addr=16'h4793; wr_data=8'h10; end
          52: begin wr_addr=16'h4797; wr_data=8'h0E; end
          53: begin wr_addr=16'h479B; wr_data=8'h0E; end
          54: begin wr_addr=16'h018C; wr_data=8'h0A; end // RAW10 data type
          55: begin wr_addr=16'h018D; wr_data=8'h0A; end
          56: begin wr_addr=16'h0309; wr_data=8'h0A; end
          57: begin wr_addr=16'h0160; wr_data=8'h06; end // FLL = 1763
          58: begin wr_addr=16'h0161; wr_data=8'hE3; end
          59: begin wr_addr=16'h015A; wr_data=8'h02; end // initial exposure = 600 lines
          60: begin wr_addr=16'h015B; wr_data=8'h58; end
          61: begin wr_addr=16'h0157; wr_data=8'h00; end // analogue gain code
          62: begin wr_addr=16'h0158; wr_data=8'h01; end // digital gain = 0x0100
          63: begin wr_addr=16'h0159; wr_data=8'h00; end
          64: begin wr_addr=16'h0172; wr_data=8'h00; end
          65: begin wr_addr=16'h0600; wr_data=8'h00; end
          66: begin wr_addr=16'h0100; wr_data=8'h01; end // start stream after table
          default: begin wr_addr=0; wr_data=0; end
        endcase
      end
    endtask

    always @(posedge clk) begin
      if (!resetn) begin
        launch<=0; init_done<=0; busy<=0; index<=0; inflight<=0; ae_step<=0;
        startup_count<=0; startup_done<=0; sensor_reset_release<=0;
        wr_addr<=0; wr_data<=0; exp_latched<=16'd600; gain_latched<=0;
      end else begin
        launch<=0;
        if (!startup_done) begin
          if (!sensor_reset_release) begin
            if (startup_count==20'd9999) begin sensor_reset_release<=1; startup_count<=0; end
            else startup_count<=startup_count+1'b1;
          end else if (startup_count==20'd619999) begin startup_done<=1; startup_count<=startup_count; end
          else startup_count<=startup_count+1'b1;
        end else if (!init_done) begin
          busy<=1;
          if (!inflight && !wr_busy && index<=66) begin select_init(index); launch<=1; inflight<=1; end
          if (wr_done) begin
            inflight<=0;
            if (!wr_nack) begin
              if (index==66) begin init_done<=1; busy<=0; end
              else index<=index+1'b1;
            end // NACK holds the sequence for a visible, non-ready fault.
          end
        end else begin
          if (ae_update && !busy && !inflight) begin exp_latched<=ae_exposure; gain_latched<=ae_gain; ae_step<=0; busy<=1; end
          if (busy && !inflight && !wr_busy) begin
            case(ae_step)
              0: begin wr_addr<=16'h015A; wr_data<=exp_latched[15:8]; end
              1: begin wr_addr<=16'h015B; wr_data<=exp_latched[7:0]; end
              default: begin wr_addr<=16'h0157; wr_data<=gain_latched; end
            endcase
            launch<=1; inflight<=1;
          end
          if (wr_done) begin
            inflight<=0;
            if (wr_nack || ae_step==2) begin busy<=0; ae_step<=0; end
            else ae_step<=ae_step+1'b1;
          end
        end
      end
    end
endmodule
