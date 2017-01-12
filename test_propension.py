# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 20:31:06 2017

@author: jean
"""
from network import Network

root = 'F:/Google Drive/Polytechnique/3A/P3A/'
test = "test_load_flux"
name = "Paris_" + test
serie = "S2"

def rapport(n, i):
    print("...")
    path = root + test + "/" + name + "_" + serie + i
    plt = n.load_flux(edges=1, modes=["metro", "foot", "no_network"])
    plt.savefig(path + ".png")
    plt.close()
    print("RAPPORT", i)
    

n = Network.new(root + "DATA/", "Paris", info=1)
rapport(n, "0")

n.draw_line()
rapport(n, "4")
