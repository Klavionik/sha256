import sys
from utils import *
from constants import K, PRIMES_8
from time import sleep
import progressbar
import logging

log = logging.getLogger(__name__)
stdout = logging.StreamHandler()
log.addHandler(stdout)


class DummyPB(progressbar.ProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def start(self, max_value=None, init=True):
        pass

    def update(self, value=None, force=False, **kwargs):
        pass

    def finish(self, end='\n', dirty=False):
        pass


widgets = [progressbar.Percentage(), progressbar.Bar()]


class SHA256:
    block_length = 512
    schedule_length = 64
    expand_length = 48
    word_length = 32
    schedule_window = 16

    def __init__(self, speed='normal', pb=None, loglevel=logging.INFO):
        self._origin_string = ''
        self._origin_binary = ''

        self._initial_hash = initial_hash(PRIMES_8)
        self._current_hash = ''

        # initialize working variables
        self.a = self._initial_hash[0]
        self.b = self._initial_hash[1]
        self.c = self._initial_hash[2]
        self.d = self._initial_hash[3]
        self.e = self._initial_hash[4]
        self.f = self._initial_hash[5]
        self.g = self._initial_hash[6]
        self.h = self._initial_hash[7]

        self._init_utils(speed, pb, loglevel)

    def _init_utils(self, speed, pb, loglevel):
        self.speed = set_speed(speed)

        log.setLevel(loglevel)

        if not pb:
            pb = DummyPB

        self.pb = pb

    def __str__(self):
        return f'SHA256 Hash for {self._origin_string}'

    def save_intermediate(self):
        self._initial_hash[0] = self.a
        self._initial_hash[1] = self.b
        self._initial_hash[2] = self.c
        self._initial_hash[3] = self.d
        self._initial_hash[4] = self.e
        self._initial_hash[5] = self.f
        self._initial_hash[6] = self.g
        self._initial_hash[7] = self.h

    def compress(self, schedule):
        log.debug('Compressing schedule...')

        pb = self.pb(redirect_stdout=True, widgets=widgets, max_value=64, min_value=0)
        pb.start()

        for i, (word, constant) in enumerate(zip(schedule, K)):
            sleep(self.speed * 0.05)

            t1 = summ(bsigma1(self.e), choice(self.e, self.f, self.g), self.h, constant, word)
            t2 = summ(bsigma0(self.a), majority(self.a, self.b, self.c))

            self.h = self.g
            self.g = self.f
            self.f = self.e
            self.e = summ(self.d, t1)
            self.d = self.c
            self.c = self.b
            self.b = self.a
            self.a = summ(t1, t2)

            pb.update(i + 1)

        pb.finish()

        self.a = summ(self.a, self._initial_hash[0])
        self.b = summ(self.b, self._initial_hash[1])
        self.c = summ(self.c, self._initial_hash[2])
        self.d = summ(self.d, self._initial_hash[3])
        self.e = summ(self.e, self._initial_hash[4])
        self.f = summ(self.f, self._initial_hash[5])
        self.g = summ(self.g, self._initial_hash[6])
        self.h = summ(self.h, self._initial_hash[7])

        self.save_intermediate()
        self._current_hash = self.concat_variables()

    def registers_to_hex(self):
        hex_ = [format(i, '08x') for i in [self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h]]
        return hex_

    def concat_variables(self):
        return join(self.registers_to_hex())

    @staticmethod
    def sum_words(x, y, z, e):
        sigma_x = sigma1(x)
        sigma_z = sigma0(z)
        blocks_sum = summ(sigma_x, y, sigma_z, e)
        return blocks_sum

    def make_next_word(self, words_block):
        x = words_block[-2]
        y = words_block[-7]
        z = words_block[-15]
        e = words_block[-16]
        word = self.sum_words(x, y, z, e)
        return word

    def expand_schedule(self, schedule):
        def move_schedule():
            for index in range(0, self.expand_length):
                next_word_index = index + self.schedule_window
                yield next_word_index, schedule[index:next_word_index]

        log.debug('Expanding schedule to 64 words...')
        sleep(self.speed * 1)
        pb = self.pb(redirect_stdout=True, widgets=widgets, max_value=64, min_value=16)
        pb.start()

        for i, words in move_schedule():
            next_word = self.make_next_word(words)
            schedule.append(next_word)

            sleep(self.speed * 0.05)
            pb.update(i + 1)

        pb.finish()

        return schedule

    def create_message_schedule(self, block):
        def yield_words():
            for index in range(0, len(block), self.word_length):
                word = block[index:index + self.word_length]
                yield basetwo(word)

        schedule = list(yield_words())
        sleep(self.speed * 2)

        schedule = self.expand_schedule(schedule)

        return schedule

    def yield_schedules(self, blocks):
        for i, block in enumerate(blocks, start=1):
            log.debug(f'Processing block {i} out of {len(blocks)}')
            yield self.create_message_schedule(block)

    def split_string(self, string):
        def yield_blocks():
            for index in range(0, len(string), self.block_length):
                yield string[index:index + self.block_length]

        blocks = list(yield_blocks())
        log.debug(f'Total blocks: {len(blocks)}\n{"-" * 128}')
        sleep(self.speed * 2)
        return blocks

    def pad_binary(self, string):
        string_len = len(string)
        sleep(self.speed * 2)
        padding_len = (448 - string_len - 1) % 512

        string = string + '1' + padding_len * '0'
        message_length = bin64(string_len)
        string = string + message_length

        log.debug(f'Padded input: {string}, ({len(string)} bits)')
        return string

    @staticmethod
    def string_to_bin(string):
        log.debug(f'Input string: {string}')
        ascii_codes = [ord(char) for char in string]
        log.debug(f'Input ASCII codes: {ascii_codes}')
        binary = join([bin8(code) for code in ascii_codes])
        log.debug(f'Input binary: {binary} ({len(binary)} bits)\n{"-" * 128}')
        return binary

    def _calculate_hash(self):
        binary_string = self.string_to_bin(self._origin_string)
        padded_string = self.pad_binary(binary_string)
        blocks = self.split_string(padded_string)

        for schedule in self.yield_schedules(blocks):
            self.compress(schedule)
            log.debug(f'Intermediate hash: {self._current_hash}')
            log.debug('-' * 128)

        return self._current_hash

    def hash(self, string: str) -> str:
        self._origin_string = string
        return self._calculate_hash()


def main():
    string = sys.argv[1]
    try:
        speed = sys.argv[2]
    except IndexError:
        speed = 'normal'

    pb = progressbar.ProgressBar
    loglevel = logging.DEBUG

    hasher = SHA256(speed, pb, loglevel)
    print('Final hash:', hasher.hash(string))


if __name__ == '__main__':
    main()
