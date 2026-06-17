#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : tea.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 30.06.2025
# Last Modified Date: 30.06.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>


DELTA = 0x9E3779B9
NUMBER_ROUNDS = 32
KEY = 0x80000000000000000000000000000000
PLAINTEXT = 0x0000000000000000


class TEA:

    def __init__(self, key):
        self.key = key
        self.k3 = (key) & 0xFFFFFFFF
        self.k2 = (key >> 32) & 0xFFFFFFFF
        self.k1 = (key >> 64) & 0xFFFFFFFF
        self.k0 = (key >> 96) & 0xFFFFFFFF
        # print(hex(self.k0))
        # print(hex(self.k1))
        # print(hex(self.k2))
        # print(hex(self.k3))

    def encode(self, block_i):
        block_i_1 = (block_i) & 0xFFFFFFFF
        block_i_0 = (block_i >> 32) & 0xFFFFFFFF
        sum_var = 0
        y = block_i_0
        z = block_i_1
        # print(hex(y))
        # print(hex(z))
        for i in range(0, NUMBER_ROUNDS):
            sum_var, y, z = self.basic_cycle(sum_var, y, z)
            # print(i)
            # print(hex(sum_var))
            # print(hex(y))
            # print(hex(z))

        return (y << 32) + (z & 0xFFFFFFFF)

    def basic_cycle(self, sum_var, y, z):
        sum_var = (sum_var + DELTA) & 0xFFFFFFFF
        y = y + (((z << 4) + self.k0) ^ (z + sum_var) ^ ((z >> 5) + self.k1))
        y = y & 0xFFFFFFFF
        z = z + (((y << 4) + self.k2) ^ (y + sum_var) ^ ((y >> 5) + self.k3))
        z = z & 0xFFFFFFFF
        return sum_var, y, z


if __name__ == "__main__":
    print("TEA")
    tea = TEA(KEY)
    print(hex(tea.encode(PLAINTEXT)))
