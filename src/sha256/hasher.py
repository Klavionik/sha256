import logging
from time import sleep

import progressbar

from sha256 import utils
from sha256.constants import FIRST_8_PRIMES, K

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

SLEEP_FACTOR = 0.05


class DummyPB(progressbar.ProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def start(self, max_value=None, init=True):
        pass

    def update(self, value=None, force=False, **kwargs):
        pass

    def finish(self, end="\n", dirty=False):
        pass


widgets = [progressbar.Percentage(), progressbar.Bar()]


class SHA256:
    block_length = 512
    schedule_length = 64
    expand_length = 48
    word_length = 32
    schedule_window = 16

    def __init__(self, debug: bool = False):
        self._debug = debug
        self._speed = 0
        self._pb = DummyPB

        if self._debug:
            self._speed = 1
            self._pb = progressbar.ProgressBar
            log.setLevel(logging.DEBUG)

        self._origin_string = ""
        self._origin_binary = ""

        self._initial_hash = utils.initial_hash(FIRST_8_PRIMES)
        self._current_hash = ""

        self.a = self._initial_hash[0]
        self.b = self._initial_hash[1]
        self.c = self._initial_hash[2]
        self.d = self._initial_hash[3]
        self.e = self._initial_hash[4]
        self.f = self._initial_hash[5]
        self.g = self._initial_hash[6]
        self.h = self._initial_hash[7]

    def hash(self, string: str) -> str:
        self._origin_string = string
        return self._calculate_hash()

    def _save_intermediate(self):
        self._initial_hash[0] = self.a
        self._initial_hash[1] = self.b
        self._initial_hash[2] = self.c
        self._initial_hash[3] = self.d
        self._initial_hash[4] = self.e
        self._initial_hash[5] = self.f
        self._initial_hash[6] = self.g
        self._initial_hash[7] = self.h

    def _compress(self, schedule):
        log.debug("Compressing schedule...")

        pb = self._pb(redirect_stdout=True, widgets=widgets, max_value=64, min_value=0)
        pb.start()

        for i, (word, constant) in enumerate(zip(schedule, K)):
            sleep(self._speed * SLEEP_FACTOR)

            t1 = utils.summ(
                utils.bsigma1(self.e),
                utils.choice(self.e, self.f, self.g),
                self.h,
                constant,
                word,
            )
            t2 = utils.summ(
                utils.bsigma0(self.a), utils.majority(self.a, self.b, self.c)
            )

            self.h = self.g
            self.g = self.f
            self.f = self.e
            self.e = utils.summ(self.d, t1)
            self.d = self.c
            self.c = self.b
            self.b = self.a
            self.a = utils.summ(t1, t2)

            pb.update(i + 1)

        pb.finish()

        self.a = utils.summ(self.a, self._initial_hash[0])
        self.b = utils.summ(self.b, self._initial_hash[1])
        self.c = utils.summ(self.c, self._initial_hash[2])
        self.d = utils.summ(self.d, self._initial_hash[3])
        self.e = utils.summ(self.e, self._initial_hash[4])
        self.f = utils.summ(self.f, self._initial_hash[5])
        self.g = utils.summ(self.g, self._initial_hash[6])
        self.h = utils.summ(self.h, self._initial_hash[7])

        self._save_intermediate()
        self._current_hash = self._concat_variables()

    def _registers_to_hex(self):
        hex_ = [
            format(i, "08x")
            for i in [self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h]
        ]
        return hex_

    def _concat_variables(self):
        return "".join(self._registers_to_hex())

    @staticmethod
    def _sum_words(x, y, z, e):
        sigma_x = utils.sigma1(x)
        sigma_z = utils.sigma0(z)
        blocks_sum = utils.summ(sigma_x, y, sigma_z, e)
        return blocks_sum

    def _make_next_word(self, words_block):
        x = words_block[-2]
        y = words_block[-7]
        z = words_block[-15]
        e = words_block[-16]
        word = self._sum_words(x, y, z, e)
        return word

    def _expand_schedule(self, schedule):
        def move_schedule():
            for index in range(0, self.expand_length):
                next_word_index = index + self.schedule_window
                yield next_word_index, schedule[index:next_word_index]

        log.debug("Expanding schedule to 64 words...")
        sleep(self._speed * 1)
        pb = self._pb(redirect_stdout=True, widgets=widgets, max_value=64, min_value=16)
        pb.start()

        for i, words in move_schedule():
            next_word = self._make_next_word(words)
            schedule.append(next_word)

            sleep(self._speed * SLEEP_FACTOR)
            pb.update(i + 1)

        pb.finish()

        return schedule

    def _create_message_schedule(self, block):
        def yield_words():
            for index in range(0, len(block), self.word_length):
                word = block[index : index + self.word_length]
                yield utils.basetwo(word)

        schedule = list(yield_words())
        sleep(self._speed * 2)

        schedule = self._expand_schedule(schedule)

        return schedule

    def _yield_schedules(self, blocks):
        for i, block in enumerate(blocks, start=1):
            log.debug(f"Processing block {i} out of {len(blocks)}")
            yield self._create_message_schedule(block)

    def _split_string(self, string):
        def yield_blocks():
            for index in range(0, len(string), self.block_length):
                yield string[index : index + self.block_length]

        blocks = list(yield_blocks())
        log.debug(f'Total blocks: {len(blocks)}\n{"-" * 128}')
        sleep(self._speed * 2)
        return blocks

    def _pad_binary(self, string):
        string_len = len(string)
        sleep(self._speed * 2)
        padding_len = (448 - string_len - 1) % 512

        string = string + "1" + padding_len * "0"
        message_length = utils.bin64(string_len)
        string = string + message_length

        log.debug(f"Padded input: {string} ({len(string)} bits)")
        return string

    @staticmethod
    def _string_to_bin(string):
        log.debug(f"Input string: {string}")
        ascii_codes = [ord(char) for char in string]
        log.debug(f"Input ASCII codes: {ascii_codes}")
        binary = "".join([utils.bin8(code) for code in ascii_codes])
        log.debug(f'Input binary: {binary} ({len(binary)} bits)\n{"-" * 128}')
        return binary

    def _calculate_hash(self):
        binary_string = self._string_to_bin(self._origin_string)
        padded_string = self._pad_binary(binary_string)
        blocks = self._split_string(padded_string)

        for schedule in self._yield_schedules(blocks):
            self._compress(schedule)
            log.debug(f"Intermediate hash: {self._current_hash}")
            log.debug("-" * 128)

        return self._current_hash
