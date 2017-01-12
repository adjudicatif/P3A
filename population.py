# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 18:57:10 2017

@author: jean
"""
from individu import Individu
import multiprocessing as mp

if __name__=='__main__':
    population = list()
    manager = mp.Manager()
    lock = manager.RLock()
    common = manager.dict()
    population = dict()
    
    i = Individu(common, lock)
    i.start()
    i.join()
    print(common)