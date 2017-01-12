# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 10:46:22 2017

@author: jean
"""
import multiprocessing as mp
from network import Network

root = 'F:/Google Drive/Polytechnique/3A/P3A/DATA/'

class Individu(mp.Process):
    def __init__(self, common, lock):
        mp.Process.__init__(self)
        self.common = common
        self.lock = lock
        
        self.n = Network.new(root, "P")
        with self.lock :
            self.common[self.pid] = [self.n]
        
    def run(self):
        print("on it")
        
        