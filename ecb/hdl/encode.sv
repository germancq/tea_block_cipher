/**
 * File              : encode.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 14.07.2025
 * Last Modified Date: 14.07.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module encode (
    input clk,
    input rst,
    input start,
    input [63:0] block_i,
    output [63:0] block_o,
    input [127:0] key,
    output logic end_signal
);

  localparam DELTA = 32'h9e3779b9;

  assign block_o[31:0]  = z_reg_dout;
  assign block_o[63:32] = y_reg_dout;

  logic rounds_counter_rst;
  logic rounds_counter_up;
  logic rounds_counter_down;
  logic [7:0] rounds_counter_din;
  logic [7:0] rounds_counter_dout;
  counter #(
      .DATA_WIDTH(8)
  ) rounds_counter (
      .clk (clk),
      .rst (rounds_counter_rst),
      .up  (rounds_counter_up),
      .down(rounds_counter_down),
      .din (rounds_counter_din),
      .dout(rounds_counter_dout)
  );


  logic y_reg_cl;
  logic y_reg_w;
  logic [31:0] y_reg_din;
  logic [31:0] y_reg_dout;
  register #(
      .DATA_WIDTH(32)
  ) y_reg (
      .clk(clk),
      .cl(y_reg_cl),
      .w(y_reg_w),
      .din(y_reg_din),
      .dout(y_reg_dout)
  );

  logic z_reg_cl;
  logic z_reg_w;
  logic [31:0] z_reg_din;
  logic [31:0] z_reg_dout;
  register #(
      .DATA_WIDTH(32)
  ) z_reg (
      .clk(clk),
      .cl(z_reg_cl),
      .w(z_reg_w),
      .din(z_reg_din),
      .dout(z_reg_dout)
  );

  logic sum_reg_cl;
  logic sum_reg_w;
  logic [31:0] sum_reg_din;
  logic [31:0] sum_reg_dout;
  register #(
      .DATA_WIDTH(32)
  ) sum_reg (
      .clk(clk),
      .cl(sum_reg_cl),
      .w(sum_reg_w),
      .din(sum_reg_din),
      .dout(sum_reg_dout)
  );

  logic [1:0] current_state, next_state;


  localparam IDLE = 0;
  localparam REG_INPUTS = 1;
  localparam ROUND_ENC = 2;
  localparam END_ENC = 3;

  always_comb begin

    next_state = current_state;

    rounds_counter_up = 0;
    rounds_counter_rst = 0;
    rounds_counter_down = 0;

    y_reg_cl = 0;
    y_reg_w = 0;
    y_reg_din = 0;


    z_reg_cl = 0;
    z_reg_w = 0;
    z_reg_din = 0;

    sum_reg_cl = 0;
    sum_reg_w = 0;
    sum_reg_din = 0;

    end_signal = 0;

    case (current_state)
      IDLE: begin
        rounds_counter_rst = 1;
        y_reg_cl = 1;
        z_reg_cl = 1;
        sum_reg_cl = 1;
        if (start == 1) begin
          next_state = REG_INPUTS;
        end
      end
      REG_INPUTS: begin
        y_reg_din = block_i[63:32];
        z_reg_din = block_i[31:0];
        y_reg_w = 1;
        z_reg_w = 1;
        next_state = ROUND_ENC;
      end
      ROUND_ENC: begin
        rounds_counter_up = 1;
        sum_reg_din = sum_reg_dout + DELTA;
        y_reg_din = y_reg_dout + (((z_reg_dout << 4) + key[127:96]) ^ (z_reg_dout + sum_reg_dout + DELTA) ^ ((z_reg_dout>>5) + key[95:64]));
        z_reg_din = z_reg_dout + (((y_reg_din << 4) + key[63:32]) ^ (y_reg_din + sum_reg_dout + DELTA) ^ ((y_reg_din>>5) + key[31:0]));

        sum_reg_w = 1;
        y_reg_w = 1;
        z_reg_w = 1;

        if (rounds_counter_dout == 31) begin
          next_state = END_ENC;
        end

      end
      END_ENC: begin
        end_signal = 1;
      end

      default: begin
        next_state = IDLE;
      end

    endcase

  end

  always_ff @(posedge clk) begin
    if (rst == 1) begin
      current_state <= IDLE;
    end else begin
      current_state <= next_state;
    end

  end


endmodule
