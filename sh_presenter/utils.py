import random
from string import ascii_letters


def random_string(length: int) -> str:
    """
    Generate random token from ansii letters of given length

    @param length: TODO
    """
    return ''.join(random.choice(ascii_letters) for _ in range(length))
