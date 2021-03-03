from functools import partial
from math import floor, sqrt


def shr(value, bits_num):
    """
    Возвращает результат побитового сдвига числа вправо.

    Пример:
    value = 587 (1001001011)
    bits_num = 3
    shr(587, 3) = 73 (0001001001)

    :param value: целое число
    :param bits_num: количество битов, на которое будет сдвинуто целое число
    """
    shifted = value >> bits_num
    return shifted


def rotr(value: int, bits_num: int, max_bits=32):
    """
    Возвращает результат циклического сдвига числа вправо.

    Пример:
    value = 5234 (00000000000000000001010001110010)
    bits_num = 7
    rotr(5234, 7) = 3825205288 (11100100000000000000000000101000)

    :param value: целое число
    :param bits_num: количество битов, на которое будет выполнен сдвиг
    :param max_bits: максимальная битность результата сдвига
    """
    mask = 2 ** max_bits - 1
    right = value >> bits_num
    left = value << max_bits - bits_num
    result = right | left & mask
    return result


def summ(*values, max_bits=32):
    """
    Возвращает результат суммирования чисел.

    :param values: список или тапл чисел
    :param max_bits: максимальая битность суммы чисел
    """
    result = sum(values) % 2 ** max_bits
    return result


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
    Возвращает число, побитово составленное из значений y и z
    на основе числа x: если x = 1, выбирает значение y, если
    x = 0, выбирает значение z.

    Пример:
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
    Возвращает число, побитово составленное из значений x, y, z
    путем выбора самого частого бита среди x, y, z.

    Пример:
    x: 00000000111111110000000011111111
    y: 00000000000000001111111111111111
    z: 11111111111111110000000000000000
       --------------------------------
       00000000111111110000000011111111
    """
    result = (x & y) ^ (x & z) ^ (y & z)
    return result


def join(strings):
    return ''.join(strings)


def fractional(x):
    return x - floor(x)


def first_32_bits(x):
    return floor(x * 2 ** 32)


def cube_root(x):
    return x ** (1 / 3)


def initial_hash(primes):
    return list(map(first_32_bits, map(fractional, map(sqrt, primes))))


def constants(primes):
    return list(map(first_32_bits, map(fractional, map(cube_root, primes))))


basetwo = partial(int, base=2)


def bin8(value):
    return format(value, '08b')


def bin32(value):
    return format(value, '032b')


def bin64(value):
    return format(value, '064b')


def print_bin32(text, value):
    return print(text, bin32(value))


def set_speed(speed):
    if speed == 'normal':
        return 0
    if speed == 'slow':
        return 1
