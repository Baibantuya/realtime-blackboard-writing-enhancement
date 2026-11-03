// Passive observability only. Counters snapshot on PS observing ap_done.
`timescale 1ns/1ps
module wb_rectify_monitor(
 (* X_INTERFACE_PARAMETER="ASSOCIATED_BUSIF s_axi, ASSOCIATED_RESET resetn", X_INTERFACE_INFO="xilinx.com:signal:clock:1.0 clk CLK" *) input wire clk,
 (* X_INTERFACE_PARAMETER="POLARITY ACTIVE_LOW", X_INTERFACE_INFO="xilinx.com:signal:reset:1.0 resetn RST" *) input wire resetn,
 (* X_INTERFACE_PARAMETER="XIL_INTERFACENAME s_axi, PROTOCOL AXI4LITE, DATA_WIDTH 32, ADDR_WIDTH 8", X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi AWADDR" *) input wire [7:0] s_axi_AWADDR,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi AWVALID" *) input wire s_axi_AWVALID,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi AWREADY" *) output wire s_axi_AWREADY,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi WDATA" *) input wire [31:0] s_axi_WDATA,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi WSTRB" *) input wire [3:0] s_axi_WSTRB,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi WVALID" *) input wire s_axi_WVALID,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi WREADY" *) output wire s_axi_WREADY,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi BRESP" *) output wire [1:0] s_axi_BRESP,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi BVALID" *) output reg s_axi_BVALID,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi BREADY" *) input wire s_axi_BREADY,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi ARADDR" *) input wire [7:0] s_axi_ARADDR,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi ARVALID" *) input wire s_axi_ARVALID,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi ARREADY" *) output wire s_axi_ARREADY,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi RDATA" *) output reg [31:0] s_axi_RDATA,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi RRESP" *) output wire [1:0] s_axi_RRESP,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi RVALID" *) output reg s_axi_RVALID,
 (* X_INTERFACE_INFO="xilinx.com:interface:aximm:1.0 s_axi RREADY" *) input wire s_axi_RREADY,
 (* X_INTERFACE_IGNORE="true" *) input wire ctl_awvalid,ctl_awready,(* X_INTERFACE_IGNORE="true" *) input wire [6:0] ctl_awaddr,
 (* X_INTERFACE_IGNORE="true" *) input wire ctl_wvalid,ctl_wready,(* X_INTERFACE_IGNORE="true" *) input wire [31:0] ctl_wdata,
 (* X_INTERFACE_IGNORE="true" *) input wire ctl_arvalid,ctl_arready,(* X_INTERFACE_IGNORE="true" *) input wire [6:0] ctl_araddr,
 (* X_INTERFACE_IGNORE="true" *) input wire ctl_rvalid,ctl_rready,(* X_INTERFACE_IGNORE="true" *) input wire [31:0] ctl_rdata,
 input wire arvalid,arready,input wire [7:0] arlen,
 input wire rvalid,rready,rlast,
 input wire awvalid,awready,wvalid,wready,wlast,bvalid,bready,
 (* MARK_DEBUG="TRUE", KEEP="TRUE" *) output wire [511:0] stats,
 (* MARK_DEBUG="TRUE", KEEP="TRUE" *) output wire frame_done
);
 reg [6:0] awaddr,araddr;
 reg active;
 reg [31:0] cycles,reads,ar_stall,beats,r_gap,r_stall,writes,wbeats,w_stall,b_stall,outstanding,peak;
 reg [511:0] saved;
 reg aw_pending,w_pending;
 wire aw_fire=ctl_awvalid&&ctl_awready;
 wire ar_fire=ctl_arvalid&&ctl_arready;
 wire start=ctl_wvalid&&ctl_wready&&ctl_wdata[0]&&((aw_fire?ctl_awaddr:awaddr)==0);
 wire done=active&&ctl_rvalid&&ctl_rready&&ctl_rdata[1]&&(araddr==0);
 wire read_issue=arvalid&&arready,read_finish=rvalid&&rready&&rlast;
 assign frame_done=done;
 assign stats=saved;
 assign s_axi_AWREADY=!aw_pending&&!s_axi_BVALID;
 assign s_axi_WREADY=!w_pending&&!s_axi_BVALID;
 assign s_axi_BRESP=2'b10; // read-only bank; writes acknowledged as SLVERR
 assign s_axi_ARREADY=!s_axi_RVALID;
 assign s_axi_RRESP=2'b00;
 always @(posedge clk) begin
  if(!resetn)begin s_axi_RVALID<=0;s_axi_BVALID<=0;s_axi_RDATA<=0;aw_pending<=0;w_pending<=0;end
  else begin
   if(s_axi_AWVALID&&s_axi_AWREADY)aw_pending<=1;
   if(s_axi_WVALID&&s_axi_WREADY)w_pending<=1;
   if(!s_axi_BVALID&&aw_pending&&w_pending)s_axi_BVALID<=1;
   if(s_axi_BVALID&&s_axi_BREADY)begin s_axi_BVALID<=0;aw_pending<=0;w_pending<=0;end
   if(s_axi_RVALID&&s_axi_RREADY)s_axi_RVALID<=0;
   if(s_axi_ARVALID&&s_axi_ARREADY)begin
    s_axi_RVALID<=1;
    if(s_axi_ARADDR[7:2]==0)s_axi_RDATA<=32'h57424436;
    else if(s_axi_ARADDR[7:2]<16)s_axi_RDATA<=saved[511-32*s_axi_ARADDR[5:2]-:32];
    else s_axi_RDATA<=0;
   end
  end
 end
 always @(posedge clk) begin
  if(!resetn)begin
   awaddr<=0;araddr<=0;active<=0;saved<=0;
   cycles<=0;reads<=0;ar_stall<=0;beats<=0;r_gap<=0;r_stall<=0;
   writes<=0;wbeats<=0;w_stall<=0;b_stall<=0;outstanding<=0;peak<=0;
  end else begin
   if(aw_fire)awaddr<=ctl_awaddr;
   if(ar_fire)araddr<=ctl_araddr;
   if(start)begin
    active<=1;cycles<=0;reads<=0;ar_stall<=0;beats<=0;r_gap<=0;r_stall<=0;
    writes<=0;wbeats<=0;w_stall<=0;b_stall<=0;outstanding<=0;peak<=0;
   end else if(active)begin
    cycles<=cycles+1;
    if(read_issue)reads<=reads+1;
    if(arvalid&&!arready)ar_stall<=ar_stall+1;
    if(rvalid&&rready)beats<=beats+1;
    if(outstanding!=0&&!rvalid)r_gap<=r_gap+1;
    if(rvalid&&!rready)r_stall<=r_stall+1;
    if(awvalid&&awready)writes<=writes+1;
    if(wvalid&&wready)wbeats<=wbeats+1;
    if(wvalid&&!wready)w_stall<=w_stall+1;
    if(bvalid&&!bready)b_stall<=b_stall+1;
    if(read_issue&&!read_finish)outstanding<=outstanding+1;
    if(read_finish&&!read_issue&&outstanding!=0)outstanding<=outstanding-1;
    if(outstanding>peak)peak<=outstanding;
    if(done)begin
     active<=0;
     saved<={32'h57424436,cycles,reads,ar_stall,beats,r_gap,r_stall,writes,wbeats,w_stall,b_stall,peak,128'd0};
    end
   end
  end
 end
endmodule
