#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : encode_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 15.07.2025
# Last Modified Date: 15.07.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import os
import random
import sys

import cocotb
import numpy as np
import tea
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CLK_PERIOD = 20


def setup_dut(dut, blk_i, key):
    print("setup block cipher")
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    dut.start.value = 0
    dut.key.value = key
    dut.block_i.value = blk_i


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


async def rst_function_test(dut):
    print("rst function")
    dut.rst.value = 1
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.IDLE.value
    ), f"ERROR STATE IN IDLE, STATE={dut.current_state.value}"
    await n_cycles_clock(dut, 5)

    assert (
        dut.current_state.value == dut.IDLE.value
    ), f"ERROR STATE IN IDLE, STATE={dut.current_state.value}"

    dut.rst.value = 0


async def reg_input_test(dut, expected_y, expected_z, expected_sum):
    print("reg input test")
    dut.start.value = 1
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.REG_INPUTS.value
    ), f"ERROR STATE IN REG_INPUTS, STATE={dut.current_state.value}"
    assert (
        dut.sum_reg_din.value == expected_sum
    ), f"ERROR STATE IN REG_INPUTS, sum_reg_din={dut.sum_reg_din.value}"
    assert (
        dut.y_reg_din.value == expected_y
    ), f"ERROR STATE IN REG_INPUTS, y_reg_din={dut.y_reg_din.value}"
    assert (
        dut.z_reg_din.value == expected_z
    ), f"ERROR STATE IN REG_INPUTS, z_reg_din={dut.z_reg_din.value}"
    assert (
        dut.y_reg_w.value == 1
    ), f"ERROR STATE IN REG_INPUTS, y_reg_w={dut.y_reg_w.value}"
    assert (
        dut.z_reg_w.value == 1
    ), f"ERROR STATE IN REG_INPUTS, z_reg_w={dut.z_reg_w.value}"


async def round_enc_test(dut, rnd, expected_y, expected_z, expected_sum):
    print("round_enc_test")
    print("rnd")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.ROUND_ENC.value
    ), f"ERROR STATE IN ROUND_ENC, STATE={dut.current_state.value}"
    assert (
        dut.sum_reg_din.value == expected_sum
    ), f"ERROR STATE IN ROUND_ENC, sum_reg_din={hex(dut.sum_reg_din.value)}, expected = {hex(expected_sum)}"
    assert (
        dut.y_reg_din.value == expected_y
    ), f"ERROR STATE IN ROUND_ENC, y_reg_din={hex(dut.y_reg_din.value)}, expected = {hex(expected_y)}"
    assert (
        dut.z_reg_din.value == expected_z
    ), f"ERROR STATE IN ROUND_ENC, z_reg_din={hex(dut.z_reg_din.value)}, expected = {hex(expected_z)}"
    assert (
        dut.y_reg_w.value == 1
    ), f"ERROR STATE IN ROUND_ENC, y_reg_w={dut.y_reg_w.value}"
    assert (
        dut.z_reg_w.value == 1
    ), f"ERROR STATE IN ROUND_ENC, z_reg_w={dut.z_reg_w.value}"
    assert (
        dut.sum_reg_w.value == 1
    ), f"ERROR STATE IN ROUND_ENC, sum_reg_w={dut.sum_reg_w.value}"
    assert (
        dut.rounds_counter_dout.value == rnd
    ), f"ERROR STATE IN ROUND_ENC, rounds_counter_dout={dut.rounds_counter_dout.value}"


async def end_enc_test(dut, expected_result):
    print("end_enc_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.END_ENC.value
    ), f"ERROR STATE IN END_ENC, STATE={dut.current_state.value}"
    assert (
        dut.block_o.value == expected_result
    ), f"ERROR STATE IN END_ENC, block_o={dut.block_o.value}"
    assert (
        dut.end_signal.value == 1
    ), f"ERROR STATE IN END_ENC, end_signal={dut.end_signal.value}"


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    key = random.getrandbits(128)
    plaintext = random.getrandbits(64)
    tea_sw = tea.TEA(key)

    expected_result = tea_sw.encode(plaintext)

    setup_dut(dut, plaintext, key)
    await rst_function_test(dut)
    block_i_1 = (plaintext) & 0xFFFFFFFF
    block_i_0 = (plaintext >> 32) & 0xFFFFFFFF
    sum_var = 0
    y = block_i_0
    z = block_i_1
    await reg_input_test(dut, y, z, sum_var)
    for i in range(0, 32):
        sum_var, y, z = tea_sw.basic_cycle(sum_var, y, z)
        await round_enc_test(dut, i, y, z, sum_var)

    await end_enc_test(dut, expected_result)
