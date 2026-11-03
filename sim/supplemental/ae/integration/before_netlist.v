// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2025.2 (win64) Build 6299465 Fri Nov 14 19:35:11 GMT 2025
// Date        : Wed Oct 28 23:53:49 2026
// Host        : 白板涂鸦 running 64-bit major release  (build 9200)
// Command     : write_verilog -mode funcsim W:/local6/ae/integration/before_netlist.v
// Design      : axis_ae_status
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xck26-sfvc784-2LV-c
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module ae_controller
   (\coarse_integration_reg[6]_0 ,
    \coarse_integration_reg[5]_0 ,
    \coarse_integration_reg[4]_0 ,
    \coarse_integration_reg[3]_0 ,
    Q,
    \coarse_integration_reg[15]_0 ,
    \coarse_integration_reg[13]_0 ,
    \coarse_integration_reg[14]_0 ,
    \coarse_integration_reg[12]_0 ,
    \coarse_integration_reg[10]_0 ,
    \coarse_integration_reg[8]_0 ,
    \coarse_integration_reg[7]_0 ,
    \coarse_integration_reg[9]_0 ,
    \coarse_integration_reg[11]_0 ,
    coarse_integration23_in,
    \analog_gain_reg[5]_0 ,
    \coarse_integration_reg[2]_0 ,
    \coarse_integration_reg[1]_0 ,
    \coarse_integration_reg[0]_0 ,
    \analog_gain_reg[6]_0 ,
    update_valid_reg_0,
    \analog_gain_reg[7]_0 ,
    S,
    update_valid_reg_1,
    \coarse_integration_reg[15]_1 ,
    clear,
    aclk,
    frame_valid,
    E);
  output \coarse_integration_reg[6]_0 ;
  output \coarse_integration_reg[5]_0 ;
  output \coarse_integration_reg[4]_0 ;
  output \coarse_integration_reg[3]_0 ;
  output [4:0]Q;
  output \coarse_integration_reg[15]_0 ;
  output \coarse_integration_reg[13]_0 ;
  output \coarse_integration_reg[14]_0 ;
  output \coarse_integration_reg[12]_0 ;
  output \coarse_integration_reg[10]_0 ;
  output \coarse_integration_reg[8]_0 ;
  output \coarse_integration_reg[7]_0 ;
  output \coarse_integration_reg[9]_0 ;
  output \coarse_integration_reg[11]_0 ;
  output coarse_integration23_in;
  output \analog_gain_reg[5]_0 ;
  output \coarse_integration_reg[2]_0 ;
  output \coarse_integration_reg[1]_0 ;
  output \coarse_integration_reg[0]_0 ;
  output \analog_gain_reg[6]_0 ;
  output update_valid_reg_0;
  input \analog_gain_reg[7]_0 ;
  input [1:0]S;
  input update_valid_reg_1;
  input \coarse_integration_reg[15]_1 ;
  input clear;
  input aclk;
  input frame_valid;
  input [0:0]E;

  wire [0:0]E;
  wire [4:0]Q;
  wire [1:0]S;
  wire _carry__0_i_10_n_0;
  wire _carry__0_i_11_n_0;
  wire _carry__0_i_12_n_0;
  wire _carry__0_i_13_n_0;
  wire _carry__0_i_14_n_0;
  wire _carry__0_i_15_n_0;
  wire _carry__0_i_1_n_0;
  wire _carry__0_i_2_n_0;
  wire _carry__0_i_3_n_0;
  wire _carry__0_i_4_n_0;
  wire _carry__0_i_5_n_0;
  wire _carry__0_i_6_n_0;
  wire _carry__0_i_7_n_0;
  wire _carry__0_i_8_n_0;
  wire _carry__0_i_9_n_0;
  wire _carry__0_n_0;
  wire _carry__0_n_1;
  wire _carry__0_n_2;
  wire _carry__0_n_3;
  wire _carry__0_n_4;
  wire _carry__0_n_5;
  wire _carry__0_n_6;
  wire _carry__0_n_7;
  wire _carry_i_10_n_0;
  wire _carry_i_11_n_0;
  wire _carry_i_12_n_0;
  wire _carry_i_1_n_0;
  wire _carry_i_2_n_0;
  wire _carry_i_3_n_0;
  wire _carry_i_4_n_0;
  wire _carry_i_5_n_0;
  wire _carry_i_6_n_0;
  wire _carry_i_7_n_0;
  wire _carry_i_8_n_0;
  wire _carry_i_9_n_0;
  wire _carry_n_0;
  wire _carry_n_1;
  wire _carry_n_2;
  wire _carry_n_3;
  wire _carry_n_4;
  wire _carry_n_5;
  wire _carry_n_6;
  wire _carry_n_7;
  wire aclk;
  wire analog_gain0_carry_i_2_n_0;
  wire analog_gain0_carry_i_3_n_0;
  wire analog_gain0_carry_i_6_n_0;
  wire analog_gain0_carry_n_10;
  wire analog_gain0_carry_n_11;
  wire analog_gain0_carry_n_12;
  wire analog_gain0_carry_n_13;
  wire analog_gain0_carry_n_14;
  wire analog_gain0_carry_n_3;
  wire analog_gain0_carry_n_4;
  wire analog_gain0_carry_n_5;
  wire analog_gain0_carry_n_6;
  wire analog_gain0_carry_n_7;
  wire \analog_gain[7]_i_7_n_0 ;
  wire \analog_gain[7]_i_8_n_0 ;
  wire \analog_gain[7]_i_9_n_0 ;
  wire \analog_gain_reg[5]_0 ;
  wire \analog_gain_reg[6]_0 ;
  wire \analog_gain_reg[7]_0 ;
  wire clear;
  wire [15:0]coarse_integration0;
  wire coarse_integration23_in;
  wire \coarse_integration[0]_i_1_n_0 ;
  wire \coarse_integration[10]_i_1_n_0 ;
  wire \coarse_integration[11]_i_1_n_0 ;
  wire \coarse_integration[12]_i_1_n_0 ;
  wire \coarse_integration[13]_i_1_n_0 ;
  wire \coarse_integration[14]_i_1_n_0 ;
  wire \coarse_integration[15]_i_10_n_0 ;
  wire \coarse_integration[15]_i_11_n_0 ;
  wire \coarse_integration[15]_i_12_n_0 ;
  wire \coarse_integration[15]_i_13_n_0 ;
  wire \coarse_integration[15]_i_14_n_0 ;
  wire \coarse_integration[15]_i_15_n_0 ;
  wire \coarse_integration[15]_i_16_n_0 ;
  wire \coarse_integration[15]_i_17_n_0 ;
  wire \coarse_integration[15]_i_18_n_0 ;
  wire \coarse_integration[15]_i_1_n_0 ;
  wire \coarse_integration[15]_i_2_n_0 ;
  wire \coarse_integration[15]_i_3_n_0 ;
  wire \coarse_integration[15]_i_6_n_0 ;
  wire \coarse_integration[15]_i_7_n_0 ;
  wire \coarse_integration[15]_i_8_n_0 ;
  wire \coarse_integration[15]_i_9_n_0 ;
  wire \coarse_integration[1]_i_1_n_0 ;
  wire \coarse_integration[2]_i_1_n_0 ;
  wire \coarse_integration[3]_i_1_n_0 ;
  wire \coarse_integration[4]_i_1_n_0 ;
  wire \coarse_integration[5]_i_1_n_0 ;
  wire \coarse_integration[6]_i_1_n_0 ;
  wire \coarse_integration[7]_i_10_n_0 ;
  wire \coarse_integration[7]_i_11_n_0 ;
  wire \coarse_integration[7]_i_12_n_0 ;
  wire \coarse_integration[7]_i_13_n_0 ;
  wire \coarse_integration[7]_i_14_n_0 ;
  wire \coarse_integration[7]_i_15_n_0 ;
  wire \coarse_integration[7]_i_16_n_0 ;
  wire \coarse_integration[7]_i_17_n_0 ;
  wire \coarse_integration[7]_i_18_n_0 ;
  wire \coarse_integration[7]_i_19_n_0 ;
  wire \coarse_integration[7]_i_1_n_0 ;
  wire \coarse_integration[7]_i_4_n_0 ;
  wire \coarse_integration[7]_i_5_n_0 ;
  wire \coarse_integration[7]_i_6_n_0 ;
  wire \coarse_integration[7]_i_7_n_0 ;
  wire \coarse_integration[7]_i_8_n_0 ;
  wire \coarse_integration[7]_i_9_n_0 ;
  wire \coarse_integration[8]_i_1_n_0 ;
  wire \coarse_integration[9]_i_1_n_0 ;
  wire \coarse_integration_reg[0]_0 ;
  wire \coarse_integration_reg[10]_0 ;
  wire \coarse_integration_reg[11]_0 ;
  wire \coarse_integration_reg[12]_0 ;
  wire \coarse_integration_reg[13]_0 ;
  wire \coarse_integration_reg[14]_0 ;
  wire \coarse_integration_reg[15]_0 ;
  wire \coarse_integration_reg[15]_1 ;
  wire \coarse_integration_reg[15]_i_4_n_0 ;
  wire \coarse_integration_reg[15]_i_4_n_1 ;
  wire \coarse_integration_reg[15]_i_4_n_10 ;
  wire \coarse_integration_reg[15]_i_4_n_11 ;
  wire \coarse_integration_reg[15]_i_4_n_12 ;
  wire \coarse_integration_reg[15]_i_4_n_13 ;
  wire \coarse_integration_reg[15]_i_4_n_14 ;
  wire \coarse_integration_reg[15]_i_4_n_15 ;
  wire \coarse_integration_reg[15]_i_4_n_2 ;
  wire \coarse_integration_reg[15]_i_4_n_3 ;
  wire \coarse_integration_reg[15]_i_4_n_4 ;
  wire \coarse_integration_reg[15]_i_4_n_5 ;
  wire \coarse_integration_reg[15]_i_4_n_6 ;
  wire \coarse_integration_reg[15]_i_4_n_7 ;
  wire \coarse_integration_reg[15]_i_4_n_8 ;
  wire \coarse_integration_reg[15]_i_4_n_9 ;
  wire \coarse_integration_reg[15]_i_5_n_1 ;
  wire \coarse_integration_reg[15]_i_5_n_2 ;
  wire \coarse_integration_reg[15]_i_5_n_3 ;
  wire \coarse_integration_reg[15]_i_5_n_4 ;
  wire \coarse_integration_reg[15]_i_5_n_5 ;
  wire \coarse_integration_reg[15]_i_5_n_6 ;
  wire \coarse_integration_reg[15]_i_5_n_7 ;
  wire \coarse_integration_reg[1]_0 ;
  wire \coarse_integration_reg[2]_0 ;
  wire \coarse_integration_reg[3]_0 ;
  wire \coarse_integration_reg[4]_0 ;
  wire \coarse_integration_reg[5]_0 ;
  wire \coarse_integration_reg[6]_0 ;
  wire \coarse_integration_reg[7]_0 ;
  wire \coarse_integration_reg[7]_i_2_n_0 ;
  wire \coarse_integration_reg[7]_i_2_n_1 ;
  wire \coarse_integration_reg[7]_i_2_n_10 ;
  wire \coarse_integration_reg[7]_i_2_n_11 ;
  wire \coarse_integration_reg[7]_i_2_n_12 ;
  wire \coarse_integration_reg[7]_i_2_n_13 ;
  wire \coarse_integration_reg[7]_i_2_n_14 ;
  wire \coarse_integration_reg[7]_i_2_n_15 ;
  wire \coarse_integration_reg[7]_i_2_n_2 ;
  wire \coarse_integration_reg[7]_i_2_n_3 ;
  wire \coarse_integration_reg[7]_i_2_n_4 ;
  wire \coarse_integration_reg[7]_i_2_n_5 ;
  wire \coarse_integration_reg[7]_i_2_n_6 ;
  wire \coarse_integration_reg[7]_i_2_n_7 ;
  wire \coarse_integration_reg[7]_i_2_n_8 ;
  wire \coarse_integration_reg[7]_i_2_n_9 ;
  wire \coarse_integration_reg[7]_i_3_n_0 ;
  wire \coarse_integration_reg[7]_i_3_n_1 ;
  wire \coarse_integration_reg[7]_i_3_n_2 ;
  wire \coarse_integration_reg[7]_i_3_n_3 ;
  wire \coarse_integration_reg[7]_i_3_n_4 ;
  wire \coarse_integration_reg[7]_i_3_n_5 ;
  wire \coarse_integration_reg[7]_i_3_n_6 ;
  wire \coarse_integration_reg[7]_i_3_n_7 ;
  wire \coarse_integration_reg[8]_0 ;
  wire \coarse_integration_reg[9]_0 ;
  wire frame_valid;
  wire update_valid_i_1_n_0;
  wire update_valid_reg_0;
  wire update_valid_reg_1;
  wire [7:0]NLW__carry_O_UNCONNECTED;
  wire [7:0]NLW__carry__0_O_UNCONNECTED;
  wire [7:5]NLW_analog_gain0_carry_CO_UNCONNECTED;
  wire [7:0]NLW_analog_gain0_carry_O_UNCONNECTED;
  wire [7:7]\NLW_coarse_integration_reg[15]_i_5_CO_UNCONNECTED ;

  CARRY8 _carry
       (.CI(1'b1),
        .CI_TOP(1'b0),
        .CO({_carry_n_0,_carry_n_1,_carry_n_2,_carry_n_3,_carry_n_4,_carry_n_5,_carry_n_6,_carry_n_7}),
        .DI({_carry_i_1_n_0,_carry_i_2_n_0,_carry_i_3_n_0,_carry_i_4_n_0,\coarse_integration_reg[6]_0 ,\coarse_integration_reg[5]_0 ,\coarse_integration_reg[4]_0 ,\coarse_integration_reg[3]_0 }),
        .O(NLW__carry_O_UNCONNECTED[7:0]),
        .S({_carry_i_5_n_0,_carry_i_6_n_0,_carry_i_7_n_0,_carry_i_8_n_0,_carry_i_9_n_0,_carry_i_10_n_0,_carry_i_11_n_0,_carry_i_12_n_0}));
  CARRY8 _carry__0
       (.CI(_carry_n_0),
        .CI_TOP(1'b0),
        .CO({_carry__0_n_0,_carry__0_n_1,_carry__0_n_2,_carry__0_n_3,_carry__0_n_4,_carry__0_n_5,_carry__0_n_6,_carry__0_n_7}),
        .DI({1'b0,1'b0,_carry__0_i_1_n_0,_carry__0_i_2_n_0,_carry__0_i_3_n_0,_carry__0_i_4_n_0,_carry__0_i_5_n_0,_carry__0_i_6_n_0}),
        .O(NLW__carry__0_O_UNCONNECTED[7:0]),
        .S({_carry__0_i_7_n_0,_carry__0_i_8_n_0,_carry__0_i_9_n_0,_carry__0_i_10_n_0,_carry__0_i_11_n_0,_carry__0_i_12_n_0,_carry__0_i_13_n_0,_carry__0_i_14_n_0}));
  LUT4 #(
    .INIT(16'h8000)) 
    _carry__0_i_1
       (.I0(\coarse_integration_reg[15]_0 ),
        .I1(\coarse_integration_reg[13]_0 ),
        .I2(_carry__0_i_15_n_0),
        .I3(\coarse_integration_reg[14]_0 ),
        .O(_carry__0_i_1_n_0));
  LUT5 #(
    .INIT(32'h6AAA9555)) 
    _carry__0_i_10
       (.I0(\coarse_integration_reg[15]_0 ),
        .I1(\coarse_integration_reg[14]_0 ),
        .I2(_carry__0_i_15_n_0),
        .I3(\coarse_integration_reg[13]_0 ),
        .I4(\coarse_integration_reg[12]_0 ),
        .O(_carry__0_i_10_n_0));
  LUT4 #(
    .INIT(16'h6A95)) 
    _carry__0_i_11
       (.I0(\coarse_integration_reg[14]_0 ),
        .I1(\coarse_integration_reg[13]_0 ),
        .I2(_carry__0_i_15_n_0),
        .I3(\coarse_integration_reg[11]_0 ),
        .O(_carry__0_i_11_n_0));
  LUT3 #(
    .INIT(8'h69)) 
    _carry__0_i_12
       (.I0(\coarse_integration_reg[13]_0 ),
        .I1(_carry__0_i_15_n_0),
        .I2(\coarse_integration_reg[10]_0 ),
        .O(_carry__0_i_12_n_0));
  LUT6 #(
    .INIT(64'h6AAAAAAA55555555)) 
    _carry__0_i_13
       (.I0(\coarse_integration_reg[12]_0 ),
        .I1(\coarse_integration_reg[11]_0 ),
        .I2(\coarse_integration_reg[7]_0 ),
        .I3(\coarse_integration_reg[8]_0 ),
        .I4(\coarse_integration_reg[10]_0 ),
        .I5(\coarse_integration_reg[9]_0 ),
        .O(_carry__0_i_13_n_0));
  LUT5 #(
    .INIT(32'h6AAA5555)) 
    _carry__0_i_14
       (.I0(\coarse_integration_reg[11]_0 ),
        .I1(\coarse_integration_reg[10]_0 ),
        .I2(\coarse_integration_reg[7]_0 ),
        .I3(\coarse_integration_reg[9]_0 ),
        .I4(\coarse_integration_reg[8]_0 ),
        .O(_carry__0_i_14_n_0));
  LUT6 #(
    .INIT(64'h8000000000000000)) 
    _carry__0_i_15
       (.I0(\coarse_integration_reg[12]_0 ),
        .I1(\coarse_integration_reg[10]_0 ),
        .I2(\coarse_integration_reg[8]_0 ),
        .I3(\coarse_integration_reg[7]_0 ),
        .I4(\coarse_integration_reg[9]_0 ),
        .I5(\coarse_integration_reg[11]_0 ),
        .O(_carry__0_i_15_n_0));
  LUT4 #(
    .INIT(16'h7F80)) 
    _carry__0_i_2
       (.I0(\coarse_integration_reg[13]_0 ),
        .I1(_carry__0_i_15_n_0),
        .I2(\coarse_integration_reg[14]_0 ),
        .I3(\coarse_integration_reg[15]_0 ),
        .O(_carry__0_i_2_n_0));
  LUT3 #(
    .INIT(8'h78)) 
    _carry__0_i_3
       (.I0(_carry__0_i_15_n_0),
        .I1(\coarse_integration_reg[13]_0 ),
        .I2(\coarse_integration_reg[14]_0 ),
        .O(_carry__0_i_3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    _carry__0_i_4
       (.I0(_carry__0_i_15_n_0),
        .I1(\coarse_integration_reg[13]_0 ),
        .O(_carry__0_i_4_n_0));
  LUT6 #(
    .INIT(64'h7FFFFFFF80000000)) 
    _carry__0_i_5
       (.I0(\coarse_integration_reg[10]_0 ),
        .I1(\coarse_integration_reg[8]_0 ),
        .I2(\coarse_integration_reg[7]_0 ),
        .I3(\coarse_integration_reg[9]_0 ),
        .I4(\coarse_integration_reg[11]_0 ),
        .I5(\coarse_integration_reg[12]_0 ),
        .O(_carry__0_i_5_n_0));
  LUT5 #(
    .INIT(32'h7FFF8000)) 
    _carry__0_i_6
       (.I0(\coarse_integration_reg[9]_0 ),
        .I1(\coarse_integration_reg[7]_0 ),
        .I2(\coarse_integration_reg[8]_0 ),
        .I3(\coarse_integration_reg[10]_0 ),
        .I4(\coarse_integration_reg[11]_0 ),
        .O(_carry__0_i_6_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    _carry__0_i_7
       (.I0(\coarse_integration_reg[15]_0 ),
        .O(_carry__0_i_7_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    _carry__0_i_8
       (.I0(\coarse_integration_reg[14]_0 ),
        .O(_carry__0_i_8_n_0));
  LUT4 #(
    .INIT(16'h80FF)) 
    _carry__0_i_9
       (.I0(\coarse_integration_reg[14]_0 ),
        .I1(_carry__0_i_15_n_0),
        .I2(\coarse_integration_reg[15]_0 ),
        .I3(\coarse_integration_reg[13]_0 ),
        .O(_carry__0_i_9_n_0));
  LUT4 #(
    .INIT(16'h7F80)) 
    _carry_i_1
       (.I0(\coarse_integration_reg[8]_0 ),
        .I1(\coarse_integration_reg[7]_0 ),
        .I2(\coarse_integration_reg[9]_0 ),
        .I3(\coarse_integration_reg[10]_0 ),
        .O(_carry_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    _carry_i_10
       (.I0(\coarse_integration_reg[5]_0 ),
        .I1(\coarse_integration_reg[2]_0 ),
        .O(_carry_i_10_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    _carry_i_11
       (.I0(\coarse_integration_reg[4]_0 ),
        .I1(\coarse_integration_reg[1]_0 ),
        .O(_carry_i_11_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    _carry_i_12
       (.I0(\coarse_integration_reg[3]_0 ),
        .I1(\coarse_integration_reg[0]_0 ),
        .O(_carry_i_12_n_0));
  LUT3 #(
    .INIT(8'h78)) 
    _carry_i_2
       (.I0(\coarse_integration_reg[7]_0 ),
        .I1(\coarse_integration_reg[8]_0 ),
        .I2(\coarse_integration_reg[9]_0 ),
        .O(_carry_i_2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    _carry_i_3
       (.I0(\coarse_integration_reg[7]_0 ),
        .I1(\coarse_integration_reg[8]_0 ),
        .O(_carry_i_3_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    _carry_i_4
       (.I0(\coarse_integration_reg[7]_0 ),
        .O(_carry_i_4_n_0));
  LUT4 #(
    .INIT(16'h6A55)) 
    _carry_i_5
       (.I0(\coarse_integration_reg[10]_0 ),
        .I1(\coarse_integration_reg[9]_0 ),
        .I2(\coarse_integration_reg[8]_0 ),
        .I3(\coarse_integration_reg[7]_0 ),
        .O(_carry_i_5_n_0));
  LUT4 #(
    .INIT(16'h6A95)) 
    _carry_i_6
       (.I0(\coarse_integration_reg[9]_0 ),
        .I1(\coarse_integration_reg[8]_0 ),
        .I2(\coarse_integration_reg[7]_0 ),
        .I3(\coarse_integration_reg[6]_0 ),
        .O(_carry_i_6_n_0));
  LUT3 #(
    .INIT(8'h69)) 
    _carry_i_7
       (.I0(\coarse_integration_reg[8]_0 ),
        .I1(\coarse_integration_reg[7]_0 ),
        .I2(\coarse_integration_reg[5]_0 ),
        .O(_carry_i_7_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    _carry_i_8
       (.I0(\coarse_integration_reg[7]_0 ),
        .I1(\coarse_integration_reg[4]_0 ),
        .O(_carry_i_8_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    _carry_i_9
       (.I0(\coarse_integration_reg[6]_0 ),
        .I1(\coarse_integration_reg[3]_0 ),
        .O(_carry_i_9_n_0));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 analog_gain0_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({NLW_analog_gain0_carry_CO_UNCONNECTED[7:5],analog_gain0_carry_n_3,analog_gain0_carry_n_4,analog_gain0_carry_n_5,analog_gain0_carry_n_6,analog_gain0_carry_n_7}),
        .DI({1'b0,1'b0,1'b0,Q[2],\analog_gain_reg[7]_0 ,Q[1:0],1'b0}),
        .O({NLW_analog_gain0_carry_O_UNCONNECTED[7:6],analog_gain0_carry_n_10,analog_gain0_carry_n_11,analog_gain0_carry_n_12,analog_gain0_carry_n_13,analog_gain0_carry_n_14,NLW_analog_gain0_carry_O_UNCONNECTED[0]}),
        .S({1'b0,1'b0,analog_gain0_carry_i_2_n_0,analog_gain0_carry_i_3_n_0,S,analog_gain0_carry_i_6_n_0,1'b0}));
  LUT2 #(
    .INIT(4'h9)) 
    analog_gain0_carry_i_2
       (.I0(Q[3]),
        .I1(Q[4]),
        .O(analog_gain0_carry_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    analog_gain0_carry_i_3
       (.I0(Q[2]),
        .I1(Q[3]),
        .O(analog_gain0_carry_i_3_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    analog_gain0_carry_i_6
       (.I0(Q[0]),
        .O(analog_gain0_carry_i_6_n_0));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT5 #(
    .INIT(32'hAAAAAAA8)) 
    \analog_gain[7]_i_3 
       (.I0(_carry__0_n_0),
        .I1(Q[3]),
        .I2(Q[2]),
        .I3(Q[4]),
        .I4(Q[1]),
        .O(\analog_gain_reg[6]_0 ));
  LUT6 #(
    .INIT(64'h000000005555FF7F)) 
    \analog_gain[7]_i_5 
       (.I0(\analog_gain[7]_i_7_n_0 ),
        .I1(\coarse_integration_reg[7]_i_2_n_9 ),
        .I2(\coarse_integration_reg[7]_i_2_n_8 ),
        .I3(\analog_gain[7]_i_8_n_0 ),
        .I4(\coarse_integration_reg[15]_i_4_n_15 ),
        .I5(\analog_gain[7]_i_9_n_0 ),
        .O(coarse_integration23_in));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT3 #(
    .INIT(8'h7F)) 
    \analog_gain[7]_i_6 
       (.I0(Q[2]),
        .I1(Q[4]),
        .I2(Q[3]),
        .O(\analog_gain_reg[5]_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \analog_gain[7]_i_7 
       (.I0(\coarse_integration_reg[15]_i_4_n_14 ),
        .I1(\coarse_integration_reg[15]_i_4_n_13 ),
        .O(\analog_gain[7]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'h000000007FFFFFFF)) 
    \analog_gain[7]_i_8 
       (.I0(\coarse_integration_reg[7]_i_2_n_15 ),
        .I1(\coarse_integration_reg[7]_i_2_n_13 ),
        .I2(\coarse_integration_reg[7]_i_2_n_14 ),
        .I3(\coarse_integration_reg[7]_i_2_n_11 ),
        .I4(\coarse_integration_reg[7]_i_2_n_12 ),
        .I5(\coarse_integration_reg[7]_i_2_n_10 ),
        .O(\analog_gain[7]_i_8_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFFFFFE)) 
    \analog_gain[7]_i_9 
       (.I0(\coarse_integration_reg[15]_i_4_n_11 ),
        .I1(\coarse_integration_reg[15]_i_4_n_12 ),
        .I2(\coarse_integration_reg[15]_i_4_n_8 ),
        .I3(\coarse_integration_reg[15]_i_4_n_0 ),
        .I4(\coarse_integration_reg[15]_i_4_n_10 ),
        .I5(\coarse_integration_reg[15]_i_4_n_9 ),
        .O(\analog_gain[7]_i_9_n_0 ));
  FDRE \analog_gain_reg[3] 
       (.C(aclk),
        .CE(E),
        .D(analog_gain0_carry_n_14),
        .Q(Q[0]),
        .R(clear));
  FDRE \analog_gain_reg[4] 
       (.C(aclk),
        .CE(E),
        .D(analog_gain0_carry_n_13),
        .Q(Q[1]),
        .R(clear));
  FDRE \analog_gain_reg[5] 
       (.C(aclk),
        .CE(E),
        .D(analog_gain0_carry_n_12),
        .Q(Q[2]),
        .R(clear));
  FDRE \analog_gain_reg[6] 
       (.C(aclk),
        .CE(E),
        .D(analog_gain0_carry_n_11),
        .Q(Q[3]),
        .R(clear));
  FDRE \analog_gain_reg[7] 
       (.C(aclk),
        .CE(E),
        .D(analog_gain0_carry_n_10),
        .Q(Q[4]),
        .R(clear));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[0]_i_1 
       (.I0(\coarse_integration_reg[7]_i_2_n_15 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[0]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[0]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[10]_i_1 
       (.I0(\coarse_integration_reg[15]_i_4_n_13 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[10]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[10]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h80808F80)) 
    \coarse_integration[11]_i_1 
       (.I0(coarse_integration23_in),
        .I1(\coarse_integration_reg[15]_i_4_n_12 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[11]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[11]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h80808F80)) 
    \coarse_integration[12]_i_1 
       (.I0(coarse_integration23_in),
        .I1(\coarse_integration_reg[15]_i_4_n_11 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[12]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[12]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h80808F80)) 
    \coarse_integration[13]_i_1 
       (.I0(coarse_integration23_in),
        .I1(\coarse_integration_reg[15]_i_4_n_10 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[13]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[13]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h80808F80)) 
    \coarse_integration[14]_i_1 
       (.I0(coarse_integration23_in),
        .I1(\coarse_integration_reg[15]_i_4_n_9 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[14]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[14]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hBFB00000)) 
    \coarse_integration[15]_i_1 
       (.I0(coarse_integration23_in),
        .I1(\analog_gain_reg[5]_0 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(\coarse_integration[15]_i_3_n_0 ),
        .I4(\coarse_integration_reg[15]_1 ),
        .O(\coarse_integration[15]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[15]_i_10 
       (.I0(\coarse_integration_reg[8]_0 ),
        .I1(\coarse_integration_reg[11]_0 ),
        .O(\coarse_integration[15]_i_10_n_0 ));
  LUT1 #(
    .INIT(2'h1)) 
    \coarse_integration[15]_i_11 
       (.I0(\coarse_integration_reg[15]_0 ),
        .O(\coarse_integration[15]_i_11_n_0 ));
  LUT1 #(
    .INIT(2'h1)) 
    \coarse_integration[15]_i_12 
       (.I0(\coarse_integration_reg[14]_0 ),
        .O(\coarse_integration[15]_i_12_n_0 ));
  LUT1 #(
    .INIT(2'h1)) 
    \coarse_integration[15]_i_13 
       (.I0(\coarse_integration_reg[13]_0 ),
        .O(\coarse_integration[15]_i_13_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[15]_i_14 
       (.I0(\coarse_integration_reg[15]_0 ),
        .I1(\coarse_integration_reg[12]_0 ),
        .O(\coarse_integration[15]_i_14_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[15]_i_15 
       (.I0(\coarse_integration_reg[14]_0 ),
        .I1(\coarse_integration_reg[11]_0 ),
        .O(\coarse_integration[15]_i_15_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[15]_i_16 
       (.I0(\coarse_integration_reg[13]_0 ),
        .I1(\coarse_integration_reg[10]_0 ),
        .O(\coarse_integration[15]_i_16_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[15]_i_17 
       (.I0(\coarse_integration_reg[12]_0 ),
        .I1(\coarse_integration_reg[9]_0 ),
        .O(\coarse_integration[15]_i_17_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[15]_i_18 
       (.I0(\coarse_integration_reg[11]_0 ),
        .I1(\coarse_integration_reg[8]_0 ),
        .O(\coarse_integration[15]_i_18_n_0 ));
  LUT5 #(
    .INIT(32'h80808F80)) 
    \coarse_integration[15]_i_2 
       (.I0(coarse_integration23_in),
        .I1(\coarse_integration_reg[15]_i_4_n_8 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[15]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[15]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h222222222222222A)) 
    \coarse_integration[15]_i_3 
       (.I0(update_valid_reg_1),
        .I1(_carry__0_n_0),
        .I2(Q[3]),
        .I3(Q[2]),
        .I4(Q[4]),
        .I5(Q[1]),
        .O(\coarse_integration[15]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[15]_i_6 
       (.I0(\coarse_integration_reg[12]_0 ),
        .I1(\coarse_integration_reg[15]_0 ),
        .O(\coarse_integration[15]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[15]_i_7 
       (.I0(\coarse_integration_reg[11]_0 ),
        .I1(\coarse_integration_reg[14]_0 ),
        .O(\coarse_integration[15]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[15]_i_8 
       (.I0(\coarse_integration_reg[10]_0 ),
        .I1(\coarse_integration_reg[13]_0 ),
        .O(\coarse_integration[15]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[15]_i_9 
       (.I0(\coarse_integration_reg[9]_0 ),
        .I1(\coarse_integration_reg[12]_0 ),
        .O(\coarse_integration[15]_i_9_n_0 ));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[1]_i_1 
       (.I0(\coarse_integration_reg[7]_i_2_n_14 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[1]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[1]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[2]_i_1 
       (.I0(\coarse_integration_reg[7]_i_2_n_13 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[2]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[2]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[3]_i_1 
       (.I0(\coarse_integration_reg[7]_i_2_n_12 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[3]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[3]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hBFBFBFB0)) 
    \coarse_integration[4]_i_1 
       (.I0(\coarse_integration_reg[7]_i_2_n_11 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[4]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[4]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h80808F80)) 
    \coarse_integration[5]_i_1 
       (.I0(coarse_integration23_in),
        .I1(\coarse_integration_reg[7]_i_2_n_10 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[5]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[5]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[6]_i_1 
       (.I0(\coarse_integration_reg[7]_i_2_n_9 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[6]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[6]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[7]_i_1 
       (.I0(\coarse_integration_reg[7]_i_2_n_8 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[7]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[7]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_10 
       (.I0(\coarse_integration_reg[1]_0 ),
        .I1(\coarse_integration_reg[4]_0 ),
        .O(\coarse_integration[7]_i_10_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_11 
       (.I0(\coarse_integration_reg[0]_0 ),
        .I1(\coarse_integration_reg[3]_0 ),
        .O(\coarse_integration[7]_i_11_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_12 
       (.I0(\coarse_integration_reg[10]_0 ),
        .I1(\coarse_integration_reg[7]_0 ),
        .O(\coarse_integration[7]_i_12_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_13 
       (.I0(\coarse_integration_reg[9]_0 ),
        .I1(\coarse_integration_reg[6]_0 ),
        .O(\coarse_integration[7]_i_13_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_14 
       (.I0(\coarse_integration_reg[8]_0 ),
        .I1(\coarse_integration_reg[5]_0 ),
        .O(\coarse_integration[7]_i_14_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_15 
       (.I0(\coarse_integration_reg[7]_0 ),
        .I1(\coarse_integration_reg[4]_0 ),
        .O(\coarse_integration[7]_i_15_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_16 
       (.I0(\coarse_integration_reg[6]_0 ),
        .I1(\coarse_integration_reg[3]_0 ),
        .O(\coarse_integration[7]_i_16_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_17 
       (.I0(\coarse_integration_reg[5]_0 ),
        .I1(\coarse_integration_reg[2]_0 ),
        .O(\coarse_integration[7]_i_17_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_18 
       (.I0(\coarse_integration_reg[4]_0 ),
        .I1(\coarse_integration_reg[1]_0 ),
        .O(\coarse_integration[7]_i_18_n_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    \coarse_integration[7]_i_19 
       (.I0(\coarse_integration_reg[3]_0 ),
        .I1(\coarse_integration_reg[0]_0 ),
        .O(\coarse_integration[7]_i_19_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_4 
       (.I0(\coarse_integration_reg[7]_0 ),
        .I1(\coarse_integration_reg[10]_0 ),
        .O(\coarse_integration[7]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_5 
       (.I0(\coarse_integration_reg[6]_0 ),
        .I1(\coarse_integration_reg[9]_0 ),
        .O(\coarse_integration[7]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_6 
       (.I0(\coarse_integration_reg[5]_0 ),
        .I1(\coarse_integration_reg[8]_0 ),
        .O(\coarse_integration[7]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_7 
       (.I0(\coarse_integration_reg[4]_0 ),
        .I1(\coarse_integration_reg[7]_0 ),
        .O(\coarse_integration[7]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_8 
       (.I0(\coarse_integration_reg[3]_0 ),
        .I1(\coarse_integration_reg[6]_0 ),
        .O(\coarse_integration[7]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \coarse_integration[7]_i_9 
       (.I0(\coarse_integration_reg[2]_0 ),
        .I1(\coarse_integration_reg[5]_0 ),
        .O(\coarse_integration[7]_i_9_n_0 ));
  LUT5 #(
    .INIT(32'h80808F80)) 
    \coarse_integration[8]_i_1 
       (.I0(coarse_integration23_in),
        .I1(\coarse_integration_reg[15]_i_4_n_15 ),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[8]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[8]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hB0B0BFB0)) 
    \coarse_integration[9]_i_1 
       (.I0(\coarse_integration_reg[15]_i_4_n_14 ),
        .I1(coarse_integration23_in),
        .I2(\analog_gain_reg[7]_0 ),
        .I3(coarse_integration0[9]),
        .I4(_carry__0_n_0),
        .O(\coarse_integration[9]_i_1_n_0 ));
  FDRE \coarse_integration_reg[0] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[0]_i_1_n_0 ),
        .Q(\coarse_integration_reg[0]_0 ),
        .R(clear));
  FDRE \coarse_integration_reg[10] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[10]_i_1_n_0 ),
        .Q(\coarse_integration_reg[10]_0 ),
        .R(clear));
  FDRE \coarse_integration_reg[11] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[11]_i_1_n_0 ),
        .Q(\coarse_integration_reg[11]_0 ),
        .R(clear));
  FDRE \coarse_integration_reg[12] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[12]_i_1_n_0 ),
        .Q(\coarse_integration_reg[12]_0 ),
        .R(clear));
  FDRE \coarse_integration_reg[13] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[13]_i_1_n_0 ),
        .Q(\coarse_integration_reg[13]_0 ),
        .R(clear));
  FDRE \coarse_integration_reg[14] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[14]_i_1_n_0 ),
        .Q(\coarse_integration_reg[14]_0 ),
        .R(clear));
  FDRE \coarse_integration_reg[15] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[15]_i_2_n_0 ),
        .Q(\coarse_integration_reg[15]_0 ),
        .R(clear));
  CARRY8 \coarse_integration_reg[15]_i_4 
       (.CI(\coarse_integration_reg[7]_i_2_n_0 ),
        .CI_TOP(1'b0),
        .CO({\coarse_integration_reg[15]_i_4_n_0 ,\coarse_integration_reg[15]_i_4_n_1 ,\coarse_integration_reg[15]_i_4_n_2 ,\coarse_integration_reg[15]_i_4_n_3 ,\coarse_integration_reg[15]_i_4_n_4 ,\coarse_integration_reg[15]_i_4_n_5 ,\coarse_integration_reg[15]_i_4_n_6 ,\coarse_integration_reg[15]_i_4_n_7 }),
        .DI({1'b0,1'b0,1'b0,\coarse_integration_reg[12]_0 ,\coarse_integration_reg[11]_0 ,\coarse_integration_reg[10]_0 ,\coarse_integration_reg[9]_0 ,\coarse_integration_reg[8]_0 }),
        .O({\coarse_integration_reg[15]_i_4_n_8 ,\coarse_integration_reg[15]_i_4_n_9 ,\coarse_integration_reg[15]_i_4_n_10 ,\coarse_integration_reg[15]_i_4_n_11 ,\coarse_integration_reg[15]_i_4_n_12 ,\coarse_integration_reg[15]_i_4_n_13 ,\coarse_integration_reg[15]_i_4_n_14 ,\coarse_integration_reg[15]_i_4_n_15 }),
        .S({\coarse_integration_reg[15]_0 ,\coarse_integration_reg[14]_0 ,\coarse_integration_reg[13]_0 ,\coarse_integration[15]_i_6_n_0 ,\coarse_integration[15]_i_7_n_0 ,\coarse_integration[15]_i_8_n_0 ,\coarse_integration[15]_i_9_n_0 ,\coarse_integration[15]_i_10_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 \coarse_integration_reg[15]_i_5 
       (.CI(\coarse_integration_reg[7]_i_3_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_coarse_integration_reg[15]_i_5_CO_UNCONNECTED [7],\coarse_integration_reg[15]_i_5_n_1 ,\coarse_integration_reg[15]_i_5_n_2 ,\coarse_integration_reg[15]_i_5_n_3 ,\coarse_integration_reg[15]_i_5_n_4 ,\coarse_integration_reg[15]_i_5_n_5 ,\coarse_integration_reg[15]_i_5_n_6 ,\coarse_integration_reg[15]_i_5_n_7 }),
        .DI({1'b0,\coarse_integration_reg[14]_0 ,\coarse_integration_reg[13]_0 ,\coarse_integration_reg[12]_0 ,\coarse_integration_reg[11]_0 ,\coarse_integration_reg[10]_0 ,\coarse_integration_reg[9]_0 ,\coarse_integration_reg[8]_0 }),
        .O(coarse_integration0[15:8]),
        .S({\coarse_integration[15]_i_11_n_0 ,\coarse_integration[15]_i_12_n_0 ,\coarse_integration[15]_i_13_n_0 ,\coarse_integration[15]_i_14_n_0 ,\coarse_integration[15]_i_15_n_0 ,\coarse_integration[15]_i_16_n_0 ,\coarse_integration[15]_i_17_n_0 ,\coarse_integration[15]_i_18_n_0 }));
  FDRE \coarse_integration_reg[1] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[1]_i_1_n_0 ),
        .Q(\coarse_integration_reg[1]_0 ),
        .R(clear));
  FDRE \coarse_integration_reg[2] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[2]_i_1_n_0 ),
        .Q(\coarse_integration_reg[2]_0 ),
        .R(clear));
  FDSE \coarse_integration_reg[3] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[3]_i_1_n_0 ),
        .Q(\coarse_integration_reg[3]_0 ),
        .S(clear));
  FDSE \coarse_integration_reg[4] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[4]_i_1_n_0 ),
        .Q(\coarse_integration_reg[4]_0 ),
        .S(clear));
  FDRE \coarse_integration_reg[5] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[5]_i_1_n_0 ),
        .Q(\coarse_integration_reg[5]_0 ),
        .R(clear));
  FDSE \coarse_integration_reg[6] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[6]_i_1_n_0 ),
        .Q(\coarse_integration_reg[6]_0 ),
        .S(clear));
  FDRE \coarse_integration_reg[7] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[7]_i_1_n_0 ),
        .Q(\coarse_integration_reg[7]_0 ),
        .R(clear));
  CARRY8 \coarse_integration_reg[7]_i_2 
       (.CI(1'b1),
        .CI_TOP(1'b0),
        .CO({\coarse_integration_reg[7]_i_2_n_0 ,\coarse_integration_reg[7]_i_2_n_1 ,\coarse_integration_reg[7]_i_2_n_2 ,\coarse_integration_reg[7]_i_2_n_3 ,\coarse_integration_reg[7]_i_2_n_4 ,\coarse_integration_reg[7]_i_2_n_5 ,\coarse_integration_reg[7]_i_2_n_6 ,\coarse_integration_reg[7]_i_2_n_7 }),
        .DI({\coarse_integration_reg[7]_0 ,\coarse_integration_reg[6]_0 ,\coarse_integration_reg[5]_0 ,\coarse_integration_reg[4]_0 ,\coarse_integration_reg[3]_0 ,\coarse_integration_reg[2]_0 ,\coarse_integration_reg[1]_0 ,\coarse_integration_reg[0]_0 }),
        .O({\coarse_integration_reg[7]_i_2_n_8 ,\coarse_integration_reg[7]_i_2_n_9 ,\coarse_integration_reg[7]_i_2_n_10 ,\coarse_integration_reg[7]_i_2_n_11 ,\coarse_integration_reg[7]_i_2_n_12 ,\coarse_integration_reg[7]_i_2_n_13 ,\coarse_integration_reg[7]_i_2_n_14 ,\coarse_integration_reg[7]_i_2_n_15 }),
        .S({\coarse_integration[7]_i_4_n_0 ,\coarse_integration[7]_i_5_n_0 ,\coarse_integration[7]_i_6_n_0 ,\coarse_integration[7]_i_7_n_0 ,\coarse_integration[7]_i_8_n_0 ,\coarse_integration[7]_i_9_n_0 ,\coarse_integration[7]_i_10_n_0 ,\coarse_integration[7]_i_11_n_0 }));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 \coarse_integration_reg[7]_i_3 
       (.CI(1'b1),
        .CI_TOP(1'b0),
        .CO({\coarse_integration_reg[7]_i_3_n_0 ,\coarse_integration_reg[7]_i_3_n_1 ,\coarse_integration_reg[7]_i_3_n_2 ,\coarse_integration_reg[7]_i_3_n_3 ,\coarse_integration_reg[7]_i_3_n_4 ,\coarse_integration_reg[7]_i_3_n_5 ,\coarse_integration_reg[7]_i_3_n_6 ,\coarse_integration_reg[7]_i_3_n_7 }),
        .DI({\coarse_integration_reg[7]_0 ,\coarse_integration_reg[6]_0 ,\coarse_integration_reg[5]_0 ,\coarse_integration_reg[4]_0 ,\coarse_integration_reg[3]_0 ,\coarse_integration_reg[2]_0 ,\coarse_integration_reg[1]_0 ,\coarse_integration_reg[0]_0 }),
        .O(coarse_integration0[7:0]),
        .S({\coarse_integration[7]_i_12_n_0 ,\coarse_integration[7]_i_13_n_0 ,\coarse_integration[7]_i_14_n_0 ,\coarse_integration[7]_i_15_n_0 ,\coarse_integration[7]_i_16_n_0 ,\coarse_integration[7]_i_17_n_0 ,\coarse_integration[7]_i_18_n_0 ,\coarse_integration[7]_i_19_n_0 }));
  FDRE \coarse_integration_reg[8] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[8]_i_1_n_0 ),
        .Q(\coarse_integration_reg[8]_0 ),
        .R(clear));
  FDSE \coarse_integration_reg[9] 
       (.C(aclk),
        .CE(\coarse_integration[15]_i_1_n_0 ),
        .D(\coarse_integration[9]_i_1_n_0 ),
        .Q(\coarse_integration_reg[9]_0 ),
        .S(clear));
  LUT4 #(
    .INIT(16'h00E0)) 
    update_valid_i_1
       (.I0(\analog_gain_reg[7]_0 ),
        .I1(update_valid_reg_1),
        .I2(frame_valid),
        .I3(update_valid_reg_0),
        .O(update_valid_i_1_n_0));
  FDRE update_valid_reg
       (.C(aclk),
        .CE(1'b1),
        .D(update_valid_i_1_n_0),
        .Q(update_valid_reg_0),
        .R(clear));
endmodule

(* FRAME_PIXELS = "2073600" *) 
(* NotValidForBitStream *)
module axis_ae_status
   (aclk,
    aresetn,
    s_axis_tdata,
    s_axis_tvalid,
    s_axis_tready,
    s_axis_tuser,
    status);
  input aclk;
  input aresetn;
  input [23:0]s_axis_tdata;
  input s_axis_tvalid;
  input s_axis_tready;
  input s_axis_tuser;
  output [31:0]status;

  wire \<const0> ;
  wire aclk;
  wire aresetn;
  wire clear;
  wire coarse_integration23_in;
  wire controller_n_19;
  wire controller_n_23;
  wire controller_n_24;
  wire frame_valid;
  wire meter_n_14;
  wire meter_n_15;
  wire meter_n_2;
  wire meter_n_3;
  wire meter_n_4;
  wire meter_n_5;
  wire n_0_327;
  wire [23:0]s_axis_tdata;
  wire s_axis_tready;
  wire s_axis_tuser;
  wire s_axis_tvalid;
  wire [31:0]\^status ;

  assign status[31:19] = \^status [31:19];
  assign status[18] = \<const0> ;
  assign status[17] = \<const0> ;
  assign status[16] = \<const0> ;
  assign status[15:0] = \^status [15:0];
  GND GND
       (.G(\<const0> ));
  ae_controller controller
       (.E(meter_n_2),
        .Q(\^status [23:19]),
        .S({meter_n_14,meter_n_15}),
        .aclk(aclk),
        .\analog_gain_reg[5]_0 (controller_n_19),
        .\analog_gain_reg[6]_0 (controller_n_23),
        .\analog_gain_reg[7]_0 (meter_n_5),
        .clear(clear),
        .coarse_integration23_in(coarse_integration23_in),
        .\coarse_integration_reg[0]_0 (\^status [0]),
        .\coarse_integration_reg[10]_0 (\^status [10]),
        .\coarse_integration_reg[11]_0 (\^status [11]),
        .\coarse_integration_reg[12]_0 (\^status [12]),
        .\coarse_integration_reg[13]_0 (\^status [13]),
        .\coarse_integration_reg[14]_0 (\^status [14]),
        .\coarse_integration_reg[15]_0 (\^status [15]),
        .\coarse_integration_reg[15]_1 (meter_n_3),
        .\coarse_integration_reg[1]_0 (\^status [1]),
        .\coarse_integration_reg[2]_0 (\^status [2]),
        .\coarse_integration_reg[3]_0 (\^status [3]),
        .\coarse_integration_reg[4]_0 (\^status [4]),
        .\coarse_integration_reg[5]_0 (\^status [5]),
        .\coarse_integration_reg[6]_0 (\^status [6]),
        .\coarse_integration_reg[7]_0 (\^status [7]),
        .\coarse_integration_reg[8]_0 (\^status [8]),
        .\coarse_integration_reg[9]_0 (\^status [9]),
        .frame_valid(frame_valid),
        .update_valid_reg_0(controller_n_24),
        .update_valid_reg_1(meter_n_4));
  LUT1 #(
    .INIT(2'h1)) 
    i_327
       (.I0(aresetn),
        .O(n_0_327));
  axis_luma_meter meter
       (.E(meter_n_2),
        .S({meter_n_14,meter_n_15}),
        .SR(clear),
        .aclk(aclk),
        .\analog_gain_reg[7] (controller_n_23),
        .\analog_gain_reg[7]_0 (controller_n_19),
        .\analog_gain_reg[7]_1 (controller_n_24),
        .\analog_gain_reg[7]_2 (\^status [21:20]),
        .aresetn(aresetn),
        .coarse_integration23_in(coarse_integration23_in),
        .\frame_mean_reg[5]_0 (meter_n_5),
        .\frame_mean_reg[7]_0 (meter_n_4),
        .frame_valid(frame_valid),
        .frame_valid_reg_0(meter_n_3),
        .s_axis_tdata(s_axis_tdata),
        .s_axis_tready(s_axis_tready),
        .s_axis_tuser(s_axis_tuser),
        .s_axis_tvalid(s_axis_tvalid),
        .status(\^status [31:24]));
endmodule

module axis_luma_meter
   (SR,
    frame_valid,
    E,
    frame_valid_reg_0,
    \frame_mean_reg[7]_0 ,
    \frame_mean_reg[5]_0 ,
    status,
    S,
    s_axis_tuser,
    aclk,
    \analog_gain_reg[7] ,
    coarse_integration23_in,
    \analog_gain_reg[7]_0 ,
    \analog_gain_reg[7]_1 ,
    aresetn,
    s_axis_tvalid,
    s_axis_tready,
    \analog_gain_reg[7]_2 ,
    s_axis_tdata);
  output [0:0]SR;
  output frame_valid;
  output [0:0]E;
  output frame_valid_reg_0;
  output \frame_mean_reg[7]_0 ;
  output \frame_mean_reg[5]_0 ;
  output [7:0]status;
  output [1:0]S;
  input s_axis_tuser;
  input aclk;
  input \analog_gain_reg[7] ;
  input coarse_integration23_in;
  input \analog_gain_reg[7]_0 ;
  input \analog_gain_reg[7]_1 ;
  input aresetn;
  input s_axis_tvalid;
  input s_axis_tready;
  input [1:0]\analog_gain_reg[7]_2 ;
  input [23:0]s_axis_tdata;

  wire [14:1]C;
  wire [0:0]E;
  wire [1:0]S;
  wire [0:0]SR;
  wire aclk;
  wire analog_gain0_carry_i_7_n_0;
  wire \analog_gain_reg[7] ;
  wire \analog_gain_reg[7]_0 ;
  wire \analog_gain_reg[7]_1 ;
  wire [1:0]\analog_gain_reg[7]_2 ;
  wire aresetn;
  wire coarse_integration23_in;
  wire [1:1]count;
  wire [20:1]count0;
  wire count0_carry__0_n_0;
  wire count0_carry__0_n_1;
  wire count0_carry__0_n_2;
  wire count0_carry__0_n_3;
  wire count0_carry__0_n_4;
  wire count0_carry__0_n_5;
  wire count0_carry__0_n_6;
  wire count0_carry__0_n_7;
  wire count0_carry__1_n_5;
  wire count0_carry__1_n_6;
  wire count0_carry__1_n_7;
  wire count0_carry_n_0;
  wire count0_carry_n_1;
  wire count0_carry_n_2;
  wire count0_carry_n_3;
  wire count0_carry_n_4;
  wire count0_carry_n_5;
  wire count0_carry_n_6;
  wire count0_carry_n_7;
  wire \count[0]_i_1_n_0 ;
  wire \count[20]_i_3_n_0 ;
  wire \count[20]_i_4_n_0 ;
  wire \count[20]_i_5_n_0 ;
  wire \count[20]_i_6_n_0 ;
  wire \count[20]_i_7_n_0 ;
  wire \count_reg_n_0_[0] ;
  wire \count_reg_n_0_[10] ;
  wire \count_reg_n_0_[11] ;
  wire \count_reg_n_0_[12] ;
  wire \count_reg_n_0_[13] ;
  wire \count_reg_n_0_[14] ;
  wire \count_reg_n_0_[15] ;
  wire \count_reg_n_0_[16] ;
  wire \count_reg_n_0_[17] ;
  wire \count_reg_n_0_[18] ;
  wire \count_reg_n_0_[19] ;
  wire \count_reg_n_0_[1] ;
  wire \count_reg_n_0_[20] ;
  wire \count_reg_n_0_[2] ;
  wire \count_reg_n_0_[3] ;
  wire \count_reg_n_0_[4] ;
  wire \count_reg_n_0_[5] ;
  wire \count_reg_n_0_[6] ;
  wire \count_reg_n_0_[7] ;
  wire \count_reg_n_0_[8] ;
  wire \count_reg_n_0_[9] ;
  wire [2:0]div_bit;
  wire \div_bit[0]_i_1_n_0 ;
  wire \div_bit[1]_i_1_n_0 ;
  wire \div_bit[2]_i_1_n_0 ;
  wire \div_bit[2]_i_2_n_0 ;
  wire div_busy_reg_n_0;
  wire [28:0]div_difference;
  wire div_difference_carry__0_i_1_n_0;
  wire div_difference_carry__0_i_2_n_0;
  wire div_difference_carry__0_i_3_n_0;
  wire div_difference_carry__0_i_4_n_0;
  wire div_difference_carry__0_i_5_n_0;
  wire div_difference_carry__0_i_6_n_0;
  wire div_difference_carry__0_i_7_n_0;
  wire div_difference_carry__0_i_8_n_0;
  wire div_difference_carry__0_n_0;
  wire div_difference_carry__0_n_1;
  wire div_difference_carry__0_n_2;
  wire div_difference_carry__0_n_3;
  wire div_difference_carry__0_n_4;
  wire div_difference_carry__0_n_5;
  wire div_difference_carry__0_n_6;
  wire div_difference_carry__0_n_7;
  wire div_difference_carry__1_i_1_n_0;
  wire div_difference_carry__1_i_2_n_0;
  wire div_difference_carry__1_i_3_n_0;
  wire div_difference_carry__1_i_4_n_0;
  wire div_difference_carry__1_i_5_n_0;
  wire div_difference_carry__1_i_6_n_0;
  wire div_difference_carry__1_i_7_n_0;
  wire div_difference_carry__1_i_8_n_0;
  wire div_difference_carry__1_n_0;
  wire div_difference_carry__1_n_1;
  wire div_difference_carry__1_n_2;
  wire div_difference_carry__1_n_3;
  wire div_difference_carry__1_n_4;
  wire div_difference_carry__1_n_5;
  wire div_difference_carry__1_n_6;
  wire div_difference_carry__1_n_7;
  wire div_difference_carry__2_i_1_n_0;
  wire div_difference_carry__2_i_2_n_0;
  wire div_difference_carry__2_i_3_n_0;
  wire div_difference_carry__2_i_4_n_0;
  wire div_difference_carry__2_i_5_n_0;
  wire div_difference_carry__2_n_4;
  wire div_difference_carry__2_n_5;
  wire div_difference_carry__2_n_6;
  wire div_difference_carry__2_n_7;
  wire div_difference_carry_i_1_n_0;
  wire div_difference_carry_i_2_n_0;
  wire div_difference_carry_i_3_n_0;
  wire div_difference_carry_i_4_n_0;
  wire div_difference_carry_i_5_n_0;
  wire div_difference_carry_i_6_n_0;
  wire div_difference_carry_i_7_n_0;
  wire div_difference_carry_i_8_n_0;
  wire div_difference_carry_n_0;
  wire div_difference_carry_n_1;
  wire div_difference_carry_n_2;
  wire div_difference_carry_n_3;
  wire div_difference_carry_n_4;
  wire div_difference_carry_n_5;
  wire div_difference_carry_n_6;
  wire div_difference_carry_n_7;
  wire [7:1]div_quotient;
  wire \div_quotient[1]_i_1_n_0 ;
  wire \div_quotient[2]_i_1_n_0 ;
  wire \div_quotient[3]_i_1_n_0 ;
  wire \div_quotient[4]_i_1_n_0 ;
  wire \div_quotient[5]_i_1_n_0 ;
  wire \div_quotient[6]_i_1_n_0 ;
  wire \div_quotient[7]_i_1_n_0 ;
  wire [28:0]div_remainder;
  wire \div_remainder[28]_i_1_n_0 ;
  wire \div_remainder[7]_i_10_n_0 ;
  wire \div_remainder[7]_i_3_n_0 ;
  wire \div_remainder[7]_i_4_n_0 ;
  wire \div_remainder[7]_i_5_n_0 ;
  wire \div_remainder[7]_i_6_n_0 ;
  wire \div_remainder[7]_i_7_n_0 ;
  wire \div_remainder[7]_i_8_n_0 ;
  wire \div_remainder[7]_i_9_n_0 ;
  wire \div_remainder_reg[15]_i_2_n_0 ;
  wire \div_remainder_reg[15]_i_2_n_1 ;
  wire \div_remainder_reg[15]_i_2_n_2 ;
  wire \div_remainder_reg[15]_i_2_n_3 ;
  wire \div_remainder_reg[15]_i_2_n_4 ;
  wire \div_remainder_reg[15]_i_2_n_5 ;
  wire \div_remainder_reg[15]_i_2_n_6 ;
  wire \div_remainder_reg[15]_i_2_n_7 ;
  wire \div_remainder_reg[23]_i_2_n_0 ;
  wire \div_remainder_reg[23]_i_2_n_1 ;
  wire \div_remainder_reg[23]_i_2_n_2 ;
  wire \div_remainder_reg[23]_i_2_n_3 ;
  wire \div_remainder_reg[23]_i_2_n_4 ;
  wire \div_remainder_reg[23]_i_2_n_5 ;
  wire \div_remainder_reg[23]_i_2_n_6 ;
  wire \div_remainder_reg[23]_i_2_n_7 ;
  wire \div_remainder_reg[28]_i_3_n_4 ;
  wire \div_remainder_reg[28]_i_3_n_5 ;
  wire \div_remainder_reg[28]_i_3_n_6 ;
  wire \div_remainder_reg[28]_i_3_n_7 ;
  wire \div_remainder_reg[7]_i_2_n_0 ;
  wire \div_remainder_reg[7]_i_2_n_1 ;
  wire \div_remainder_reg[7]_i_2_n_2 ;
  wire \div_remainder_reg[7]_i_2_n_3 ;
  wire \div_remainder_reg[7]_i_2_n_4 ;
  wire \div_remainder_reg[7]_i_2_n_5 ;
  wire \div_remainder_reg[7]_i_2_n_6 ;
  wire \div_remainder_reg[7]_i_2_n_7 ;
  wire div_take;
  wire \div_trial[17]_i_1_n_0 ;
  wire \div_trial[20]_i_1_n_0 ;
  wire \div_trial[21]_i_1_n_0 ;
  wire \div_trial[21]_i_2_n_0 ;
  wire \div_trial[22]_i_1_n_0 ;
  wire \div_trial[23]_i_1_n_0 ;
  wire \div_trial[24]_i_1_n_0 ;
  wire \div_trial[25]_i_1_n_0 ;
  wire \div_trial[26]_i_1_n_0 ;
  wire \div_trial[27]_i_2_n_0 ;
  wire \div_trial[27]_i_3_n_0 ;
  wire \div_trial[27]_i_4_n_0 ;
  wire \div_trial[27]_i_5_n_0 ;
  wire \div_trial[27]_i_6_n_0 ;
  wire \div_trial_reg_n_0_[0] ;
  wire \div_trial_reg_n_0_[10] ;
  wire \div_trial_reg_n_0_[11] ;
  wire \div_trial_reg_n_0_[12] ;
  wire \div_trial_reg_n_0_[13] ;
  wire \div_trial_reg_n_0_[14] ;
  wire \div_trial_reg_n_0_[15] ;
  wire \div_trial_reg_n_0_[16] ;
  wire \div_trial_reg_n_0_[17] ;
  wire \div_trial_reg_n_0_[18] ;
  wire \div_trial_reg_n_0_[19] ;
  wire \div_trial_reg_n_0_[1] ;
  wire \div_trial_reg_n_0_[20] ;
  wire \div_trial_reg_n_0_[21] ;
  wire \div_trial_reg_n_0_[22] ;
  wire \div_trial_reg_n_0_[23] ;
  wire \div_trial_reg_n_0_[24] ;
  wire \div_trial_reg_n_0_[25] ;
  wire \div_trial_reg_n_0_[26] ;
  wire \div_trial_reg_n_0_[27] ;
  wire \div_trial_reg_n_0_[2] ;
  wire \div_trial_reg_n_0_[3] ;
  wire \div_trial_reg_n_0_[4] ;
  wire \div_trial_reg_n_0_[5] ;
  wire \div_trial_reg_n_0_[6] ;
  wire \div_trial_reg_n_0_[7] ;
  wire \div_trial_reg_n_0_[8] ;
  wire \div_trial_reg_n_0_[9] ;
  wire [28:0]division_numerator;
  wire \frame_mean[7]_i_2_n_0 ;
  wire \frame_mean_reg[5]_0 ;
  wire \frame_mean_reg[7]_0 ;
  wire frame_valid;
  wire frame_valid_i_1_n_0;
  wire frame_valid_reg_0;
  wire i___1_carry__0_i_1_n_0;
  wire i___1_carry__0_i_2_n_0;
  wire i___1_carry__0_i_3_n_0;
  wire i___1_carry_i_10_n_0;
  wire i___1_carry_i_11_n_0;
  wire i___1_carry_i_12_n_0;
  wire i___1_carry_i_13_n_0;
  wire i___1_carry_i_14_n_0;
  wire i___1_carry_i_15_n_0;
  wire i___1_carry_i_1_n_0;
  wire i___1_carry_i_2_n_0;
  wire i___1_carry_i_3_n_0;
  wire i___1_carry_i_4_n_0;
  wire i___1_carry_i_5_n_0;
  wire i___1_carry_i_6_n_0;
  wire i___1_carry_i_7_n_0;
  wire i___1_carry_i_8_n_0;
  wire i___1_carry_i_9_n_0;
  wire p_0_in;
  wire [28:0]p_2_in;
  wire [23:0]s_axis_tdata;
  wire s_axis_tready;
  wire s_axis_tuser;
  wire s_axis_tvalid;
  wire start_division;
  wire [7:0]status;
  wire [28:0]sum;
  wire \sum[15]_i_2_n_0 ;
  wire \sum[15]_i_3_n_0 ;
  wire \sum[15]_i_4_n_0 ;
  wire \sum[15]_i_5_n_0 ;
  wire \sum[15]_i_6_n_0 ;
  wire \sum[15]_i_7_n_0 ;
  wire \sum[15]_i_8_n_0 ;
  wire \sum[15]_i_9_n_0 ;
  wire \sum[23]_i_2_n_0 ;
  wire \sum[23]_i_3_n_0 ;
  wire \sum[23]_i_4_n_0 ;
  wire \sum[23]_i_5_n_0 ;
  wire \sum[23]_i_6_n_0 ;
  wire \sum[23]_i_7_n_0 ;
  wire \sum[23]_i_8_n_0 ;
  wire \sum[23]_i_9_n_0 ;
  wire \sum[28]_i_1_n_0 ;
  wire \sum[28]_i_3_n_0 ;
  wire \sum[28]_i_4_n_0 ;
  wire \sum[28]_i_5_n_0 ;
  wire \sum[28]_i_6_n_0 ;
  wire \sum[28]_i_7_n_0 ;
  wire \sum[7]_i_10_n_0 ;
  wire \sum[7]_i_11_n_0 ;
  wire \sum[7]_i_12_n_0 ;
  wire \sum[7]_i_13_n_0 ;
  wire \sum[7]_i_14_n_0 ;
  wire \sum[7]_i_15_n_0 ;
  wire \sum[7]_i_16_n_0 ;
  wire \sum[7]_i_17_n_0 ;
  wire \sum[7]_i_18_n_0 ;
  wire \sum[7]_i_1_n_0 ;
  wire \sum[7]_i_3_n_0 ;
  wire \sum[7]_i_4_n_0 ;
  wire \sum[7]_i_5_n_0 ;
  wire \sum[7]_i_6_n_0 ;
  wire \sum[7]_i_7_n_0 ;
  wire \sum[7]_i_8_n_0 ;
  wire \sum[7]_i_9_n_0 ;
  wire \sum_reg[15]_i_1_n_0 ;
  wire \sum_reg[15]_i_1_n_1 ;
  wire \sum_reg[15]_i_1_n_10 ;
  wire \sum_reg[15]_i_1_n_11 ;
  wire \sum_reg[15]_i_1_n_12 ;
  wire \sum_reg[15]_i_1_n_13 ;
  wire \sum_reg[15]_i_1_n_14 ;
  wire \sum_reg[15]_i_1_n_15 ;
  wire \sum_reg[15]_i_1_n_2 ;
  wire \sum_reg[15]_i_1_n_3 ;
  wire \sum_reg[15]_i_1_n_4 ;
  wire \sum_reg[15]_i_1_n_5 ;
  wire \sum_reg[15]_i_1_n_6 ;
  wire \sum_reg[15]_i_1_n_7 ;
  wire \sum_reg[15]_i_1_n_8 ;
  wire \sum_reg[15]_i_1_n_9 ;
  wire \sum_reg[23]_i_1_n_0 ;
  wire \sum_reg[23]_i_1_n_1 ;
  wire \sum_reg[23]_i_1_n_10 ;
  wire \sum_reg[23]_i_1_n_11 ;
  wire \sum_reg[23]_i_1_n_12 ;
  wire \sum_reg[23]_i_1_n_13 ;
  wire \sum_reg[23]_i_1_n_14 ;
  wire \sum_reg[23]_i_1_n_15 ;
  wire \sum_reg[23]_i_1_n_2 ;
  wire \sum_reg[23]_i_1_n_3 ;
  wire \sum_reg[23]_i_1_n_4 ;
  wire \sum_reg[23]_i_1_n_5 ;
  wire \sum_reg[23]_i_1_n_6 ;
  wire \sum_reg[23]_i_1_n_7 ;
  wire \sum_reg[23]_i_1_n_8 ;
  wire \sum_reg[23]_i_1_n_9 ;
  wire \sum_reg[28]_i_2_n_11 ;
  wire \sum_reg[28]_i_2_n_12 ;
  wire \sum_reg[28]_i_2_n_13 ;
  wire \sum_reg[28]_i_2_n_14 ;
  wire \sum_reg[28]_i_2_n_15 ;
  wire \sum_reg[28]_i_2_n_4 ;
  wire \sum_reg[28]_i_2_n_5 ;
  wire \sum_reg[28]_i_2_n_6 ;
  wire \sum_reg[28]_i_2_n_7 ;
  wire \sum_reg[7]_i_2_n_0 ;
  wire \sum_reg[7]_i_2_n_1 ;
  wire \sum_reg[7]_i_2_n_10 ;
  wire \sum_reg[7]_i_2_n_11 ;
  wire \sum_reg[7]_i_2_n_12 ;
  wire \sum_reg[7]_i_2_n_13 ;
  wire \sum_reg[7]_i_2_n_14 ;
  wire \sum_reg[7]_i_2_n_15 ;
  wire \sum_reg[7]_i_2_n_2 ;
  wire \sum_reg[7]_i_2_n_3 ;
  wire \sum_reg[7]_i_2_n_4 ;
  wire \sum_reg[7]_i_2_n_5 ;
  wire \sum_reg[7]_i_2_n_6 ;
  wire \sum_reg[7]_i_2_n_7 ;
  wire \sum_reg[7]_i_2_n_8 ;
  wire \sum_reg[7]_i_2_n_9 ;
  wire user_pipe;
  wire valid_pipe;
  wire valid_pipe_i_1_n_0;
  wire [7:0]y;
  wire [7:0]y_pipe;
  wire [12:3]y_sum0;
  wire y_sum0__1_carry__0_i_1_n_0;
  wire y_sum0__1_carry__0_i_2_n_0;
  wire y_sum0__1_carry__0_i_3_n_0;
  wire y_sum0__1_carry__0_n_7;
  wire y_sum0__1_carry_i_10_n_0;
  wire y_sum0__1_carry_i_11_n_0;
  wire y_sum0__1_carry_i_12_n_0;
  wire y_sum0__1_carry_i_13_n_0;
  wire y_sum0__1_carry_i_14_n_0;
  wire y_sum0__1_carry_i_15_n_0;
  wire y_sum0__1_carry_i_16_n_0;
  wire y_sum0__1_carry_i_17_n_0;
  wire y_sum0__1_carry_i_18_n_0;
  wire y_sum0__1_carry_i_1_n_0;
  wire y_sum0__1_carry_i_2_n_0;
  wire y_sum0__1_carry_i_3_n_0;
  wire y_sum0__1_carry_i_4_n_0;
  wire y_sum0__1_carry_i_5_n_0;
  wire y_sum0__1_carry_i_6_n_0;
  wire y_sum0__1_carry_i_7_n_0;
  wire y_sum0__1_carry_i_8_n_0;
  wire y_sum0__1_carry_i_9_n_0;
  wire y_sum0__1_carry_n_0;
  wire y_sum0__1_carry_n_1;
  wire y_sum0__1_carry_n_2;
  wire y_sum0__1_carry_n_3;
  wire y_sum0__1_carry_n_4;
  wire y_sum0__1_carry_n_5;
  wire y_sum0__1_carry_n_6;
  wire y_sum0__1_carry_n_7;
  wire [14:3]y_sum1;
  wire y_sum1__5_carry__0_i_1_n_0;
  wire y_sum1__5_carry__0_i_2_n_0;
  wire y_sum1__5_carry__0_i_3_n_0;
  wire y_sum1__5_carry__0_n_12;
  wire y_sum1__5_carry__0_n_13;
  wire y_sum1__5_carry__0_n_14;
  wire y_sum1__5_carry__0_n_15;
  wire y_sum1__5_carry__0_n_4;
  wire y_sum1__5_carry__0_n_5;
  wire y_sum1__5_carry__0_n_6;
  wire y_sum1__5_carry__0_n_7;
  wire y_sum1__5_carry_i_10_n_0;
  wire y_sum1__5_carry_i_11_n_0;
  wire y_sum1__5_carry_i_12_n_0;
  wire y_sum1__5_carry_i_13_n_0;
  wire y_sum1__5_carry_i_14_n_0;
  wire y_sum1__5_carry_i_15_n_0;
  wire y_sum1__5_carry_i_1_n_0;
  wire y_sum1__5_carry_i_2_n_0;
  wire y_sum1__5_carry_i_3_n_0;
  wire y_sum1__5_carry_i_4_n_0;
  wire y_sum1__5_carry_i_5_n_0;
  wire y_sum1__5_carry_i_6_n_0;
  wire y_sum1__5_carry_i_7_n_0;
  wire y_sum1__5_carry_i_8_n_0;
  wire y_sum1__5_carry_i_9_n_0;
  wire y_sum1__5_carry_n_0;
  wire y_sum1__5_carry_n_1;
  wire y_sum1__5_carry_n_10;
  wire y_sum1__5_carry_n_11;
  wire y_sum1__5_carry_n_12;
  wire y_sum1__5_carry_n_13;
  wire y_sum1__5_carry_n_14;
  wire y_sum1__5_carry_n_15;
  wire y_sum1__5_carry_n_2;
  wire y_sum1__5_carry_n_3;
  wire y_sum1__5_carry_n_4;
  wire y_sum1__5_carry_n_5;
  wire y_sum1__5_carry_n_6;
  wire y_sum1__5_carry_n_7;
  wire y_sum1__5_carry_n_8;
  wire y_sum1__5_carry_n_9;
  wire \y_sum1_inferred__0/i___1_carry__0_n_4 ;
  wire \y_sum1_inferred__0/i___1_carry__0_n_5 ;
  wire \y_sum1_inferred__0/i___1_carry__0_n_6 ;
  wire \y_sum1_inferred__0/i___1_carry__0_n_7 ;
  wire \y_sum1_inferred__0/i___1_carry_n_0 ;
  wire \y_sum1_inferred__0/i___1_carry_n_1 ;
  wire \y_sum1_inferred__0/i___1_carry_n_2 ;
  wire \y_sum1_inferred__0/i___1_carry_n_3 ;
  wire \y_sum1_inferred__0/i___1_carry_n_4 ;
  wire \y_sum1_inferred__0/i___1_carry_n_5 ;
  wire \y_sum1_inferred__0/i___1_carry_n_6 ;
  wire \y_sum1_inferred__0/i___1_carry_n_7 ;
  wire y_sum__41_carry__0_n_2;
  wire y_sum__41_carry__0_n_3;
  wire y_sum__41_carry__0_n_4;
  wire y_sum__41_carry__0_n_5;
  wire y_sum__41_carry__0_n_6;
  wire y_sum__41_carry__0_n_7;
  wire y_sum__41_carry_i_1__0_n_0;
  wire y_sum__41_carry_i_1_n_0;
  wire y_sum__41_carry_i_2__0_n_0;
  wire y_sum__41_carry_i_2_n_0;
  wire y_sum__41_carry_i_3__0_n_0;
  wire y_sum__41_carry_i_3_n_0;
  wire y_sum__41_carry_i_4__0_n_0;
  wire y_sum__41_carry_i_4_n_0;
  wire y_sum__41_carry_i_5__0_n_0;
  wire y_sum__41_carry_i_5_n_0;
  wire y_sum__41_carry_i_6__0_n_0;
  wire y_sum__41_carry_i_6_n_0;
  wire y_sum__41_carry_i_7__0_n_0;
  wire y_sum__41_carry_i_7_n_0;
  wire y_sum__41_carry_i_8_n_0;
  wire y_sum__41_carry_n_0;
  wire y_sum__41_carry_n_1;
  wire y_sum__41_carry_n_2;
  wire y_sum__41_carry_n_3;
  wire y_sum__41_carry_n_4;
  wire y_sum__41_carry_n_5;
  wire y_sum__41_carry_n_6;
  wire y_sum__41_carry_n_7;
  wire y_sum_carry__0_i_1_n_0;
  wire y_sum_carry__0_i_2_n_0;
  wire y_sum_carry__0_i_3_n_0;
  wire y_sum_carry__0_i_4_n_0;
  wire y_sum_carry__0_i_5_n_0;
  wire y_sum_carry__0_n_1;
  wire y_sum_carry__0_n_2;
  wire y_sum_carry__0_n_3;
  wire y_sum_carry__0_n_4;
  wire y_sum_carry__0_n_5;
  wire y_sum_carry__0_n_6;
  wire y_sum_carry__0_n_7;
  wire y_sum_carry_i_1_n_0;
  wire y_sum_carry_i_2_n_0;
  wire y_sum_carry_i_3_n_0;
  wire y_sum_carry_i_4_n_0;
  wire y_sum_carry_i_5_n_0;
  wire y_sum_carry_i_6_n_0;
  wire y_sum_carry_i_7_n_0;
  wire y_sum_carry_i_8_n_0;
  wire y_sum_carry_n_0;
  wire y_sum_carry_n_1;
  wire y_sum_carry_n_2;
  wire y_sum_carry_n_3;
  wire y_sum_carry_n_4;
  wire y_sum_carry_n_5;
  wire y_sum_carry_n_6;
  wire y_sum_carry_n_7;
  wire [7:3]NLW_count0_carry__1_CO_UNCONNECTED;
  wire [7:4]NLW_count0_carry__1_O_UNCONNECTED;
  wire [7:5]NLW_div_difference_carry__2_CO_UNCONNECTED;
  wire [7:5]NLW_div_difference_carry__2_O_UNCONNECTED;
  wire [7:4]\NLW_div_remainder_reg[28]_i_3_CO_UNCONNECTED ;
  wire [7:5]\NLW_div_remainder_reg[28]_i_3_O_UNCONNECTED ;
  wire [7:4]\NLW_sum_reg[28]_i_2_CO_UNCONNECTED ;
  wire [7:5]\NLW_sum_reg[28]_i_2_O_UNCONNECTED ;
  wire [7:1]NLW_y_sum0__1_carry__0_CO_UNCONNECTED;
  wire [7:2]NLW_y_sum0__1_carry__0_O_UNCONNECTED;
  wire [7:4]NLW_y_sum1__5_carry__0_CO_UNCONNECTED;
  wire [7:4]NLW_y_sum1__5_carry__0_O_UNCONNECTED;
  wire [7:4]\NLW_y_sum1_inferred__0/i___1_carry__0_CO_UNCONNECTED ;
  wire [7:4]\NLW_y_sum1_inferred__0/i___1_carry__0_O_UNCONNECTED ;
  wire [6:0]NLW_y_sum__41_carry_O_UNCONNECTED;
  wire [7:6]NLW_y_sum__41_carry__0_CO_UNCONNECTED;
  wire [7:7]NLW_y_sum__41_carry__0_O_UNCONNECTED;
  wire [0:0]NLW_y_sum_carry_O_UNCONNECTED;
  wire [7:7]NLW_y_sum_carry__0_CO_UNCONNECTED;
  wire [7:7]NLW_y_sum_carry__0_O_UNCONNECTED;

  LUT4 #(
    .INIT(16'h00F7)) 
    analog_gain0_carry_i_1
       (.I0(status[5]),
        .I1(status[6]),
        .I2(analog_gain0_carry_i_7_n_0),
        .I3(status[7]),
        .O(\frame_mean_reg[5]_0 ));
  LUT2 #(
    .INIT(4'h9)) 
    analog_gain0_carry_i_4
       (.I0(\frame_mean_reg[5]_0 ),
        .I1(\analog_gain_reg[7]_2 [1]),
        .O(S[1]));
  LUT2 #(
    .INIT(4'h9)) 
    analog_gain0_carry_i_5
       (.I0(\frame_mean_reg[5]_0 ),
        .I1(\analog_gain_reg[7]_2 [0]),
        .O(S[0]));
  LUT5 #(
    .INIT(32'h0000777F)) 
    analog_gain0_carry_i_7
       (.I0(status[2]),
        .I1(status[3]),
        .I2(status[1]),
        .I3(status[0]),
        .I4(status[4]),
        .O(analog_gain0_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h0080AA8000800080)) 
    \analog_gain[7]_i_1 
       (.I0(frame_valid_reg_0),
        .I1(\analog_gain_reg[7] ),
        .I2(\frame_mean_reg[7]_0 ),
        .I3(\frame_mean_reg[5]_0 ),
        .I4(coarse_integration23_in),
        .I5(\analog_gain_reg[7]_0 ),
        .O(E));
  LUT2 #(
    .INIT(4'h2)) 
    \analog_gain[7]_i_2 
       (.I0(frame_valid),
        .I1(\analog_gain_reg[7]_1 ),
        .O(frame_valid_reg_0));
  LUT6 #(
    .INIT(64'hEEEAAAAAAAAAAAAA)) 
    \analog_gain[7]_i_4 
       (.I0(status[7]),
        .I1(status[6]),
        .I2(status[3]),
        .I3(status[2]),
        .I4(status[4]),
        .I5(status[5]),
        .O(\frame_mean_reg[7]_0 ));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 count0_carry
       (.CI(\count_reg_n_0_[0] ),
        .CI_TOP(1'b0),
        .CO({count0_carry_n_0,count0_carry_n_1,count0_carry_n_2,count0_carry_n_3,count0_carry_n_4,count0_carry_n_5,count0_carry_n_6,count0_carry_n_7}),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O(count0[8:1]),
        .S({\count_reg_n_0_[8] ,\count_reg_n_0_[7] ,\count_reg_n_0_[6] ,\count_reg_n_0_[5] ,\count_reg_n_0_[4] ,\count_reg_n_0_[3] ,\count_reg_n_0_[2] ,\count_reg_n_0_[1] }));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 count0_carry__0
       (.CI(count0_carry_n_0),
        .CI_TOP(1'b0),
        .CO({count0_carry__0_n_0,count0_carry__0_n_1,count0_carry__0_n_2,count0_carry__0_n_3,count0_carry__0_n_4,count0_carry__0_n_5,count0_carry__0_n_6,count0_carry__0_n_7}),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O(count0[16:9]),
        .S({\count_reg_n_0_[16] ,\count_reg_n_0_[15] ,\count_reg_n_0_[14] ,\count_reg_n_0_[13] ,\count_reg_n_0_[12] ,\count_reg_n_0_[11] ,\count_reg_n_0_[10] ,\count_reg_n_0_[9] }));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 count0_carry__1
       (.CI(count0_carry__0_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_count0_carry__1_CO_UNCONNECTED[7:3],count0_carry__1_n_5,count0_carry__1_n_6,count0_carry__1_n_7}),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O({NLW_count0_carry__1_O_UNCONNECTED[7:4],count0[20:17]}),
        .S({1'b0,1'b0,1'b0,1'b0,\count_reg_n_0_[20] ,\count_reg_n_0_[19] ,\count_reg_n_0_[18] ,\count_reg_n_0_[17] }));
  LUT4 #(
    .INIT(16'hAFB0)) 
    \count[0]_i_1 
       (.I0(user_pipe),
        .I1(p_0_in),
        .I2(valid_pipe),
        .I3(\count_reg_n_0_[0] ),
        .O(\count[0]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'hA8FF)) 
    \count[20]_i_1 
       (.I0(valid_pipe),
        .I1(user_pipe),
        .I2(p_0_in),
        .I3(aresetn),
        .O(count));
  LUT5 #(
    .INIT(32'h00000002)) 
    \count[20]_i_2 
       (.I0(valid_pipe),
        .I1(user_pipe),
        .I2(\count[20]_i_3_n_0 ),
        .I3(\count[20]_i_4_n_0 ),
        .I4(\count[20]_i_5_n_0 ),
        .O(p_0_in));
  LUT5 #(
    .INIT(32'hFFFFFFEF)) 
    \count[20]_i_3 
       (.I0(\count_reg_n_0_[14] ),
        .I1(\count_reg_n_0_[12] ),
        .I2(\count_reg_n_0_[19] ),
        .I3(\count_reg_n_0_[10] ),
        .I4(\count_reg_n_0_[11] ),
        .O(\count[20]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'hFFFF7FFF)) 
    \count[20]_i_4 
       (.I0(\count_reg_n_0_[5] ),
        .I1(\count_reg_n_0_[4] ),
        .I2(\count_reg_n_0_[7] ),
        .I3(\count_reg_n_0_[6] ),
        .I4(\count[20]_i_6_n_0 ),
        .O(\count[20]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'hFFFF7FFF)) 
    \count[20]_i_5 
       (.I0(\count_reg_n_0_[13] ),
        .I1(\count_reg_n_0_[17] ),
        .I2(\count_reg_n_0_[15] ),
        .I3(\count_reg_n_0_[16] ),
        .I4(\count[20]_i_7_n_0 ),
        .O(\count[20]_i_5_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT4 #(
    .INIT(16'h7FFF)) 
    \count[20]_i_6 
       (.I0(\count_reg_n_0_[2] ),
        .I1(\count_reg_n_0_[3] ),
        .I2(\count_reg_n_0_[0] ),
        .I3(\count_reg_n_0_[1] ),
        .O(\count[20]_i_6_n_0 ));
  LUT4 #(
    .INIT(16'h7FFF)) 
    \count[20]_i_7 
       (.I0(\count_reg_n_0_[20] ),
        .I1(\count_reg_n_0_[18] ),
        .I2(\count_reg_n_0_[8] ),
        .I3(\count_reg_n_0_[9] ),
        .O(\count[20]_i_7_n_0 ));
  FDRE \count_reg[0] 
       (.C(aclk),
        .CE(1'b1),
        .D(\count[0]_i_1_n_0 ),
        .Q(\count_reg_n_0_[0] ),
        .R(SR));
  FDRE \count_reg[10] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[10]),
        .Q(\count_reg_n_0_[10] ),
        .R(count));
  FDRE \count_reg[11] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[11]),
        .Q(\count_reg_n_0_[11] ),
        .R(count));
  FDRE \count_reg[12] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[12]),
        .Q(\count_reg_n_0_[12] ),
        .R(count));
  FDRE \count_reg[13] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[13]),
        .Q(\count_reg_n_0_[13] ),
        .R(count));
  FDRE \count_reg[14] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[14]),
        .Q(\count_reg_n_0_[14] ),
        .R(count));
  FDRE \count_reg[15] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[15]),
        .Q(\count_reg_n_0_[15] ),
        .R(count));
  FDRE \count_reg[16] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[16]),
        .Q(\count_reg_n_0_[16] ),
        .R(count));
  FDRE \count_reg[17] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[17]),
        .Q(\count_reg_n_0_[17] ),
        .R(count));
  FDRE \count_reg[18] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[18]),
        .Q(\count_reg_n_0_[18] ),
        .R(count));
  FDRE \count_reg[19] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[19]),
        .Q(\count_reg_n_0_[19] ),
        .R(count));
  FDRE \count_reg[1] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[1]),
        .Q(\count_reg_n_0_[1] ),
        .R(count));
  FDRE \count_reg[20] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[20]),
        .Q(\count_reg_n_0_[20] ),
        .R(count));
  FDRE \count_reg[2] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[2]),
        .Q(\count_reg_n_0_[2] ),
        .R(count));
  FDRE \count_reg[3] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[3]),
        .Q(\count_reg_n_0_[3] ),
        .R(count));
  FDRE \count_reg[4] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[4]),
        .Q(\count_reg_n_0_[4] ),
        .R(count));
  FDRE \count_reg[5] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[5]),
        .Q(\count_reg_n_0_[5] ),
        .R(count));
  FDRE \count_reg[6] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[6]),
        .Q(\count_reg_n_0_[6] ),
        .R(count));
  FDRE \count_reg[7] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[7]),
        .Q(\count_reg_n_0_[7] ),
        .R(count));
  FDRE \count_reg[8] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[8]),
        .Q(\count_reg_n_0_[8] ),
        .R(count));
  FDRE \count_reg[9] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(count0[9]),
        .Q(\count_reg_n_0_[9] ),
        .R(count));
  (* SOFT_HLUTNM = "soft_lutpair20" *) 
  LUT2 #(
    .INIT(4'hB)) 
    \div_bit[0]_i_1 
       (.I0(start_division),
        .I1(div_bit[0]),
        .O(\div_bit[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT3 #(
    .INIT(8'hEB)) 
    \div_bit[1]_i_1 
       (.I0(start_division),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .O(\div_bit[1]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hFFFFFE00)) 
    \div_bit[2]_i_1 
       (.I0(div_bit[2]),
        .I1(div_bit[0]),
        .I2(div_bit[1]),
        .I3(div_busy_reg_n_0),
        .I4(start_division),
        .O(\div_bit[2]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT4 #(
    .INIT(16'hEEEB)) 
    \div_bit[2]_i_2 
       (.I0(start_division),
        .I1(div_bit[2]),
        .I2(div_bit[0]),
        .I3(div_bit[1]),
        .O(\div_bit[2]_i_2_n_0 ));
  FDRE \div_bit_reg[0] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_bit[0]_i_1_n_0 ),
        .Q(div_bit[0]),
        .R(SR));
  FDRE \div_bit_reg[1] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_bit[1]_i_1_n_0 ),
        .Q(div_bit[1]),
        .R(SR));
  FDRE \div_bit_reg[2] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_bit[2]_i_2_n_0 ),
        .Q(div_bit[2]),
        .R(SR));
  FDRE div_busy_reg
       (.C(aclk),
        .CE(1'b1),
        .D(\div_bit[2]_i_1_n_0 ),
        .Q(div_busy_reg_n_0),
        .R(SR));
  CARRY8 div_difference_carry
       (.CI(1'b1),
        .CI_TOP(1'b0),
        .CO({div_difference_carry_n_0,div_difference_carry_n_1,div_difference_carry_n_2,div_difference_carry_n_3,div_difference_carry_n_4,div_difference_carry_n_5,div_difference_carry_n_6,div_difference_carry_n_7}),
        .DI(div_remainder[7:0]),
        .O(div_difference[7:0]),
        .S({div_difference_carry_i_1_n_0,div_difference_carry_i_2_n_0,div_difference_carry_i_3_n_0,div_difference_carry_i_4_n_0,div_difference_carry_i_5_n_0,div_difference_carry_i_6_n_0,div_difference_carry_i_7_n_0,div_difference_carry_i_8_n_0}));
  CARRY8 div_difference_carry__0
       (.CI(div_difference_carry_n_0),
        .CI_TOP(1'b0),
        .CO({div_difference_carry__0_n_0,div_difference_carry__0_n_1,div_difference_carry__0_n_2,div_difference_carry__0_n_3,div_difference_carry__0_n_4,div_difference_carry__0_n_5,div_difference_carry__0_n_6,div_difference_carry__0_n_7}),
        .DI(div_remainder[15:8]),
        .O(div_difference[15:8]),
        .S({div_difference_carry__0_i_1_n_0,div_difference_carry__0_i_2_n_0,div_difference_carry__0_i_3_n_0,div_difference_carry__0_i_4_n_0,div_difference_carry__0_i_5_n_0,div_difference_carry__0_i_6_n_0,div_difference_carry__0_i_7_n_0,div_difference_carry__0_i_8_n_0}));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_1
       (.I0(div_remainder[15]),
        .I1(\div_trial_reg_n_0_[15] ),
        .O(div_difference_carry__0_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_2
       (.I0(div_remainder[14]),
        .I1(\div_trial_reg_n_0_[14] ),
        .O(div_difference_carry__0_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_3
       (.I0(div_remainder[13]),
        .I1(\div_trial_reg_n_0_[13] ),
        .O(div_difference_carry__0_i_3_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_4
       (.I0(div_remainder[12]),
        .I1(\div_trial_reg_n_0_[12] ),
        .O(div_difference_carry__0_i_4_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_5
       (.I0(div_remainder[11]),
        .I1(\div_trial_reg_n_0_[11] ),
        .O(div_difference_carry__0_i_5_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_6
       (.I0(div_remainder[10]),
        .I1(\div_trial_reg_n_0_[10] ),
        .O(div_difference_carry__0_i_6_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_7
       (.I0(div_remainder[9]),
        .I1(\div_trial_reg_n_0_[9] ),
        .O(div_difference_carry__0_i_7_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__0_i_8
       (.I0(div_remainder[8]),
        .I1(\div_trial_reg_n_0_[8] ),
        .O(div_difference_carry__0_i_8_n_0));
  CARRY8 div_difference_carry__1
       (.CI(div_difference_carry__0_n_0),
        .CI_TOP(1'b0),
        .CO({div_difference_carry__1_n_0,div_difference_carry__1_n_1,div_difference_carry__1_n_2,div_difference_carry__1_n_3,div_difference_carry__1_n_4,div_difference_carry__1_n_5,div_difference_carry__1_n_6,div_difference_carry__1_n_7}),
        .DI(div_remainder[23:16]),
        .O(div_difference[23:16]),
        .S({div_difference_carry__1_i_1_n_0,div_difference_carry__1_i_2_n_0,div_difference_carry__1_i_3_n_0,div_difference_carry__1_i_4_n_0,div_difference_carry__1_i_5_n_0,div_difference_carry__1_i_6_n_0,div_difference_carry__1_i_7_n_0,div_difference_carry__1_i_8_n_0}));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_1
       (.I0(div_remainder[23]),
        .I1(\div_trial_reg_n_0_[23] ),
        .O(div_difference_carry__1_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_2
       (.I0(div_remainder[22]),
        .I1(\div_trial_reg_n_0_[22] ),
        .O(div_difference_carry__1_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_3
       (.I0(div_remainder[21]),
        .I1(\div_trial_reg_n_0_[21] ),
        .O(div_difference_carry__1_i_3_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_4
       (.I0(div_remainder[20]),
        .I1(\div_trial_reg_n_0_[20] ),
        .O(div_difference_carry__1_i_4_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_5
       (.I0(div_remainder[19]),
        .I1(\div_trial_reg_n_0_[19] ),
        .O(div_difference_carry__1_i_5_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_6
       (.I0(div_remainder[18]),
        .I1(\div_trial_reg_n_0_[18] ),
        .O(div_difference_carry__1_i_6_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_7
       (.I0(div_remainder[17]),
        .I1(\div_trial_reg_n_0_[17] ),
        .O(div_difference_carry__1_i_7_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__1_i_8
       (.I0(div_remainder[16]),
        .I1(\div_trial_reg_n_0_[16] ),
        .O(div_difference_carry__1_i_8_n_0));
  CARRY8 div_difference_carry__2
       (.CI(div_difference_carry__1_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_div_difference_carry__2_CO_UNCONNECTED[7:5],div_take,div_difference_carry__2_n_4,div_difference_carry__2_n_5,div_difference_carry__2_n_6,div_difference_carry__2_n_7}),
        .DI({1'b0,1'b0,1'b0,div_remainder[28:24]}),
        .O({NLW_div_difference_carry__2_O_UNCONNECTED[7:5],div_difference[28:24]}),
        .S({1'b0,1'b0,1'b0,div_difference_carry__2_i_1_n_0,div_difference_carry__2_i_2_n_0,div_difference_carry__2_i_3_n_0,div_difference_carry__2_i_4_n_0,div_difference_carry__2_i_5_n_0}));
  LUT1 #(
    .INIT(2'h1)) 
    div_difference_carry__2_i_1
       (.I0(div_remainder[28]),
        .O(div_difference_carry__2_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__2_i_2
       (.I0(div_remainder[27]),
        .I1(\div_trial_reg_n_0_[27] ),
        .O(div_difference_carry__2_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__2_i_3
       (.I0(div_remainder[26]),
        .I1(\div_trial_reg_n_0_[26] ),
        .O(div_difference_carry__2_i_3_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__2_i_4
       (.I0(div_remainder[25]),
        .I1(\div_trial_reg_n_0_[25] ),
        .O(div_difference_carry__2_i_4_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry__2_i_5
       (.I0(div_remainder[24]),
        .I1(\div_trial_reg_n_0_[24] ),
        .O(div_difference_carry__2_i_5_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_1
       (.I0(div_remainder[7]),
        .I1(\div_trial_reg_n_0_[7] ),
        .O(div_difference_carry_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_2
       (.I0(div_remainder[6]),
        .I1(\div_trial_reg_n_0_[6] ),
        .O(div_difference_carry_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_3
       (.I0(div_remainder[5]),
        .I1(\div_trial_reg_n_0_[5] ),
        .O(div_difference_carry_i_3_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_4
       (.I0(div_remainder[4]),
        .I1(\div_trial_reg_n_0_[4] ),
        .O(div_difference_carry_i_4_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_5
       (.I0(div_remainder[3]),
        .I1(\div_trial_reg_n_0_[3] ),
        .O(div_difference_carry_i_5_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_6
       (.I0(div_remainder[2]),
        .I1(\div_trial_reg_n_0_[2] ),
        .O(div_difference_carry_i_6_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_7
       (.I0(div_remainder[1]),
        .I1(\div_trial_reg_n_0_[1] ),
        .O(div_difference_carry_i_7_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    div_difference_carry_i_8
       (.I0(div_remainder[0]),
        .I1(\div_trial_reg_n_0_[0] ),
        .O(div_difference_carry_i_8_n_0));
  LUT6 #(
    .INIT(64'hFFFFFFFF00200000)) 
    \div_quotient[1]_i_1 
       (.I0(div_take),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .I3(div_bit[2]),
        .I4(div_busy_reg_n_0),
        .I5(div_quotient[1]),
        .O(\div_quotient[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFF00200000)) 
    \div_quotient[2]_i_1 
       (.I0(div_take),
        .I1(div_bit[0]),
        .I2(div_bit[1]),
        .I3(div_bit[2]),
        .I4(div_busy_reg_n_0),
        .I5(div_quotient[2]),
        .O(\div_quotient[2]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFF00800000)) 
    \div_quotient[3]_i_1 
       (.I0(div_take),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .I3(div_bit[2]),
        .I4(div_busy_reg_n_0),
        .I5(div_quotient[3]),
        .O(\div_quotient[3]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFF02000000)) 
    \div_quotient[4]_i_1 
       (.I0(div_take),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .I3(div_bit[2]),
        .I4(div_busy_reg_n_0),
        .I5(div_quotient[4]),
        .O(\div_quotient[4]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFF20000000)) 
    \div_quotient[5]_i_1 
       (.I0(div_take),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .I3(div_bit[2]),
        .I4(div_busy_reg_n_0),
        .I5(div_quotient[5]),
        .O(\div_quotient[5]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFF20000000)) 
    \div_quotient[6]_i_1 
       (.I0(div_take),
        .I1(div_bit[0]),
        .I2(div_bit[1]),
        .I3(div_bit[2]),
        .I4(div_busy_reg_n_0),
        .I5(div_quotient[6]),
        .O(\div_quotient[6]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFF80000000)) 
    \div_quotient[7]_i_1 
       (.I0(div_take),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .I3(div_bit[2]),
        .I4(div_busy_reg_n_0),
        .I5(div_quotient[7]),
        .O(\div_quotient[7]_i_1_n_0 ));
  FDRE \div_quotient_reg[1] 
       (.C(aclk),
        .CE(1'b1),
        .D(\div_quotient[1]_i_1_n_0 ),
        .Q(div_quotient[1]),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_quotient_reg[2] 
       (.C(aclk),
        .CE(1'b1),
        .D(\div_quotient[2]_i_1_n_0 ),
        .Q(div_quotient[2]),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_quotient_reg[3] 
       (.C(aclk),
        .CE(1'b1),
        .D(\div_quotient[3]_i_1_n_0 ),
        .Q(div_quotient[3]),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_quotient_reg[4] 
       (.C(aclk),
        .CE(1'b1),
        .D(\div_quotient[4]_i_1_n_0 ),
        .Q(div_quotient[4]),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_quotient_reg[5] 
       (.C(aclk),
        .CE(1'b1),
        .D(\div_quotient[5]_i_1_n_0 ),
        .Q(div_quotient[5]),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_quotient_reg[6] 
       (.C(aclk),
        .CE(1'b1),
        .D(\div_quotient[6]_i_1_n_0 ),
        .Q(div_quotient[6]),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_quotient_reg[7] 
       (.C(aclk),
        .CE(1'b1),
        .D(\div_quotient[7]_i_1_n_0 ),
        .Q(div_quotient[7]),
        .R(\div_trial[21]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[0]_i_1 
       (.I0(division_numerator[0]),
        .I1(div_difference[0]),
        .I2(start_division),
        .O(p_2_in[0]));
  (* SOFT_HLUTNM = "soft_lutpair11" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[10]_i_1 
       (.I0(division_numerator[10]),
        .I1(div_difference[10]),
        .I2(start_division),
        .O(p_2_in[10]));
  (* SOFT_HLUTNM = "soft_lutpair11" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[11]_i_1 
       (.I0(division_numerator[11]),
        .I1(div_difference[11]),
        .I2(start_division),
        .O(p_2_in[11]));
  (* SOFT_HLUTNM = "soft_lutpair12" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[12]_i_1 
       (.I0(division_numerator[12]),
        .I1(div_difference[12]),
        .I2(start_division),
        .O(p_2_in[12]));
  (* SOFT_HLUTNM = "soft_lutpair12" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[13]_i_1 
       (.I0(division_numerator[13]),
        .I1(div_difference[13]),
        .I2(start_division),
        .O(p_2_in[13]));
  (* SOFT_HLUTNM = "soft_lutpair13" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[14]_i_1 
       (.I0(division_numerator[14]),
        .I1(div_difference[14]),
        .I2(start_division),
        .O(p_2_in[14]));
  (* SOFT_HLUTNM = "soft_lutpair13" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[15]_i_1 
       (.I0(division_numerator[15]),
        .I1(div_difference[15]),
        .I2(start_division),
        .O(p_2_in[15]));
  (* SOFT_HLUTNM = "soft_lutpair14" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[16]_i_1 
       (.I0(division_numerator[16]),
        .I1(div_difference[16]),
        .I2(start_division),
        .O(p_2_in[16]));
  (* SOFT_HLUTNM = "soft_lutpair14" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[17]_i_1 
       (.I0(division_numerator[17]),
        .I1(div_difference[17]),
        .I2(start_division),
        .O(p_2_in[17]));
  (* SOFT_HLUTNM = "soft_lutpair15" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[18]_i_1 
       (.I0(division_numerator[18]),
        .I1(div_difference[18]),
        .I2(start_division),
        .O(p_2_in[18]));
  (* SOFT_HLUTNM = "soft_lutpair15" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[19]_i_1 
       (.I0(division_numerator[19]),
        .I1(div_difference[19]),
        .I2(start_division),
        .O(p_2_in[19]));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[1]_i_1 
       (.I0(division_numerator[1]),
        .I1(div_difference[1]),
        .I2(start_division),
        .O(p_2_in[1]));
  (* SOFT_HLUTNM = "soft_lutpair16" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[20]_i_1 
       (.I0(division_numerator[20]),
        .I1(div_difference[20]),
        .I2(start_division),
        .O(p_2_in[20]));
  (* SOFT_HLUTNM = "soft_lutpair16" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[21]_i_1 
       (.I0(division_numerator[21]),
        .I1(div_difference[21]),
        .I2(start_division),
        .O(p_2_in[21]));
  (* SOFT_HLUTNM = "soft_lutpair17" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[22]_i_1 
       (.I0(division_numerator[22]),
        .I1(div_difference[22]),
        .I2(start_division),
        .O(p_2_in[22]));
  (* SOFT_HLUTNM = "soft_lutpair17" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[23]_i_1 
       (.I0(division_numerator[23]),
        .I1(div_difference[23]),
        .I2(start_division),
        .O(p_2_in[23]));
  (* SOFT_HLUTNM = "soft_lutpair18" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[24]_i_1 
       (.I0(division_numerator[24]),
        .I1(div_difference[24]),
        .I2(start_division),
        .O(p_2_in[24]));
  (* SOFT_HLUTNM = "soft_lutpair18" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[25]_i_1 
       (.I0(division_numerator[25]),
        .I1(div_difference[25]),
        .I2(start_division),
        .O(p_2_in[25]));
  (* SOFT_HLUTNM = "soft_lutpair19" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[26]_i_1 
       (.I0(division_numerator[26]),
        .I1(div_difference[26]),
        .I2(start_division),
        .O(p_2_in[26]));
  (* SOFT_HLUTNM = "soft_lutpair19" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[27]_i_1 
       (.I0(division_numerator[27]),
        .I1(div_difference[27]),
        .I2(start_division),
        .O(p_2_in[27]));
  LUT3 #(
    .INIT(8'hEA)) 
    \div_remainder[28]_i_1 
       (.I0(start_division),
        .I1(div_take),
        .I2(div_busy_reg_n_0),
        .O(\div_remainder[28]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair20" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[28]_i_2 
       (.I0(division_numerator[28]),
        .I1(div_difference[28]),
        .I2(start_division),
        .O(p_2_in[28]));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[2]_i_1 
       (.I0(division_numerator[2]),
        .I1(div_difference[2]),
        .I2(start_division),
        .O(p_2_in[2]));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[3]_i_1 
       (.I0(division_numerator[3]),
        .I1(div_difference[3]),
        .I2(start_division),
        .O(p_2_in[3]));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[4]_i_1 
       (.I0(division_numerator[4]),
        .I1(div_difference[4]),
        .I2(start_division),
        .O(p_2_in[4]));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[5]_i_1 
       (.I0(division_numerator[5]),
        .I1(div_difference[5]),
        .I2(start_division),
        .O(p_2_in[5]));
  (* SOFT_HLUTNM = "soft_lutpair9" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[6]_i_1 
       (.I0(division_numerator[6]),
        .I1(div_difference[6]),
        .I2(start_division),
        .O(p_2_in[6]));
  (* SOFT_HLUTNM = "soft_lutpair9" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[7]_i_1 
       (.I0(division_numerator[7]),
        .I1(div_difference[7]),
        .I2(start_division),
        .O(p_2_in[7]));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_10 
       (.I0(sum[0]),
        .I1(y_pipe[0]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_10_n_0 ));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_3 
       (.I0(sum[7]),
        .I1(y_pipe[7]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_3_n_0 ));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_4 
       (.I0(sum[6]),
        .I1(y_pipe[6]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_4_n_0 ));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_5 
       (.I0(sum[5]),
        .I1(y_pipe[5]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_5_n_0 ));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_6 
       (.I0(sum[4]),
        .I1(y_pipe[4]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_6_n_0 ));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_7 
       (.I0(sum[3]),
        .I1(y_pipe[3]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_7_n_0 ));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_8 
       (.I0(sum[2]),
        .I1(y_pipe[2]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_8_n_0 ));
  LUT3 #(
    .INIT(8'h6A)) 
    \div_remainder[7]_i_9 
       (.I0(sum[1]),
        .I1(y_pipe[1]),
        .I2(p_0_in),
        .O(\div_remainder[7]_i_9_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair10" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[8]_i_1 
       (.I0(division_numerator[8]),
        .I1(div_difference[8]),
        .I2(start_division),
        .O(p_2_in[8]));
  (* SOFT_HLUTNM = "soft_lutpair10" *) 
  LUT3 #(
    .INIT(8'hAC)) 
    \div_remainder[9]_i_1 
       (.I0(division_numerator[9]),
        .I1(div_difference[9]),
        .I2(start_division),
        .O(p_2_in[9]));
  FDRE \div_remainder_reg[0] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[0]),
        .Q(div_remainder[0]),
        .R(SR));
  FDRE \div_remainder_reg[10] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[10]),
        .Q(div_remainder[10]),
        .R(SR));
  FDRE \div_remainder_reg[11] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[11]),
        .Q(div_remainder[11]),
        .R(SR));
  FDRE \div_remainder_reg[12] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[12]),
        .Q(div_remainder[12]),
        .R(SR));
  FDRE \div_remainder_reg[13] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[13]),
        .Q(div_remainder[13]),
        .R(SR));
  FDRE \div_remainder_reg[14] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[14]),
        .Q(div_remainder[14]),
        .R(SR));
  FDRE \div_remainder_reg[15] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[15]),
        .Q(div_remainder[15]),
        .R(SR));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 \div_remainder_reg[15]_i_2 
       (.CI(\div_remainder_reg[7]_i_2_n_0 ),
        .CI_TOP(1'b0),
        .CO({\div_remainder_reg[15]_i_2_n_0 ,\div_remainder_reg[15]_i_2_n_1 ,\div_remainder_reg[15]_i_2_n_2 ,\div_remainder_reg[15]_i_2_n_3 ,\div_remainder_reg[15]_i_2_n_4 ,\div_remainder_reg[15]_i_2_n_5 ,\div_remainder_reg[15]_i_2_n_6 ,\div_remainder_reg[15]_i_2_n_7 }),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O(division_numerator[15:8]),
        .S(sum[15:8]));
  FDRE \div_remainder_reg[16] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[16]),
        .Q(div_remainder[16]),
        .R(SR));
  FDRE \div_remainder_reg[17] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[17]),
        .Q(div_remainder[17]),
        .R(SR));
  FDRE \div_remainder_reg[18] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[18]),
        .Q(div_remainder[18]),
        .R(SR));
  FDRE \div_remainder_reg[19] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[19]),
        .Q(div_remainder[19]),
        .R(SR));
  FDRE \div_remainder_reg[1] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[1]),
        .Q(div_remainder[1]),
        .R(SR));
  FDRE \div_remainder_reg[20] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[20]),
        .Q(div_remainder[20]),
        .R(SR));
  FDRE \div_remainder_reg[21] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[21]),
        .Q(div_remainder[21]),
        .R(SR));
  FDRE \div_remainder_reg[22] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[22]),
        .Q(div_remainder[22]),
        .R(SR));
  FDRE \div_remainder_reg[23] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[23]),
        .Q(div_remainder[23]),
        .R(SR));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 \div_remainder_reg[23]_i_2 
       (.CI(\div_remainder_reg[15]_i_2_n_0 ),
        .CI_TOP(1'b0),
        .CO({\div_remainder_reg[23]_i_2_n_0 ,\div_remainder_reg[23]_i_2_n_1 ,\div_remainder_reg[23]_i_2_n_2 ,\div_remainder_reg[23]_i_2_n_3 ,\div_remainder_reg[23]_i_2_n_4 ,\div_remainder_reg[23]_i_2_n_5 ,\div_remainder_reg[23]_i_2_n_6 ,\div_remainder_reg[23]_i_2_n_7 }),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O(division_numerator[23:16]),
        .S(sum[23:16]));
  FDRE \div_remainder_reg[24] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[24]),
        .Q(div_remainder[24]),
        .R(SR));
  FDRE \div_remainder_reg[25] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[25]),
        .Q(div_remainder[25]),
        .R(SR));
  FDRE \div_remainder_reg[26] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[26]),
        .Q(div_remainder[26]),
        .R(SR));
  FDRE \div_remainder_reg[27] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[27]),
        .Q(div_remainder[27]),
        .R(SR));
  FDRE \div_remainder_reg[28] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[28]),
        .Q(div_remainder[28]),
        .R(SR));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 \div_remainder_reg[28]_i_3 
       (.CI(\div_remainder_reg[23]_i_2_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_div_remainder_reg[28]_i_3_CO_UNCONNECTED [7:4],\div_remainder_reg[28]_i_3_n_4 ,\div_remainder_reg[28]_i_3_n_5 ,\div_remainder_reg[28]_i_3_n_6 ,\div_remainder_reg[28]_i_3_n_7 }),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O({\NLW_div_remainder_reg[28]_i_3_O_UNCONNECTED [7:5],division_numerator[28:24]}),
        .S({1'b0,1'b0,1'b0,sum[28:24]}));
  FDRE \div_remainder_reg[2] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[2]),
        .Q(div_remainder[2]),
        .R(SR));
  FDRE \div_remainder_reg[3] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[3]),
        .Q(div_remainder[3]),
        .R(SR));
  FDRE \div_remainder_reg[4] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[4]),
        .Q(div_remainder[4]),
        .R(SR));
  FDRE \div_remainder_reg[5] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[5]),
        .Q(div_remainder[5]),
        .R(SR));
  FDRE \div_remainder_reg[6] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[6]),
        .Q(div_remainder[6]),
        .R(SR));
  FDRE \div_remainder_reg[7] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[7]),
        .Q(div_remainder[7]),
        .R(SR));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 \div_remainder_reg[7]_i_2 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\div_remainder_reg[7]_i_2_n_0 ,\div_remainder_reg[7]_i_2_n_1 ,\div_remainder_reg[7]_i_2_n_2 ,\div_remainder_reg[7]_i_2_n_3 ,\div_remainder_reg[7]_i_2_n_4 ,\div_remainder_reg[7]_i_2_n_5 ,\div_remainder_reg[7]_i_2_n_6 ,\div_remainder_reg[7]_i_2_n_7 }),
        .DI(sum[7:0]),
        .O(division_numerator[7:0]),
        .S({\div_remainder[7]_i_3_n_0 ,\div_remainder[7]_i_4_n_0 ,\div_remainder[7]_i_5_n_0 ,\div_remainder[7]_i_6_n_0 ,\div_remainder[7]_i_7_n_0 ,\div_remainder[7]_i_8_n_0 ,\div_remainder[7]_i_9_n_0 ,\div_remainder[7]_i_10_n_0 }));
  FDRE \div_remainder_reg[8] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[8]),
        .Q(div_remainder[8]),
        .R(SR));
  FDRE \div_remainder_reg[9] 
       (.C(aclk),
        .CE(\div_remainder[28]_i_1_n_0 ),
        .D(p_2_in[9]),
        .Q(div_remainder[9]),
        .R(SR));
  LUT2 #(
    .INIT(4'hE)) 
    \div_trial[17]_i_1 
       (.I0(\div_trial_reg_n_0_[18] ),
        .I1(start_division),
        .O(\div_trial[17]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair23" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \div_trial[20]_i_1 
       (.I0(\div_trial_reg_n_0_[21] ),
        .I1(start_division),
        .O(\div_trial[20]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'hB)) 
    \div_trial[21]_i_1 
       (.I0(start_division),
        .I1(aresetn),
        .O(\div_trial[21]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'hAAA8)) 
    \div_trial[21]_i_2 
       (.I0(div_busy_reg_n_0),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .I3(div_bit[2]),
        .O(\div_trial[21]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair23" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \div_trial[22]_i_1 
       (.I0(\div_trial_reg_n_0_[23] ),
        .I1(start_division),
        .O(\div_trial[22]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair22" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \div_trial[23]_i_1 
       (.I0(\div_trial_reg_n_0_[24] ),
        .I1(start_division),
        .O(\div_trial[23]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair22" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \div_trial[24]_i_1 
       (.I0(\div_trial_reg_n_0_[25] ),
        .I1(start_division),
        .O(\div_trial[24]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair21" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \div_trial[25]_i_1 
       (.I0(\div_trial_reg_n_0_[26] ),
        .I1(start_division),
        .O(\div_trial[25]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair21" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \div_trial[26]_i_1 
       (.I0(\div_trial_reg_n_0_[27] ),
        .I1(start_division),
        .O(\div_trial[26]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h00000000FFFF8880)) 
    \div_trial[27]_i_1 
       (.I0(valid_pipe),
        .I1(user_pipe),
        .I2(\div_trial[27]_i_2_n_0 ),
        .I3(\div_trial[27]_i_3_n_0 ),
        .I4(p_0_in),
        .I5(div_busy_reg_n_0),
        .O(start_division));
  LUT5 #(
    .INIT(32'hFFFFFFFE)) 
    \div_trial[27]_i_2 
       (.I0(\count_reg_n_0_[19] ),
        .I1(\count_reg_n_0_[17] ),
        .I2(\count_reg_n_0_[16] ),
        .I3(\count_reg_n_0_[20] ),
        .I4(\count_reg_n_0_[18] ),
        .O(\div_trial[27]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFFFFFE)) 
    \div_trial[27]_i_3 
       (.I0(\div_trial[27]_i_4_n_0 ),
        .I1(\count_reg_n_0_[14] ),
        .I2(\count_reg_n_0_[15] ),
        .I3(\count_reg_n_0_[12] ),
        .I4(\count_reg_n_0_[13] ),
        .I5(\div_trial[27]_i_5_n_0 ),
        .O(\div_trial[27]_i_3_n_0 ));
  LUT4 #(
    .INIT(16'hFFFE)) 
    \div_trial[27]_i_4 
       (.I0(\count_reg_n_0_[10] ),
        .I1(\count_reg_n_0_[11] ),
        .I2(\count_reg_n_0_[8] ),
        .I3(\count_reg_n_0_[9] ),
        .O(\div_trial[27]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'hFFFFFFFE)) 
    \div_trial[27]_i_5 
       (.I0(\count_reg_n_0_[5] ),
        .I1(\count_reg_n_0_[4] ),
        .I2(\count_reg_n_0_[7] ),
        .I3(\count_reg_n_0_[6] ),
        .I4(\div_trial[27]_i_6_n_0 ),
        .O(\div_trial[27]_i_5_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT4 #(
    .INIT(16'hFFFE)) 
    \div_trial[27]_i_6 
       (.I0(\count_reg_n_0_[2] ),
        .I1(\count_reg_n_0_[3] ),
        .I2(\count_reg_n_0_[0] ),
        .I3(\count_reg_n_0_[1] ),
        .O(\div_trial[27]_i_6_n_0 ));
  FDRE \div_trial_reg[0] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[1] ),
        .Q(\div_trial_reg_n_0_[0] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[10] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[11] ),
        .Q(\div_trial_reg_n_0_[10] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[11] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[12] ),
        .Q(\div_trial_reg_n_0_[11] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[12] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[13] ),
        .Q(\div_trial_reg_n_0_[12] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[13] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[14] ),
        .Q(\div_trial_reg_n_0_[13] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[14] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[15] ),
        .Q(\div_trial_reg_n_0_[14] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[15] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[16] ),
        .Q(\div_trial_reg_n_0_[15] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[16] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[17] ),
        .Q(\div_trial_reg_n_0_[16] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[17] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_trial[17]_i_1_n_0 ),
        .Q(\div_trial_reg_n_0_[17] ),
        .R(SR));
  FDRE \div_trial_reg[18] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[19] ),
        .Q(\div_trial_reg_n_0_[18] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[19] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[20] ),
        .Q(\div_trial_reg_n_0_[19] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[1] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[2] ),
        .Q(\div_trial_reg_n_0_[1] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[20] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_trial[20]_i_1_n_0 ),
        .Q(\div_trial_reg_n_0_[20] ),
        .R(SR));
  FDRE \div_trial_reg[21] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[22] ),
        .Q(\div_trial_reg_n_0_[21] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[22] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_trial[22]_i_1_n_0 ),
        .Q(\div_trial_reg_n_0_[22] ),
        .R(SR));
  FDRE \div_trial_reg[23] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_trial[23]_i_1_n_0 ),
        .Q(\div_trial_reg_n_0_[23] ),
        .R(SR));
  FDRE \div_trial_reg[24] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_trial[24]_i_1_n_0 ),
        .Q(\div_trial_reg_n_0_[24] ),
        .R(SR));
  FDRE \div_trial_reg[25] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_trial[25]_i_1_n_0 ),
        .Q(\div_trial_reg_n_0_[25] ),
        .R(SR));
  FDRE \div_trial_reg[26] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(\div_trial[26]_i_1_n_0 ),
        .Q(\div_trial_reg_n_0_[26] ),
        .R(SR));
  FDRE \div_trial_reg[27] 
       (.C(aclk),
        .CE(\div_bit[2]_i_1_n_0 ),
        .D(start_division),
        .Q(\div_trial_reg_n_0_[27] ),
        .R(SR));
  FDRE \div_trial_reg[2] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[3] ),
        .Q(\div_trial_reg_n_0_[2] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[3] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[4] ),
        .Q(\div_trial_reg_n_0_[3] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[4] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[5] ),
        .Q(\div_trial_reg_n_0_[4] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[5] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[6] ),
        .Q(\div_trial_reg_n_0_[5] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[6] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[7] ),
        .Q(\div_trial_reg_n_0_[6] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[7] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[8] ),
        .Q(\div_trial_reg_n_0_[7] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[8] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[9] ),
        .Q(\div_trial_reg_n_0_[8] ),
        .R(\div_trial[21]_i_1_n_0 ));
  FDRE \div_trial_reg[9] 
       (.C(aclk),
        .CE(\div_trial[21]_i_2_n_0 ),
        .D(\div_trial_reg_n_0_[10] ),
        .Q(\div_trial_reg_n_0_[9] ),
        .R(\div_trial[21]_i_1_n_0 ));
  LUT1 #(
    .INIT(2'h1)) 
    \frame_mean[7]_i_1 
       (.I0(aresetn),
        .O(SR));
  LUT5 #(
    .INIT(32'h00000100)) 
    \frame_mean[7]_i_2 
       (.I0(div_bit[2]),
        .I1(div_bit[0]),
        .I2(div_bit[1]),
        .I3(div_busy_reg_n_0),
        .I4(start_division),
        .O(\frame_mean[7]_i_2_n_0 ));
  FDRE \frame_mean_reg[0] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_take),
        .Q(status[0]),
        .R(SR));
  FDRE \frame_mean_reg[1] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_quotient[1]),
        .Q(status[1]),
        .R(SR));
  FDRE \frame_mean_reg[2] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_quotient[2]),
        .Q(status[2]),
        .R(SR));
  FDRE \frame_mean_reg[3] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_quotient[3]),
        .Q(status[3]),
        .R(SR));
  FDRE \frame_mean_reg[4] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_quotient[4]),
        .Q(status[4]),
        .R(SR));
  FDRE \frame_mean_reg[5] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_quotient[5]),
        .Q(status[5]),
        .R(SR));
  FDRE \frame_mean_reg[6] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_quotient[6]),
        .Q(status[6]),
        .R(SR));
  FDRE \frame_mean_reg[7] 
       (.C(aclk),
        .CE(\frame_mean[7]_i_2_n_0 ),
        .D(div_quotient[7]),
        .Q(status[7]),
        .R(SR));
  LUT4 #(
    .INIT(16'h0002)) 
    frame_valid_i_1
       (.I0(div_busy_reg_n_0),
        .I1(div_bit[1]),
        .I2(div_bit[0]),
        .I3(div_bit[2]),
        .O(frame_valid_i_1_n_0));
  FDRE frame_valid_reg
       (.C(aclk),
        .CE(1'b1),
        .D(frame_valid_i_1_n_0),
        .Q(frame_valid),
        .R(\div_trial[21]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFA800FF000000)) 
    i___1_carry__0_i_1
       (.I0(s_axis_tdata[13]),
        .I1(i___1_carry_i_12_n_0),
        .I2(s_axis_tdata[12]),
        .I3(s_axis_tdata[11]),
        .I4(s_axis_tdata[14]),
        .I5(s_axis_tdata[15]),
        .O(i___1_carry__0_i_1_n_0));
  LUT3 #(
    .INIT(8'h78)) 
    i___1_carry__0_i_2
       (.I0(s_axis_tdata[15]),
        .I1(s_axis_tdata[12]),
        .I2(s_axis_tdata[13]),
        .O(i___1_carry__0_i_2_n_0));
  LUT6 #(
    .INIT(64'hEEAA777715558888)) 
    i___1_carry__0_i_3
       (.I0(s_axis_tdata[14]),
        .I1(s_axis_tdata[11]),
        .I2(i___1_carry_i_12_n_0),
        .I3(s_axis_tdata[13]),
        .I4(s_axis_tdata[15]),
        .I5(s_axis_tdata[12]),
        .O(i___1_carry__0_i_3_n_0));
  LUT6 #(
    .INIT(64'hBAEEAAEFA2002208)) 
    i___1_carry_i_1
       (.I0(s_axis_tdata[13]),
        .I1(s_axis_tdata[15]),
        .I2(i___1_carry_i_12_n_0),
        .I3(s_axis_tdata[14]),
        .I4(s_axis_tdata[12]),
        .I5(s_axis_tdata[10]),
        .O(i___1_carry_i_1_n_0));
  LUT4 #(
    .INIT(16'h69B4)) 
    i___1_carry_i_10
       (.I0(s_axis_tdata[9]),
        .I1(s_axis_tdata[10]),
        .I2(s_axis_tdata[11]),
        .I3(s_axis_tdata[8]),
        .O(i___1_carry_i_10_n_0));
  LUT3 #(
    .INIT(8'hC6)) 
    i___1_carry_i_11
       (.I0(s_axis_tdata[9]),
        .I1(s_axis_tdata[10]),
        .I2(s_axis_tdata[8]),
        .O(i___1_carry_i_11_n_0));
  LUT6 #(
    .INIT(64'h0000F800FFC0FFFF)) 
    i___1_carry_i_12
       (.I0(s_axis_tdata[8]),
        .I1(s_axis_tdata[9]),
        .I2(s_axis_tdata[10]),
        .I3(s_axis_tdata[11]),
        .I4(s_axis_tdata[12]),
        .I5(s_axis_tdata[13]),
        .O(i___1_carry_i_12_n_0));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT5 #(
    .INIT(32'hCC88CC80)) 
    i___1_carry_i_13
       (.I0(s_axis_tdata[13]),
        .I1(s_axis_tdata[15]),
        .I2(i___1_carry_i_12_n_0),
        .I3(s_axis_tdata[14]),
        .I4(s_axis_tdata[12]),
        .O(i___1_carry_i_13_n_0));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT5 #(
    .INIT(32'h7E33CC7E)) 
    i___1_carry_i_14
       (.I0(s_axis_tdata[12]),
        .I1(s_axis_tdata[14]),
        .I2(i___1_carry_i_12_n_0),
        .I3(s_axis_tdata[15]),
        .I4(s_axis_tdata[13]),
        .O(i___1_carry_i_14_n_0));
  LUT5 #(
    .INIT(32'h96996696)) 
    i___1_carry_i_15
       (.I0(s_axis_tdata[15]),
        .I1(s_axis_tdata[13]),
        .I2(s_axis_tdata[12]),
        .I3(s_axis_tdata[14]),
        .I4(i___1_carry_i_12_n_0),
        .O(i___1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'hFFFFD22D4BB40000)) 
    i___1_carry_i_2
       (.I0(i___1_carry_i_12_n_0),
        .I1(s_axis_tdata[14]),
        .I2(s_axis_tdata[13]),
        .I3(s_axis_tdata[15]),
        .I4(s_axis_tdata[12]),
        .I5(s_axis_tdata[9]),
        .O(i___1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h6969699696696969)) 
    i___1_carry_i_3
       (.I0(s_axis_tdata[9]),
        .I1(s_axis_tdata[15]),
        .I2(s_axis_tdata[13]),
        .I3(s_axis_tdata[12]),
        .I4(s_axis_tdata[14]),
        .I5(i___1_carry_i_12_n_0),
        .O(i___1_carry_i_3_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    i___1_carry_i_4
       (.I0(i___1_carry_i_1_n_0),
        .I1(s_axis_tdata[11]),
        .I2(i___1_carry_i_13_n_0),
        .I3(s_axis_tdata[14]),
        .O(i___1_carry_i_4_n_0));
  LUT4 #(
    .INIT(16'h9669)) 
    i___1_carry_i_5
       (.I0(i___1_carry_i_2_n_0),
        .I1(s_axis_tdata[13]),
        .I2(i___1_carry_i_14_n_0),
        .I3(s_axis_tdata[10]),
        .O(i___1_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h6696699996669969)) 
    i___1_carry_i_6
       (.I0(i___1_carry_i_15_n_0),
        .I1(s_axis_tdata[9]),
        .I2(s_axis_tdata[11]),
        .I3(s_axis_tdata[14]),
        .I4(s_axis_tdata[12]),
        .I5(i___1_carry_i_12_n_0),
        .O(i___1_carry_i_6_n_0));
  LUT5 #(
    .INIT(32'h69969669)) 
    i___1_carry_i_7
       (.I0(s_axis_tdata[11]),
        .I1(s_axis_tdata[14]),
        .I2(s_axis_tdata[12]),
        .I3(i___1_carry_i_12_n_0),
        .I4(s_axis_tdata[8]),
        .O(i___1_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h03F0FC0FF07F0F80)) 
    i___1_carry_i_8
       (.I0(s_axis_tdata[8]),
        .I1(s_axis_tdata[9]),
        .I2(s_axis_tdata[11]),
        .I3(s_axis_tdata[12]),
        .I4(s_axis_tdata[13]),
        .I5(s_axis_tdata[10]),
        .O(i___1_carry_i_8_n_0));
  LUT5 #(
    .INIT(32'h1CE3CF30)) 
    i___1_carry_i_9
       (.I0(s_axis_tdata[8]),
        .I1(s_axis_tdata[10]),
        .I2(s_axis_tdata[11]),
        .I3(s_axis_tdata[12]),
        .I4(s_axis_tdata[9]),
        .O(i___1_carry_i_9_n_0));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_2 
       (.I0(sum[15]),
        .I1(user_pipe),
        .O(\sum[15]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_3 
       (.I0(sum[14]),
        .I1(user_pipe),
        .O(\sum[15]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_4 
       (.I0(sum[13]),
        .I1(user_pipe),
        .O(\sum[15]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_5 
       (.I0(sum[12]),
        .I1(user_pipe),
        .O(\sum[15]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_6 
       (.I0(sum[11]),
        .I1(user_pipe),
        .O(\sum[15]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_7 
       (.I0(sum[10]),
        .I1(user_pipe),
        .O(\sum[15]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_8 
       (.I0(sum[9]),
        .I1(user_pipe),
        .O(\sum[15]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[15]_i_9 
       (.I0(sum[8]),
        .I1(user_pipe),
        .O(\sum[15]_i_9_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_2 
       (.I0(sum[23]),
        .I1(user_pipe),
        .O(\sum[23]_i_2_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_3 
       (.I0(sum[22]),
        .I1(user_pipe),
        .O(\sum[23]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_4 
       (.I0(sum[21]),
        .I1(user_pipe),
        .O(\sum[23]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_5 
       (.I0(sum[20]),
        .I1(user_pipe),
        .O(\sum[23]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_6 
       (.I0(sum[19]),
        .I1(user_pipe),
        .O(\sum[23]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_7 
       (.I0(sum[18]),
        .I1(user_pipe),
        .O(\sum[23]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_8 
       (.I0(sum[17]),
        .I1(user_pipe),
        .O(\sum[23]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[23]_i_9 
       (.I0(sum[16]),
        .I1(user_pipe),
        .O(\sum[23]_i_9_n_0 ));
  LUT4 #(
    .INIT(16'hE0FF)) 
    \sum[28]_i_1 
       (.I0(user_pipe),
        .I1(p_0_in),
        .I2(valid_pipe),
        .I3(aresetn),
        .O(\sum[28]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[28]_i_3 
       (.I0(sum[28]),
        .I1(user_pipe),
        .O(\sum[28]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[28]_i_4 
       (.I0(sum[27]),
        .I1(user_pipe),
        .O(\sum[28]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[28]_i_5 
       (.I0(sum[26]),
        .I1(user_pipe),
        .O(\sum[28]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[28]_i_6 
       (.I0(sum[25]),
        .I1(user_pipe),
        .O(\sum[28]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[28]_i_7 
       (.I0(sum[24]),
        .I1(user_pipe),
        .O(\sum[28]_i_7_n_0 ));
  LUT4 #(
    .INIT(16'h20FF)) 
    \sum[7]_i_1 
       (.I0(p_0_in),
        .I1(user_pipe),
        .I2(valid_pipe),
        .I3(aresetn),
        .O(\sum[7]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_10 
       (.I0(y_pipe[0]),
        .I1(user_pipe),
        .O(\sum[7]_i_10_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_11 
       (.I0(sum[7]),
        .I1(user_pipe),
        .I2(y_pipe[7]),
        .O(\sum[7]_i_11_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_12 
       (.I0(sum[6]),
        .I1(user_pipe),
        .I2(y_pipe[6]),
        .O(\sum[7]_i_12_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_13 
       (.I0(sum[5]),
        .I1(user_pipe),
        .I2(y_pipe[5]),
        .O(\sum[7]_i_13_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_14 
       (.I0(sum[4]),
        .I1(user_pipe),
        .I2(y_pipe[4]),
        .O(\sum[7]_i_14_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_15 
       (.I0(sum[3]),
        .I1(user_pipe),
        .I2(y_pipe[3]),
        .O(\sum[7]_i_15_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_16 
       (.I0(sum[2]),
        .I1(user_pipe),
        .I2(y_pipe[2]),
        .O(\sum[7]_i_16_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_17 
       (.I0(sum[1]),
        .I1(user_pipe),
        .I2(y_pipe[1]),
        .O(\sum[7]_i_17_n_0 ));
  LUT3 #(
    .INIT(8'hD2)) 
    \sum[7]_i_18 
       (.I0(sum[0]),
        .I1(user_pipe),
        .I2(y_pipe[0]),
        .O(\sum[7]_i_18_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_3 
       (.I0(y_pipe[7]),
        .I1(user_pipe),
        .O(\sum[7]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_4 
       (.I0(y_pipe[6]),
        .I1(user_pipe),
        .O(\sum[7]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_5 
       (.I0(y_pipe[5]),
        .I1(user_pipe),
        .O(\sum[7]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_6 
       (.I0(y_pipe[4]),
        .I1(user_pipe),
        .O(\sum[7]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_7 
       (.I0(y_pipe[3]),
        .I1(user_pipe),
        .O(\sum[7]_i_7_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_8 
       (.I0(y_pipe[2]),
        .I1(user_pipe),
        .O(\sum[7]_i_8_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \sum[7]_i_9 
       (.I0(y_pipe[1]),
        .I1(user_pipe),
        .O(\sum[7]_i_9_n_0 ));
  FDRE \sum_reg[0] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_15 ),
        .Q(sum[0]),
        .R(\sum[7]_i_1_n_0 ));
  FDRE \sum_reg[10] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_13 ),
        .Q(sum[10]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[11] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_12 ),
        .Q(sum[11]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[12] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_11 ),
        .Q(sum[12]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[13] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_10 ),
        .Q(sum[13]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[14] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_9 ),
        .Q(sum[14]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[15] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_8 ),
        .Q(sum[15]),
        .R(\sum[28]_i_1_n_0 ));
  CARRY8 \sum_reg[15]_i_1 
       (.CI(\sum_reg[7]_i_2_n_0 ),
        .CI_TOP(1'b0),
        .CO({\sum_reg[15]_i_1_n_0 ,\sum_reg[15]_i_1_n_1 ,\sum_reg[15]_i_1_n_2 ,\sum_reg[15]_i_1_n_3 ,\sum_reg[15]_i_1_n_4 ,\sum_reg[15]_i_1_n_5 ,\sum_reg[15]_i_1_n_6 ,\sum_reg[15]_i_1_n_7 }),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O({\sum_reg[15]_i_1_n_8 ,\sum_reg[15]_i_1_n_9 ,\sum_reg[15]_i_1_n_10 ,\sum_reg[15]_i_1_n_11 ,\sum_reg[15]_i_1_n_12 ,\sum_reg[15]_i_1_n_13 ,\sum_reg[15]_i_1_n_14 ,\sum_reg[15]_i_1_n_15 }),
        .S({\sum[15]_i_2_n_0 ,\sum[15]_i_3_n_0 ,\sum[15]_i_4_n_0 ,\sum[15]_i_5_n_0 ,\sum[15]_i_6_n_0 ,\sum[15]_i_7_n_0 ,\sum[15]_i_8_n_0 ,\sum[15]_i_9_n_0 }));
  FDRE \sum_reg[16] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_15 ),
        .Q(sum[16]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[17] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_14 ),
        .Q(sum[17]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[18] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_13 ),
        .Q(sum[18]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[19] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_12 ),
        .Q(sum[19]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[1] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_14 ),
        .Q(sum[1]),
        .R(\sum[7]_i_1_n_0 ));
  FDRE \sum_reg[20] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_11 ),
        .Q(sum[20]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[21] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_10 ),
        .Q(sum[21]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[22] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_9 ),
        .Q(sum[22]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[23] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[23]_i_1_n_8 ),
        .Q(sum[23]),
        .R(\sum[28]_i_1_n_0 ));
  CARRY8 \sum_reg[23]_i_1 
       (.CI(\sum_reg[15]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\sum_reg[23]_i_1_n_0 ,\sum_reg[23]_i_1_n_1 ,\sum_reg[23]_i_1_n_2 ,\sum_reg[23]_i_1_n_3 ,\sum_reg[23]_i_1_n_4 ,\sum_reg[23]_i_1_n_5 ,\sum_reg[23]_i_1_n_6 ,\sum_reg[23]_i_1_n_7 }),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O({\sum_reg[23]_i_1_n_8 ,\sum_reg[23]_i_1_n_9 ,\sum_reg[23]_i_1_n_10 ,\sum_reg[23]_i_1_n_11 ,\sum_reg[23]_i_1_n_12 ,\sum_reg[23]_i_1_n_13 ,\sum_reg[23]_i_1_n_14 ,\sum_reg[23]_i_1_n_15 }),
        .S({\sum[23]_i_2_n_0 ,\sum[23]_i_3_n_0 ,\sum[23]_i_4_n_0 ,\sum[23]_i_5_n_0 ,\sum[23]_i_6_n_0 ,\sum[23]_i_7_n_0 ,\sum[23]_i_8_n_0 ,\sum[23]_i_9_n_0 }));
  FDRE \sum_reg[24] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[28]_i_2_n_15 ),
        .Q(sum[24]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[25] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[28]_i_2_n_14 ),
        .Q(sum[25]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[26] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[28]_i_2_n_13 ),
        .Q(sum[26]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[27] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[28]_i_2_n_12 ),
        .Q(sum[27]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[28] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[28]_i_2_n_11 ),
        .Q(sum[28]),
        .R(\sum[28]_i_1_n_0 ));
  CARRY8 \sum_reg[28]_i_2 
       (.CI(\sum_reg[23]_i_1_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_sum_reg[28]_i_2_CO_UNCONNECTED [7:4],\sum_reg[28]_i_2_n_4 ,\sum_reg[28]_i_2_n_5 ,\sum_reg[28]_i_2_n_6 ,\sum_reg[28]_i_2_n_7 }),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .O({\NLW_sum_reg[28]_i_2_O_UNCONNECTED [7:5],\sum_reg[28]_i_2_n_11 ,\sum_reg[28]_i_2_n_12 ,\sum_reg[28]_i_2_n_13 ,\sum_reg[28]_i_2_n_14 ,\sum_reg[28]_i_2_n_15 }),
        .S({1'b0,1'b0,1'b0,\sum[28]_i_3_n_0 ,\sum[28]_i_4_n_0 ,\sum[28]_i_5_n_0 ,\sum[28]_i_6_n_0 ,\sum[28]_i_7_n_0 }));
  FDRE \sum_reg[2] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_13 ),
        .Q(sum[2]),
        .R(\sum[7]_i_1_n_0 ));
  FDRE \sum_reg[3] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_12 ),
        .Q(sum[3]),
        .R(\sum[7]_i_1_n_0 ));
  FDRE \sum_reg[4] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_11 ),
        .Q(sum[4]),
        .R(\sum[7]_i_1_n_0 ));
  FDRE \sum_reg[5] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_10 ),
        .Q(sum[5]),
        .R(\sum[7]_i_1_n_0 ));
  FDRE \sum_reg[6] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_9 ),
        .Q(sum[6]),
        .R(\sum[7]_i_1_n_0 ));
  FDRE \sum_reg[7] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[7]_i_2_n_8 ),
        .Q(sum[7]),
        .R(\sum[7]_i_1_n_0 ));
  CARRY8 \sum_reg[7]_i_2 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\sum_reg[7]_i_2_n_0 ,\sum_reg[7]_i_2_n_1 ,\sum_reg[7]_i_2_n_2 ,\sum_reg[7]_i_2_n_3 ,\sum_reg[7]_i_2_n_4 ,\sum_reg[7]_i_2_n_5 ,\sum_reg[7]_i_2_n_6 ,\sum_reg[7]_i_2_n_7 }),
        .DI({\sum[7]_i_3_n_0 ,\sum[7]_i_4_n_0 ,\sum[7]_i_5_n_0 ,\sum[7]_i_6_n_0 ,\sum[7]_i_7_n_0 ,\sum[7]_i_8_n_0 ,\sum[7]_i_9_n_0 ,\sum[7]_i_10_n_0 }),
        .O({\sum_reg[7]_i_2_n_8 ,\sum_reg[7]_i_2_n_9 ,\sum_reg[7]_i_2_n_10 ,\sum_reg[7]_i_2_n_11 ,\sum_reg[7]_i_2_n_12 ,\sum_reg[7]_i_2_n_13 ,\sum_reg[7]_i_2_n_14 ,\sum_reg[7]_i_2_n_15 }),
        .S({\sum[7]_i_11_n_0 ,\sum[7]_i_12_n_0 ,\sum[7]_i_13_n_0 ,\sum[7]_i_14_n_0 ,\sum[7]_i_15_n_0 ,\sum[7]_i_16_n_0 ,\sum[7]_i_17_n_0 ,\sum[7]_i_18_n_0 }));
  FDRE \sum_reg[8] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_15 ),
        .Q(sum[8]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE \sum_reg[9] 
       (.C(aclk),
        .CE(valid_pipe),
        .D(\sum_reg[15]_i_1_n_14 ),
        .Q(sum[9]),
        .R(\sum[28]_i_1_n_0 ));
  FDRE user_pipe_reg
       (.C(aclk),
        .CE(1'b1),
        .D(s_axis_tuser),
        .Q(user_pipe),
        .R(SR));
  LUT2 #(
    .INIT(4'h8)) 
    valid_pipe_i_1
       (.I0(s_axis_tvalid),
        .I1(s_axis_tready),
        .O(valid_pipe_i_1_n_0));
  FDRE valid_pipe_reg
       (.C(aclk),
        .CE(1'b1),
        .D(valid_pipe_i_1_n_0),
        .Q(valid_pipe),
        .R(SR));
  FDRE \y_pipe_reg[0] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[0]),
        .Q(y_pipe[0]),
        .R(SR));
  FDRE \y_pipe_reg[1] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[1]),
        .Q(y_pipe[1]),
        .R(SR));
  FDRE \y_pipe_reg[2] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[2]),
        .Q(y_pipe[2]),
        .R(SR));
  FDRE \y_pipe_reg[3] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[3]),
        .Q(y_pipe[3]),
        .R(SR));
  FDRE \y_pipe_reg[4] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[4]),
        .Q(y_pipe[4]),
        .R(SR));
  FDRE \y_pipe_reg[5] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[5]),
        .Q(y_pipe[5]),
        .R(SR));
  FDRE \y_pipe_reg[6] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[6]),
        .Q(y_pipe[6]),
        .R(SR));
  FDRE \y_pipe_reg[7] 
       (.C(aclk),
        .CE(valid_pipe_i_1_n_0),
        .D(y[7]),
        .Q(y_pipe[7]),
        .R(SR));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 y_sum0__1_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({y_sum0__1_carry_n_0,y_sum0__1_carry_n_1,y_sum0__1_carry_n_2,y_sum0__1_carry_n_3,y_sum0__1_carry_n_4,y_sum0__1_carry_n_5,y_sum0__1_carry_n_6,y_sum0__1_carry_n_7}),
        .DI({y_sum0__1_carry_i_1_n_0,y_sum0__1_carry_i_2_n_0,y_sum0__1_carry_i_3_n_0,y_sum0__1_carry_i_4_n_0,y_sum0__1_carry_i_5_n_0,y_sum0__1_carry_i_6_n_0,y_sum0__1_carry_i_7_n_0,1'b0}),
        .O(y_sum0[10:3]),
        .S({y_sum0__1_carry_i_8_n_0,y_sum0__1_carry_i_9_n_0,y_sum0__1_carry_i_10_n_0,y_sum0__1_carry_i_11_n_0,y_sum0__1_carry_i_12_n_0,y_sum0__1_carry_i_13_n_0,y_sum0__1_carry_i_14_n_0,y_sum0__1_carry_i_15_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 y_sum0__1_carry__0
       (.CI(y_sum0__1_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_y_sum0__1_carry__0_CO_UNCONNECTED[7:1],y_sum0__1_carry__0_n_7}),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,y_sum0__1_carry__0_i_1_n_0}),
        .O({NLW_y_sum0__1_carry__0_O_UNCONNECTED[7:2],y_sum0[12:11]}),
        .S({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,y_sum0__1_carry__0_i_2_n_0,y_sum0__1_carry__0_i_3_n_0}));
  LUT1 #(
    .INIT(2'h1)) 
    y_sum0__1_carry__0_i_1
       (.I0(s_axis_tdata[6]),
        .O(y_sum0__1_carry__0_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    y_sum0__1_carry__0_i_2
       (.I0(s_axis_tdata[6]),
        .I1(s_axis_tdata[7]),
        .O(y_sum0__1_carry__0_i_2_n_0));
  LUT3 #(
    .INIT(8'hCB)) 
    y_sum0__1_carry__0_i_3
       (.I0(s_axis_tdata[7]),
        .I1(s_axis_tdata[5]),
        .I2(s_axis_tdata[6]),
        .O(y_sum0__1_carry__0_i_3_n_0));
  LUT4 #(
    .INIT(16'h5C54)) 
    y_sum0__1_carry_i_1
       (.I0(s_axis_tdata[6]),
        .I1(s_axis_tdata[4]),
        .I2(s_axis_tdata[7]),
        .I3(s_axis_tdata[5]),
        .O(y_sum0__1_carry_i_1_n_0));
  LUT4 #(
    .INIT(16'h9669)) 
    y_sum0__1_carry_i_10
       (.I0(y_sum0__1_carry_i_3_n_0),
        .I1(y_sum0__1_carry_i_17_n_0),
        .I2(s_axis_tdata[3]),
        .I3(s_axis_tdata[5]),
        .O(y_sum0__1_carry_i_10_n_0));
  LUT4 #(
    .INIT(16'h9669)) 
    y_sum0__1_carry_i_11
       (.I0(y_sum0__1_carry_i_4_n_0),
        .I1(y_sum0__1_carry_i_18_n_0),
        .I2(s_axis_tdata[2]),
        .I3(s_axis_tdata[4]),
        .O(y_sum0__1_carry_i_11_n_0));
  LUT6 #(
    .INIT(64'h6996966996696996)) 
    y_sum0__1_carry_i_12
       (.I0(y_sum0__1_carry_i_5_n_0),
        .I1(s_axis_tdata[6]),
        .I2(s_axis_tdata[4]),
        .I3(y_sum0__1_carry_i_16_n_0),
        .I4(s_axis_tdata[1]),
        .I5(s_axis_tdata[3]),
        .O(y_sum0__1_carry_i_12_n_0));
  LUT6 #(
    .INIT(64'h5A96A6A59A96A569)) 
    y_sum0__1_carry_i_13
       (.I0(s_axis_tdata[5]),
        .I1(s_axis_tdata[4]),
        .I2(s_axis_tdata[0]),
        .I3(s_axis_tdata[2]),
        .I4(s_axis_tdata[3]),
        .I5(s_axis_tdata[1]),
        .O(y_sum0__1_carry_i_13_n_0));
  LUT6 #(
    .INIT(64'h6699696696996699)) 
    y_sum0__1_carry_i_14
       (.I0(y_sum0__1_carry_i_7_n_0),
        .I1(s_axis_tdata[4]),
        .I2(s_axis_tdata[0]),
        .I3(s_axis_tdata[2]),
        .I4(s_axis_tdata[3]),
        .I5(s_axis_tdata[1]),
        .O(y_sum0__1_carry_i_14_n_0));
  (* HLUTNM = "lutpair0" *) 
  LUT4 #(
    .INIT(16'h693C)) 
    y_sum0__1_carry_i_15
       (.I0(s_axis_tdata[2]),
        .I1(s_axis_tdata[1]),
        .I2(s_axis_tdata[3]),
        .I3(s_axis_tdata[0]),
        .O(y_sum0__1_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'h1517175715571777)) 
    y_sum0__1_carry_i_16
       (.I0(s_axis_tdata[3]),
        .I1(s_axis_tdata[5]),
        .I2(s_axis_tdata[2]),
        .I3(s_axis_tdata[4]),
        .I4(s_axis_tdata[1]),
        .I5(s_axis_tdata[0]),
        .O(y_sum0__1_carry_i_16_n_0));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT5 #(
    .INIT(32'h178811E8)) 
    y_sum0__1_carry_i_17
       (.I0(s_axis_tdata[5]),
        .I1(s_axis_tdata[7]),
        .I2(s_axis_tdata[4]),
        .I3(s_axis_tdata[6]),
        .I4(y_sum0__1_carry_i_16_n_0),
        .O(y_sum0__1_carry_i_17_n_0));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT5 #(
    .INIT(32'h99696966)) 
    y_sum0__1_carry_i_18
       (.I0(s_axis_tdata[7]),
        .I1(s_axis_tdata[5]),
        .I2(y_sum0__1_carry_i_16_n_0),
        .I3(s_axis_tdata[6]),
        .I4(s_axis_tdata[4]),
        .O(y_sum0__1_carry_i_18_n_0));
  LUT6 #(
    .INIT(64'h57DD55FD15001140)) 
    y_sum0__1_carry_i_2
       (.I0(s_axis_tdata[5]),
        .I1(s_axis_tdata[7]),
        .I2(s_axis_tdata[4]),
        .I3(s_axis_tdata[6]),
        .I4(y_sum0__1_carry_i_16_n_0),
        .I5(s_axis_tdata[3]),
        .O(y_sum0__1_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9969FFFF00006966)) 
    y_sum0__1_carry_i_3
       (.I0(s_axis_tdata[7]),
        .I1(s_axis_tdata[5]),
        .I2(y_sum0__1_carry_i_16_n_0),
        .I3(s_axis_tdata[6]),
        .I4(s_axis_tdata[4]),
        .I5(s_axis_tdata[2]),
        .O(y_sum0__1_carry_i_3_n_0));
  LUT5 #(
    .INIT(32'h69FF0069)) 
    y_sum0__1_carry_i_4
       (.I0(s_axis_tdata[6]),
        .I1(s_axis_tdata[4]),
        .I2(y_sum0__1_carry_i_16_n_0),
        .I3(s_axis_tdata[3]),
        .I4(s_axis_tdata[1]),
        .O(y_sum0__1_carry_i_4_n_0));
  LUT6 #(
    .INIT(64'hF1000E00FF8FFF70)) 
    y_sum0__1_carry_i_5
       (.I0(s_axis_tdata[4]),
        .I1(s_axis_tdata[1]),
        .I2(s_axis_tdata[3]),
        .I3(s_axis_tdata[0]),
        .I4(s_axis_tdata[5]),
        .I5(s_axis_tdata[2]),
        .O(y_sum0__1_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h69696A5699696969)) 
    y_sum0__1_carry_i_6
       (.I0(s_axis_tdata[5]),
        .I1(s_axis_tdata[0]),
        .I2(s_axis_tdata[3]),
        .I3(s_axis_tdata[1]),
        .I4(s_axis_tdata[4]),
        .I5(s_axis_tdata[2]),
        .O(y_sum0__1_carry_i_6_n_0));
  (* HLUTNM = "lutpair0" *) 
  LUT4 #(
    .INIT(16'h96FF)) 
    y_sum0__1_carry_i_7
       (.I0(s_axis_tdata[2]),
        .I1(s_axis_tdata[1]),
        .I2(s_axis_tdata[3]),
        .I3(s_axis_tdata[0]),
        .O(y_sum0__1_carry_i_7_n_0));
  LUT5 #(
    .INIT(32'h00F0F7AF)) 
    y_sum0__1_carry_i_8
       (.I0(s_axis_tdata[6]),
        .I1(y_sum0__1_carry_i_16_n_0),
        .I2(s_axis_tdata[4]),
        .I3(s_axis_tdata[7]),
        .I4(s_axis_tdata[5]),
        .O(y_sum0__1_carry_i_8_n_0));
  LUT6 #(
    .INIT(64'h55AAAA95556A6699)) 
    y_sum0__1_carry_i_9
       (.I0(y_sum0__1_carry_i_2_n_0),
        .I1(s_axis_tdata[6]),
        .I2(y_sum0__1_carry_i_16_n_0),
        .I3(s_axis_tdata[4]),
        .I4(s_axis_tdata[7]),
        .I5(s_axis_tdata[5]),
        .O(y_sum0__1_carry_i_9_n_0));
  CARRY8 y_sum1__5_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({y_sum1__5_carry_n_0,y_sum1__5_carry_n_1,y_sum1__5_carry_n_2,y_sum1__5_carry_n_3,y_sum1__5_carry_n_4,y_sum1__5_carry_n_5,y_sum1__5_carry_n_6,y_sum1__5_carry_n_7}),
        .DI({y_sum1__5_carry_i_1_n_0,y_sum1__5_carry_i_2_n_0,y_sum1__5_carry_i_3_n_0,s_axis_tdata[16],s_axis_tdata[18:16],1'b0}),
        .O({y_sum1__5_carry_n_8,y_sum1__5_carry_n_9,y_sum1__5_carry_n_10,y_sum1__5_carry_n_11,y_sum1__5_carry_n_12,y_sum1__5_carry_n_13,y_sum1__5_carry_n_14,y_sum1__5_carry_n_15}),
        .S({y_sum1__5_carry_i_4_n_0,y_sum1__5_carry_i_5_n_0,y_sum1__5_carry_i_6_n_0,y_sum1__5_carry_i_7_n_0,y_sum1__5_carry_i_8_n_0,y_sum1__5_carry_i_9_n_0,y_sum1__5_carry_i_10_n_0,y_sum1__5_carry_i_11_n_0}));
  CARRY8 y_sum1__5_carry__0
       (.CI(y_sum1__5_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_y_sum1__5_carry__0_CO_UNCONNECTED[7:4],y_sum1__5_carry__0_n_4,y_sum1__5_carry__0_n_5,y_sum1__5_carry__0_n_6,y_sum1__5_carry__0_n_7}),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,s_axis_tdata[21],y_sum1__5_carry__0_i_1_n_0}),
        .O({NLW_y_sum1__5_carry__0_O_UNCONNECTED[7:4],y_sum1__5_carry__0_n_12,y_sum1__5_carry__0_n_13,y_sum1__5_carry__0_n_14,y_sum1__5_carry__0_n_15}),
        .S({1'b0,1'b0,1'b0,1'b0,s_axis_tdata[23:22],y_sum1__5_carry__0_i_2_n_0,y_sum1__5_carry__0_i_3_n_0}));
  LUT6 #(
    .INIT(64'hFFFFFF000100A800)) 
    y_sum1__5_carry__0_i_1
       (.I0(s_axis_tdata[21]),
        .I1(s_axis_tdata[20]),
        .I2(y_sum1__5_carry_i_12_n_0),
        .I3(s_axis_tdata[22]),
        .I4(s_axis_tdata[23]),
        .I5(s_axis_tdata[19]),
        .O(y_sum1__5_carry__0_i_1_n_0));
  LUT5 #(
    .INIT(32'h05FFF800)) 
    y_sum1__5_carry__0_i_2
       (.I0(s_axis_tdata[22]),
        .I1(y_sum1__5_carry_i_12_n_0),
        .I2(s_axis_tdata[20]),
        .I3(s_axis_tdata[23]),
        .I4(s_axis_tdata[21]),
        .O(y_sum1__5_carry__0_i_2_n_0));
  LUT6 #(
    .INIT(64'h6699669133C87788)) 
    y_sum1__5_carry__0_i_3
       (.I0(s_axis_tdata[19]),
        .I1(s_axis_tdata[22]),
        .I2(y_sum1__5_carry_i_12_n_0),
        .I3(s_axis_tdata[20]),
        .I4(s_axis_tdata[21]),
        .I5(s_axis_tdata[23]),
        .O(y_sum1__5_carry__0_i_3_n_0));
  LUT6 #(
    .INIT(64'hAAFF0280ABEAAA00)) 
    y_sum1__5_carry_i_1
       (.I0(s_axis_tdata[18]),
        .I1(y_sum1__5_carry_i_12_n_0),
        .I2(s_axis_tdata[20]),
        .I3(s_axis_tdata[22]),
        .I4(s_axis_tdata[21]),
        .I5(s_axis_tdata[23]),
        .O(y_sum1__5_carry_i_1_n_0));
  LUT4 #(
    .INIT(16'h6966)) 
    y_sum1__5_carry_i_10
       (.I0(s_axis_tdata[17]),
        .I1(s_axis_tdata[19]),
        .I2(s_axis_tdata[18]),
        .I3(s_axis_tdata[16]),
        .O(y_sum1__5_carry_i_10_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum1__5_carry_i_11
       (.I0(s_axis_tdata[18]),
        .I1(s_axis_tdata[16]),
        .O(y_sum1__5_carry_i_11_n_0));
  LUT6 #(
    .INIT(64'hEAE8E8A8EAA8E888)) 
    y_sum1__5_carry_i_12
       (.I0(s_axis_tdata[19]),
        .I1(s_axis_tdata[21]),
        .I2(s_axis_tdata[18]),
        .I3(s_axis_tdata[20]),
        .I4(s_axis_tdata[17]),
        .I5(s_axis_tdata[16]),
        .O(y_sum1__5_carry_i_12_n_0));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT5 #(
    .INIT(32'hEEE80000)) 
    y_sum1__5_carry_i_13
       (.I0(s_axis_tdata[23]),
        .I1(s_axis_tdata[21]),
        .I2(s_axis_tdata[20]),
        .I3(y_sum1__5_carry_i_12_n_0),
        .I4(s_axis_tdata[22]),
        .O(y_sum1__5_carry_i_13_n_0));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT5 #(
    .INIT(32'h1E181878)) 
    y_sum1__5_carry_i_14
       (.I0(s_axis_tdata[23]),
        .I1(s_axis_tdata[21]),
        .I2(s_axis_tdata[22]),
        .I3(s_axis_tdata[20]),
        .I4(y_sum1__5_carry_i_12_n_0),
        .O(y_sum1__5_carry_i_14_n_0));
  LUT5 #(
    .INIT(32'h99969666)) 
    y_sum1__5_carry_i_15
       (.I0(s_axis_tdata[23]),
        .I1(s_axis_tdata[21]),
        .I2(s_axis_tdata[22]),
        .I3(s_axis_tdata[20]),
        .I4(y_sum1__5_carry_i_12_n_0),
        .O(y_sum1__5_carry_i_15_n_0));
  LUT6 #(
    .INIT(64'hECDFDFECC80404C8)) 
    y_sum1__5_carry_i_2
       (.I0(y_sum1__5_carry_i_12_n_0),
        .I1(s_axis_tdata[20]),
        .I2(s_axis_tdata[22]),
        .I3(s_axis_tdata[21]),
        .I4(s_axis_tdata[23]),
        .I5(s_axis_tdata[17]),
        .O(y_sum1__5_carry_i_2_n_0));
  LUT6 #(
    .INIT(64'h9696699696699696)) 
    y_sum1__5_carry_i_3
       (.I0(s_axis_tdata[17]),
        .I1(s_axis_tdata[23]),
        .I2(s_axis_tdata[21]),
        .I3(s_axis_tdata[22]),
        .I4(s_axis_tdata[20]),
        .I5(y_sum1__5_carry_i_12_n_0),
        .O(y_sum1__5_carry_i_3_n_0));
  LUT5 #(
    .INIT(32'h96696996)) 
    y_sum1__5_carry_i_4
       (.I0(y_sum1__5_carry_i_1_n_0),
        .I1(s_axis_tdata[22]),
        .I2(s_axis_tdata[23]),
        .I3(y_sum1__5_carry_i_13_n_0),
        .I4(s_axis_tdata[19]),
        .O(y_sum1__5_carry_i_4_n_0));
  LUT4 #(
    .INIT(16'h6996)) 
    y_sum1__5_carry_i_5
       (.I0(y_sum1__5_carry_i_2_n_0),
        .I1(s_axis_tdata[21]),
        .I2(y_sum1__5_carry_i_14_n_0),
        .I3(s_axis_tdata[18]),
        .O(y_sum1__5_carry_i_5_n_0));
  LUT6 #(
    .INIT(64'h6969969699669966)) 
    y_sum1__5_carry_i_6
       (.I0(y_sum1__5_carry_i_15_n_0),
        .I1(s_axis_tdata[17]),
        .I2(s_axis_tdata[22]),
        .I3(s_axis_tdata[20]),
        .I4(y_sum1__5_carry_i_12_n_0),
        .I5(s_axis_tdata[19]),
        .O(y_sum1__5_carry_i_6_n_0));
  LUT5 #(
    .INIT(32'h96696996)) 
    y_sum1__5_carry_i_7
       (.I0(s_axis_tdata[19]),
        .I1(s_axis_tdata[22]),
        .I2(s_axis_tdata[20]),
        .I3(y_sum1__5_carry_i_12_n_0),
        .I4(s_axis_tdata[16]),
        .O(y_sum1__5_carry_i_7_n_0));
  LUT6 #(
    .INIT(64'h66636369C666C666)) 
    y_sum1__5_carry_i_8
       (.I0(s_axis_tdata[19]),
        .I1(s_axis_tdata[21]),
        .I2(s_axis_tdata[20]),
        .I3(s_axis_tdata[17]),
        .I4(s_axis_tdata[16]),
        .I5(s_axis_tdata[18]),
        .O(y_sum1__5_carry_i_8_n_0));
  LUT5 #(
    .INIT(32'h6369C666)) 
    y_sum1__5_carry_i_9
       (.I0(s_axis_tdata[18]),
        .I1(s_axis_tdata[20]),
        .I2(s_axis_tdata[19]),
        .I3(s_axis_tdata[16]),
        .I4(s_axis_tdata[17]),
        .O(y_sum1__5_carry_i_9_n_0));
  CARRY8 \y_sum1_inferred__0/i___1_carry 
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({\y_sum1_inferred__0/i___1_carry_n_0 ,\y_sum1_inferred__0/i___1_carry_n_1 ,\y_sum1_inferred__0/i___1_carry_n_2 ,\y_sum1_inferred__0/i___1_carry_n_3 ,\y_sum1_inferred__0/i___1_carry_n_4 ,\y_sum1_inferred__0/i___1_carry_n_5 ,\y_sum1_inferred__0/i___1_carry_n_6 ,\y_sum1_inferred__0/i___1_carry_n_7 }),
        .DI({i___1_carry_i_1_n_0,i___1_carry_i_2_n_0,i___1_carry_i_3_n_0,s_axis_tdata[8],s_axis_tdata[10:8],1'b0}),
        .O(y_sum1[10:3]),
        .S({i___1_carry_i_4_n_0,i___1_carry_i_5_n_0,i___1_carry_i_6_n_0,i___1_carry_i_7_n_0,i___1_carry_i_8_n_0,i___1_carry_i_9_n_0,i___1_carry_i_10_n_0,i___1_carry_i_11_n_0}));
  CARRY8 \y_sum1_inferred__0/i___1_carry__0 
       (.CI(\y_sum1_inferred__0/i___1_carry_n_0 ),
        .CI_TOP(1'b0),
        .CO({\NLW_y_sum1_inferred__0/i___1_carry__0_CO_UNCONNECTED [7:4],\y_sum1_inferred__0/i___1_carry__0_n_4 ,\y_sum1_inferred__0/i___1_carry__0_n_5 ,\y_sum1_inferred__0/i___1_carry__0_n_6 ,\y_sum1_inferred__0/i___1_carry__0_n_7 }),
        .DI({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,s_axis_tdata[13],i___1_carry__0_i_1_n_0}),
        .O({\NLW_y_sum1_inferred__0/i___1_carry__0_O_UNCONNECTED [7:4],y_sum1[14:11]}),
        .S({1'b0,1'b0,1'b0,1'b0,s_axis_tdata[15:14],i___1_carry__0_i_2_n_0,i___1_carry__0_i_3_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 y_sum__41_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({y_sum__41_carry_n_0,y_sum__41_carry_n_1,y_sum__41_carry_n_2,y_sum__41_carry_n_3,y_sum__41_carry_n_4,y_sum__41_carry_n_5,y_sum__41_carry_n_6,y_sum__41_carry_n_7}),
        .DI({y_sum1[8:3],C[2],s_axis_tdata[8]}),
        .O({y[0],NLW_y_sum__41_carry_O_UNCONNECTED[6:0]}),
        .S({y_sum__41_carry_i_1__0_n_0,y_sum__41_carry_i_2_n_0,y_sum__41_carry_i_3_n_0,y_sum__41_carry_i_4_n_0,y_sum__41_carry_i_5_n_0,y_sum__41_carry_i_6_n_0,y_sum__41_carry_i_7_n_0,y_sum__41_carry_i_8_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY8 y_sum__41_carry__0
       (.CI(y_sum__41_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_y_sum__41_carry__0_CO_UNCONNECTED[7:6],y_sum__41_carry__0_n_2,y_sum__41_carry__0_n_3,y_sum__41_carry__0_n_4,y_sum__41_carry__0_n_5,y_sum__41_carry__0_n_6,y_sum__41_carry__0_n_7}),
        .DI({1'b0,1'b0,y_sum1[14:9]}),
        .O({NLW_y_sum__41_carry__0_O_UNCONNECTED[7],y[7:1]}),
        .S({1'b0,y_sum__41_carry_i_1_n_0,y_sum__41_carry_i_2__0_n_0,y_sum__41_carry_i_3__0_n_0,y_sum__41_carry_i_4__0_n_0,y_sum__41_carry_i_5__0_n_0,y_sum__41_carry_i_6__0_n_0,y_sum__41_carry_i_7__0_n_0}));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_1
       (.I0(y_sum_carry__0_n_1),
        .I1(\y_sum1_inferred__0/i___1_carry__0_n_4 ),
        .O(y_sum__41_carry_i_1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_1__0
       (.I0(y_sum1[8]),
        .I1(C[8]),
        .O(y_sum__41_carry_i_1__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_2
       (.I0(y_sum1[7]),
        .I1(C[7]),
        .O(y_sum__41_carry_i_2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_2__0
       (.I0(y_sum1[14]),
        .I1(C[14]),
        .O(y_sum__41_carry_i_2__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_3
       (.I0(y_sum1[6]),
        .I1(C[6]),
        .O(y_sum__41_carry_i_3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_3__0
       (.I0(y_sum1[13]),
        .I1(C[13]),
        .O(y_sum__41_carry_i_3__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_4
       (.I0(y_sum1[5]),
        .I1(C[5]),
        .O(y_sum__41_carry_i_4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_4__0
       (.I0(y_sum1[12]),
        .I1(C[12]),
        .O(y_sum__41_carry_i_4__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_5
       (.I0(y_sum1[4]),
        .I1(C[4]),
        .O(y_sum__41_carry_i_5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_5__0
       (.I0(y_sum1[11]),
        .I1(C[11]),
        .O(y_sum__41_carry_i_5__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_6
       (.I0(y_sum1[3]),
        .I1(C[3]),
        .O(y_sum__41_carry_i_6_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_6__0
       (.I0(y_sum1[10]),
        .I1(C[10]),
        .O(y_sum__41_carry_i_6__0_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    y_sum__41_carry_i_7
       (.I0(s_axis_tdata[9]),
        .I1(s_axis_tdata[8]),
        .I2(C[2]),
        .O(y_sum__41_carry_i_7_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_7__0
       (.I0(y_sum1[9]),
        .I1(C[9]),
        .O(y_sum__41_carry_i_7__0_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum__41_carry_i_8
       (.I0(s_axis_tdata[8]),
        .I1(C[1]),
        .O(y_sum__41_carry_i_8_n_0));
  CARRY8 y_sum_carry
       (.CI(1'b0),
        .CI_TOP(1'b0),
        .CO({y_sum_carry_n_0,y_sum_carry_n_1,y_sum_carry_n_2,y_sum_carry_n_3,y_sum_carry_n_4,y_sum_carry_n_5,y_sum_carry_n_6,y_sum_carry_n_7}),
        .DI({y_sum0[7:3],y_sum1__5_carry_n_15,s_axis_tdata[1:0]}),
        .O({C[7:1],NLW_y_sum_carry_O_UNCONNECTED[0]}),
        .S({y_sum_carry_i_1_n_0,y_sum_carry_i_2_n_0,y_sum_carry_i_3_n_0,y_sum_carry_i_4_n_0,y_sum_carry_i_5_n_0,y_sum_carry_i_6_n_0,y_sum_carry_i_7_n_0,y_sum_carry_i_8_n_0}));
  CARRY8 y_sum_carry__0
       (.CI(y_sum_carry_n_0),
        .CI_TOP(1'b0),
        .CO({NLW_y_sum_carry__0_CO_UNCONNECTED[7],y_sum_carry__0_n_1,y_sum_carry__0_n_2,y_sum_carry__0_n_3,y_sum_carry__0_n_4,y_sum_carry__0_n_5,y_sum_carry__0_n_6,y_sum_carry__0_n_7}),
        .DI({1'b0,1'b0,1'b0,y_sum0[12:8]}),
        .O({NLW_y_sum_carry__0_O_UNCONNECTED[7],C[14:8]}),
        .S({1'b0,y_sum1__5_carry__0_n_4,y_sum1__5_carry__0_n_12,y_sum_carry__0_i_1_n_0,y_sum_carry__0_i_2_n_0,y_sum_carry__0_i_3_n_0,y_sum_carry__0_i_4_n_0,y_sum_carry__0_i_5_n_0}));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry__0_i_1
       (.I0(y_sum0[12]),
        .I1(y_sum1__5_carry__0_n_13),
        .O(y_sum_carry__0_i_1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry__0_i_2
       (.I0(y_sum0[11]),
        .I1(y_sum1__5_carry__0_n_14),
        .O(y_sum_carry__0_i_2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry__0_i_3
       (.I0(y_sum0[10]),
        .I1(y_sum1__5_carry__0_n_15),
        .O(y_sum_carry__0_i_3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry__0_i_4
       (.I0(y_sum0[9]),
        .I1(y_sum1__5_carry_n_8),
        .O(y_sum_carry__0_i_4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry__0_i_5
       (.I0(y_sum0[8]),
        .I1(y_sum1__5_carry_n_9),
        .O(y_sum_carry__0_i_5_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry_i_1
       (.I0(y_sum0[7]),
        .I1(y_sum1__5_carry_n_10),
        .O(y_sum_carry_i_1_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry_i_2
       (.I0(y_sum0[6]),
        .I1(y_sum1__5_carry_n_11),
        .O(y_sum_carry_i_2_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry_i_3
       (.I0(y_sum0[5]),
        .I1(y_sum1__5_carry_n_12),
        .O(y_sum_carry_i_3_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry_i_4
       (.I0(y_sum0[4]),
        .I1(y_sum1__5_carry_n_13),
        .O(y_sum_carry_i_4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry_i_5
       (.I0(y_sum0[3]),
        .I1(y_sum1__5_carry_n_14),
        .O(y_sum_carry_i_5_n_0));
  LUT3 #(
    .INIT(8'h96)) 
    y_sum_carry_i_6
       (.I0(s_axis_tdata[0]),
        .I1(s_axis_tdata[2]),
        .I2(y_sum1__5_carry_n_15),
        .O(y_sum_carry_i_6_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry_i_7
       (.I0(s_axis_tdata[1]),
        .I1(s_axis_tdata[17]),
        .O(y_sum_carry_i_7_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    y_sum_carry_i_8
       (.I0(s_axis_tdata[0]),
        .I1(s_axis_tdata[16]),
        .O(y_sum_carry_i_8_n_0));
endmodule
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;
    parameter GRES_WIDTH = 10000;
    parameter GRES_START = 10000;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    wire GRESTORE;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;
    reg GRESTORE_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;
    assign (strong1, weak0) GRESTORE = GRESTORE_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

    initial begin 
	GRESTORE_int = 1'b0;
	#(GRES_START);
	GRESTORE_int = 1'b1;
	#(GRES_WIDTH);
	GRESTORE_int = 1'b0;
    end

endmodule
`endif
