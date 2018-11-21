def is_prime(x):
    d = 2
    while d * d < x:
        if x % d == 0:
            return False
        d += 1
    return True
