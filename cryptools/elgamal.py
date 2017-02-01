# -*- coding: utf-8 -*-

# todo
class ElGamal(object):

    def __init__(self, h, g, p, x):
        assert h == pow(g, x, p)
        self.h = h
        self.g = g
        self.p = p
        self.x = x

    def encrypt(m):
        return

    def decrypt(c):
        return

    pass

