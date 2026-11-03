// Single-register IMX219 I2C write: 7-bit address 0x10, 16-bit register + data.
// Open-drain SDA: drive low or release; external pull-up is required.
module imx219_i2c_write #(
    parameter integer CLK_HZ=100_000_000, parameter integer I2C_HZ=100_000
) (
    input wire clk, input wire resetn,
    input wire start, input wire [15:0] reg_addr, input wire [7:0] reg_data,
    output reg busy, output reg done, output reg nack,
    output reg scl, inout wire sda
);
    localparam integer DIV = CLK_HZ/(I2C_HZ*4);
    reg [15:0] divcnt; reg tick;
    reg sda_low; assign sda = sda_low ? 1'b0 : 1'bz;
    wire sda_in=sda;
    reg [4:0] phase; reg [3:0] bitno; reg [1:0] byte_index; reg [31:0] payload;
    reg [2:0] state;
    localparam IDLE=0, START=1, BIT=2, ACK=3, STOP=4;
    always @(posedge clk) begin
      if (!resetn) begin divcnt<=0; tick<=0; end
      else if (divcnt==DIV-1) begin divcnt<=0; tick<=1; end
      else begin divcnt<=divcnt+1'b1; tick<=0; end
    end
    always @(posedge clk) begin
      if (!resetn) begin busy<=0; done<=0; nack<=0; scl<=1; sda_low<=0; phase<=0; bitno<=0; payload<=0; state<=IDLE; end
      else begin
        done<=0;
        if (state==IDLE && start && !busy) begin
          payload<={8'h20,reg_addr,reg_data}; busy<=1; nack<=0; phase<=0; bitno<=0; byte_index<=0; state<=START;
        end else if (tick) begin
          case(state)
            START: case(phase)
              0: begin scl<=1; sda_low<=0; phase<=1; end
              1: begin sda_low<=1; phase<=2; end
              default: begin scl<=0; phase<=0; bitno<=0; state<=BIT; end
            endcase
            BIT: case(phase)
              0: begin scl<=0; sda_low<=~payload[31-(byte_index*8)-bitno]; phase<=1; end
              1: begin scl<=1; phase<=2; end
              default: begin scl<=0; phase<=0; if(bitno==7) begin bitno<=0; state<=ACK; end else bitno<=bitno+1'b1; end
            endcase
            ACK: case(phase)
              0: begin scl<=0; sda_low<=0; phase<=1; end
              1: begin scl<=1; if (sda_in) nack<=1; phase<=2; end
              default: begin scl<=0; phase<=0; if(byte_index==3) state<=STOP; else begin byte_index<=byte_index+1'b1; state<=BIT; end end
            endcase
            STOP: case(phase)
              0: begin scl<=0; sda_low<=1; phase<=1; end
              1: begin scl<=1; phase<=2; end
              default: begin sda_low<=0; busy<=0; done<=1; state<=IDLE; phase<=0; end
            endcase
            default: state<=IDLE;
          endcase
        end
      end
    end
endmodule
