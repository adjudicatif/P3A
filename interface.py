
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 16:25:54 2016

@author: jean
"""
print("...")
#%%
#%load_ext autoreload 
import pandas as pd
import numpy as np
import matplotlib.pyplot
import sys
import os

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from point import *
from line import *
from network import *
import random
import time as module_time


root = 'F:/Google Drive/Polytechnique/3A/P3A/DATA/'
p = sys.argv[1:]
#%%
### What Data
###

while True :
    print("Do you want a new network (n) or to load an existing one (type the name)")
    if len(p) > 0 :
        rep = p.pop(0)
        print(rep)
    else :
        rep = input()
    
    if rep == "n" :
        print("What limit do you expect ?")
        if len(p) > 0 :
            limit = p.pop(0)
            print(limit)
        else :
            limit = input()
        
        try : int(7600000) < limit
        except TypeError:
            limit = 7600000
            print(limit)
            
        print("What name for the network ?")
        if len(p) > 0 :
            name = p.pop(0)
            print(name)
        else :
            name = input()
            
        network = Network.new(root, name, limit)
        
        
        
        
        
        print("Network created and saved")
        break
        
    #They typed a name
    else :
        network = Network.open_file(root+ rep +".ntwk")
        print("Network loaded")
        break


#%%
##Interactive drawing
###

def onclick(event):
    global plt
    s = network.add_station(Point([event.xdata, event.ydata]), line)
#    plt = s.plot(plt, edges=1)
    plt = line.plot(plt, points=1)
    plt.draw()
    
#Tant qu'on veut ajouter des lignes :
while input("Draw a line ? (y for Yes)\n") == "y" :
    print("...")
    t = module_time.time()
    #Affiche
    plt = network.load_flux(edges=1, info=1)
    #Création
    line = network.new_line()
    t = str(round(module_time.time() - t))
    print("\ttook", t, "s")
    cid = plt.connect("button_press_event", onclick)
    plt.show()

network.load_flux(info=1)
for lid in network.line :
    load = network.get_load(lid, info=1)

network.cost(info=1)
    
rep = input("Do you want to save ? (y for Yes) , (n for no) (name for new file\n")
if rep == "y" :
    network.save(info=1)
elif rep == "n" :
    pass
else:
    network.name = rep
    network.save(info=1)
