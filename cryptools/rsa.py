# -*- coding: utf-8 -*-
from gmpy import root, gcdext, invert, is_square, is_prime
from random import getrandbits

class RSA(object):

    def __init__(self, e, n, p, q):
        self.e = e
        self.n = n
        self.p = p
        self.q = q
        self.d = self.get_private_exponent(e, p, q)

    def encrypt(self, m):
        c = pow(m, self.e, self.n)
        return c

    def decrypt(self, c):
        m = pow(c, self.d, self.n)
        return m

    @staticmethod
    def get_private_exponent(e, p, q):
        phi = (p - 1) * (q - 1)
        d = invert(e, phi)
        return d

    pass


class MultiPrimeRSA(RSA):
    
    def __init__(self, e, n, pairs):
        self.e = e
        self.n = n
        self.pairs = pairs
        self.d = self.get_private_exponent(e, pairs)

    def fast_decrypt(self, c):
        n_ary = []
        a_ary = []
        for p, k in self.pairs:
            pk = p ** k
            phi = pk * (p-1)/p
            d = invert(self.e, phi)
            mk = pow(c, d, pk)
            n_ary.append(pk)
            a_ary.append(mk)
        m = chinese_remainder(zip(n_ary, a_ary))
        return m

    @staticmethod
    def get_private_exponent(e, pairs):
        phi = 1
        for p, k in pairs:
            phi *= (p**(k-1) * (p-1))
        d = invert(e, phi)
        return d

    pass


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


# http://rosettacode.org/wiki/Chinese_remainder_theorem#Python
def chinese_remainder(pairs):
    sum = 0
    n = map(lambda x: x[0], pairs)
    prod = reduce(lambda a, b: a*b, n)

    for n_i, a_i in pairs:
        p = prod / n_i
        sum += a_i * invert(p, n_i) * p
    return sum % prod


def random_prime(bits):
    while True:
        n = getrandbits(bits)
        if is_prime(n):
            return n

########## Attack for RSA ##########

# Refered:
# - http://inaz2.hatenablog.com/entry/2016/01/15/011138


def low_public_exponent_attack(c, e):
    bound = root(n, e)[0]
    m = root(c, e)[0]
    return m, bound


def common_modulus_attack(c1, c2, e1, e2, n):
    gcd, s1, s2 = gcdext(e1, e2)
    if s1 < 0:
        s1 = -s1
        c1 = invert(c1, n)
    if s2 < 0:
        s2 = -s2
        c2 = invert(c2, n)
    v = pow(c1, s1, n)
    w = pow(c2, s2, n)
    m = (v * w) % n
    return m


def wieners_attack(e, n):
    def continued_fraction(n, d):
        """
        415/93 = 4 + 1/(2 + 1/(6 + 1/7))

        >>> continued_fraction(415, 93)
        [4, 2, 6, 7]
        """
        cf = []
        while d:
            q = n // d
            cf.append(q)
            n, d = d, n-d*q
        return cf

    def convergents_of_contfrac(cf):
        """
        4 + 1/(2 + 1/(6 + 1/7)) is approximately 4/1, 9/2, 58/13 and 415/93

        >>> list(convergents_of_contfrac([4, 2, 6, 7]))
        [(4, 1), (9, 2), (58, 13), (415, 93)]
        """
        n0, n1 = cf[0], cf[0]*cf[1]+1
        d0, d1 = 1, cf[1]
        yield (n0, d0)
        yield (n1, d1)

        for i in xrange(2, len(cf)):
            n2, d2 = cf[i]*n1+n0, cf[i]*d1+d0
            yield (n2, d2)
            n0, n1 = n1, n2
            d0, d1 = d1, d2

    cf = continued_fraction(e, n)
    convergents = convergents_of_contfrac(cf)

    for k, d in convergents:
        if k == 0:
            continue
        phi, rem = divmod(e*d-1, k)
        if rem != 0:
            continue
        s = n - phi + 1
        # check if x^2 - s*x + n = 0 has integer roots
        D = s*s - 4*n
        if D > 0 and is_square(D):
            return d


def hastads_broadcast_attack(e, pairs):
    x = chinese_remainder(pairs)
    m = root(x, e)[0]
    return m


# https://pdfs.semanticscholar.org/899a/4fdc048102471875e24f7fecb3fb8998d754.pdf
def franklin_reiter_related_message_attack(e, n, c1, c2, a, b):
    assert e == 3 and b != 0
    frac = b * (c2 + 2*pow(a,3)*c1 - pow(b,3))
    denom = a * (c2 - pow(a,3)*c1 + 2*pow(b,3))
    m = (frac * invert(denom, n)) % n
    return m


def chosen_ciphertext_attack(e, n, r, mr):
    m = (mr * invert(r, n)) % n
    return m
 
