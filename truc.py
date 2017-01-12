# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 18:53:17 2016

@author: jean
"""

import multiprocessing
class Calculateur(multiprocessing.Process):
    def __init__(self, c):
        multiprocessing.Process.__init__(self)
        self.c = c
    def run(self):
        self.c.send(100)

class Truc(object):
    def __init__(self):
        self.truc = 0
    

    
    def travailler(self):
        a = [10]
        s, r = multiprocessing.Pipe()
        p = Calculateur(s)
        p.start()
        print(p.is_alive())
        print(r.recv())
        p.join()
        print(a)
        print("et ??")
        