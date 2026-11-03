# Keep the original 100 ps input-jitter budget on the actual PS primary clock.
# clk_wiz No_buffer deliberately does not create a second primary clock.
set_input_jitter [get_clocks clk_pl_0] 0.100
