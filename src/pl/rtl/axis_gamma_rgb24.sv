// AXI4-Stream Video RGB888 gamma LUT. One RGB pixel per beat, RGB in [23:0].
// SOF is TUSER[0], EOL is TLAST. LUT is a compact gamma≈0.5 default curve.
module axis_gamma_rgb24 (
    input wire aclk, input wire aresetn,
    input wire [23:0] s_tdata, input wire s_tvalid, output wire s_tready,
    input wire s_tuser, input wire s_tlast,
    output reg [23:0] m_tdata, output reg m_tvalid, input wire m_tready,
    output reg m_tuser, output reg m_tlast
);
    function automatic [7:0] gamma_lut(input [7:0] x);
        reg [7:0] lo, hi, mid;
        reg [15:0] scaled, square;
        integer n;
        begin
            // Integer sqrt mapping: brighter output, monotonic and deterministic.
            scaled = x * 16'd255;
            lo=0; hi=255;
            for (n=0; n<8; n=n+1) begin
                mid=({1'b0,lo}+{1'b0,hi}+9'd1)>>1;
                square={8'd0,mid}*{8'd0,mid};
                if (square<=scaled) lo=mid;
                else hi=mid-1'b1;
            end
            gamma_lut=lo;
        end
    endfunction
    assign s_tready = ~m_tvalid | m_tready;
    always @(posedge aclk) begin
        if (!aresetn) begin
            m_tvalid <= 0; m_tdata <= 0; m_tuser <= 0; m_tlast <= 0;
        end else if (s_tready) begin
            m_tvalid <= s_tvalid;
            if (s_tvalid) begin
                m_tdata <= {gamma_lut(s_tdata[23:16]), gamma_lut(s_tdata[15:8]), gamma_lut(s_tdata[7:0])};
                m_tuser <= s_tuser; m_tlast <= s_tlast;
            end
        end
    end
endmodule
