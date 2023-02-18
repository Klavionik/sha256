import math
from functools import partial
from typing import Iterable


def shr(value: int, bits_num: int):
    """
    Returns result of a bitwise right shift.

    Пример:
    value = 587 (1001001011)
    bits_num = 3
    shr(587, 3) = 73 (0001001001)

    :param value: an integer
    :param bits_num: number of bits to shift
    """
    return value >> bits_num


def rotr(value: int, bits_num: int, max_bits: int = 32):
    """
    Returns result of a bitwise right rotate.

    Пример:
    value = 5234 (00000000000000000001010001110010)
    bits_num = 7
    rotr(5234, 7) = 3825205288 (11100100000000000000000000101000)

    :param value: an integer
    :param bits_num: number of bits to shift
    :param max_bits: max amount of bits limiting the result
    """
    mask = 2**max_bits - 1
    right = value >> bits_num
    left = value << max_bits - bits_num
    result = right | left & mask
    return result


def summ(*values: Iterable[int], max_bits: int = 32):
    """
    Returns sum of integers limited by a given number of bits.

    :param values: an iterable of integers
    :param max_bits: max amount of bits limiting the result
    """
    return sum(values) % 2**max_bits


def sigma0(value: int):
    rotr7 = rotr(value, 7)
    rotr18 = rotr(value, 18)
    shr3 = shr(value, 3)
    result = rotr7 ^ rotr18 ^ shr3
    return result


def sigma1(value: int):
    rotr17 = rotr(value, 17)
    rotr9 = rotr(value, 19)
    shr10 = shr(value, 10)
    result = rotr17 ^ rotr9 ^ shr10
    return result


def bsigma0(value: int):
    rotr2 = rotr(value, 2)
    rotr13 = rotr(value, 13)
    rotr22 = rotr(value, 22)
    result = rotr2 ^ rotr13 ^ rotr22
    return result


def bsigma1(value: int):
    rotr6 = rotr(value, 6)
    rotr11 = rotr(value, 11)
    rotr25 = rotr(value, 25)
    result = rotr6 ^ rotr11 ^ rotr25
    return result


def choice(x: int, y: int, z: int):
    """
    Returns a number depending on the value of x:
    if x = 1, choose y,
    if x = 0, choose z.

    Example:
    x: 00000000111111110000000011111111
    y: 00000000000000001111111111111111
    z: 11111111111111110000000000000000
       --------------------------------
       11111111000000000000000011111111
    """
    result = (x & y) ^ (~x & z)
    return result


def majority(x: int, y: int, z: int):
    """
    Returns a number depending on the most common bit across x, y, z.

    Example:
    x: 00000000111111110000000011111111
    y: 00000000000000001111111111111111
    z: 11111111111111110000000000000000
       --------------------------------
       00000000111111110000000011111111
    """
    return (x & y) ^ (x & z) ^ (y & z)


def fractional(x):
    return x - math.floor(x)


def first_32_bits(x):
    return math.floor(x * 2**32)


def cube_root(x):
    return x ** (1 / 3)


def initial_hash(primes):
    return list(map(first_32_bits, map(fractional, map(math.sqrt, primes))))


def constants(primes):
    return list(map(first_32_bits, map(fractional, map(cube_root, primes))))


basetwo = partial(int, base=2)


def bin8(value):
    return format(value, "08b")


def bin32(value):
    return format(value, "032b")


def bin64(value):
    return format(value, "064b")


def print_bin32(text, value):
    return print(text, bin32(value))
