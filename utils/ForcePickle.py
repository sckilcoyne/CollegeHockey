# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 22:04:00 2021

@author: Scott
"""
# https://stackoverflow.com/questions/60067953/is-it-possible-to-specify-the-pickle-protocol-when-writing-pandas-to-hdf5


import importlib
import pickle


class PickleProtocol:
    def __init__(self, level):
        self.previous = pickle.HIGHEST_PROTOCOL
        self.level = level

    def __enter__(self):
        importlib.reload(pickle)
        pickle.HIGHEST_PROTOCOL = self.level

    def __exit__(self, *exc):
        importlib.reload(pickle)
        pickle.HIGHEST_PROTOCOL = self.previous


def pickle_protocol(level):
    return PickleProtocol(level)
