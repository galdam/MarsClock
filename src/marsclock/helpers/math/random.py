

class MetaRand:
    s0 = 0
    s1 = 2
    seed = -1
    iteration = 0

    @classmethod
    def set_seed(cls, seed):
        cls.seed = seed
        cls.iteration = 0
        cls.s0 = seed * 39916801 * 524287
        cls.s1 = seed * 7919 * 23209

    @classmethod
    def _random(cls):
        """
        xorshift+
        https://gist.github.com/amano41/4d254198333d890e6ef7ba622923e87c
        https://en.wikipedia.org/wiki/Xorshift#xorshift+
        シフト演算で使用している 3 つの数値は元論文 Table.1 参照
        http://vigna.di.unimi.it/ftp/papers/xorshiftplus.pdf
        doi:10.1016/j.cam.2016.11.006
        """
        x, y = cls.s0, cls.s1
        x = x ^ ((x << 23) & 0xFFFFFFFFFFFFFFFF)  # 64bit
        x = (x ^ (x >> 17)) ^ (y ^ (y >> 26))
        cls.s0, cls.s1 = y, x
        cls.iteration += 1
        return cls.s0 + cls.s1

    @classmethod
    def rand_int(cls, n):
        return cls._random() % n

    @classmethod
    def random_number_picker(cls, max_num, num_picks):
        """
        Generates a sequence of random integers 0 <= n < max_num without repeats.
        """
        num_picks = min(num_picks, max_num)
        picks = []
        while len(picks) < num_picks:
            rand_num = cls._random() % max_num
            if rand_num not in picks:
                picks.append(rand_num)
        return picks
