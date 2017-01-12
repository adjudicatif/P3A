# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 16:25:54 2016

@author: jean
"""
#%%
#%load_ext autoreload 
import pandas as pd
import numpy as np
import matplotlib.pyplot
import os
root = 'F:/Google Drive/Polytechnique/3A/P3A/DATA/'

#%%
### PREPARE DATA
###
#
#coord = pd.read_csv(root+"COORD.csv", header=None)
#coord = coord.rename(columns={0:'X',1:'Y'})
#
#zones = pd.read_csv(root+'ZONES.csv', header=None)
#zones = zones.rename(columns={0:'pid'})
#
#points = coord
#points['pid'] = zones
#points['pid'] = points['pid'].astype(int)
#points = points.set_index('pid')
#
#origin = {'X':600000, 'Y':2200000} #Selon fichier sur R
#for ax in origin :
#    points[ax] = (points[ax]  - origin[ax]) / 1000
#
#flux = pd.read_csv(root+'Mat2010.csv', sep=";", header=None)
#flux = flux.rename(columns={0:'O',1:'D',2:'n'})
#flux = flux.drop([3], axis=1)
#flux['O'] = flux['O'].astype(int)
#flux['D'] = flux['D'].astype(int)
#
##limit =  7500600 
#limit = 7600000
#points_ = points.loc[:limit]
#flux_ = flux[(flux['O'] < limit) * (flux['D'] < limit)]
#flux_ = flux_.set_index(['O','D'])
#
#points_.to_csv(root+"points_.csv")
#flux_.to_csv(root+"flux_.csv")
#
#points_ = pd.read_csv(root+"points_.csv")
#points_ = points_.set_index('pid')
#flux_ = pd.read_csv(root+"flux_.csv")
#flux_ = flux_.set_index(['O', 'D'])
#
#print("Data loaded")

#%%
###
###
#%autoreload 2
from point import Point, Station, Zone
from line import Line
from network import Network
from paths import Path
import random
import time as module_time

#Station(pt)
#network = Network(name="Paris", root=root)
#network.set_data(points_, flux_)
#network.save()
#print("Network loaded and saved")

#AJOUT LIGNES
#n_stations = 3
#n_lignes = 2
#for i in range(n_lignes):
#    pts = np.random.permutation(points_)[:n_stations]
#    pts = pts + 1*np.random.sample(pts.shape)
#    line = network.new_line(pts, info=0)
#plt = network.plot(points=1, lines=True, edges=True)
#
##AJOUT LIGNE mANUEL
#pts = [[-3, 133], [-2, 132], [-1, 131],
#       [0,130],
#       [1, 129],
#        [2, 128],
#        [3, 127]]
#network.new_line(pts)
#network.save()

#RETRAITS
#network.remove_station(network[103])
#plt = network.plot(points=1, lines=True, edges=True)
#for lid in np.random.permutation(np.arange(n_lignes)):
#    network.remove_line(network[lid], info=1)
#    plt = network.plot(points=1, lines=True, edges=True)

#TEST AJOUT STATIONS
#n_stations = 1
#for lid in range(n_lignes):
#    pts = np.random.permutation(points_)[:n_stations]
#    pts = pts + 1000*np.random.sample(pts.shape)
#    for pt in pts:
#        line = network.line[lid]
#        where = int(np.random.rand() * len(line))
#        network.add_station(Point(pt), line, where)
#        network.plot().show()
#plt = network.plot(points=1, lines=True)
    
#VERIFIER CONNEXITE ET TOUS LES LIENS SONT A DEUX SENS
#for k1, pt1 in network.points().items() :
#    if len(pt1.children) == 0 :
#        print("NO CHILDREN for ", pt1)
#    for k1, [pt2, time] in pt1.children.items() :
#        if not pt1.pid in pt2.children :
#            print("PAIRS ASYMETRIQUES")
#            print(pt1)
#            print(pt2)
        
        
#TEST SINGLE SHORTEST PATH
#i = np.random.randint(0, len(network.flux))
#Opid = network.flux.iloc[i].name
#Dpid = network.flux.iloc[i]['D']
#o = network.zones[Opid]
#d = network.zones[Dpid]
#print(o)
#print(d)
#path, times, plt = network.single_shortest_path(o, d, plt=plt, route=True, search=False, edges=False)

#SHOTRESTSPATHS
#t = module_time.time()
#E = network.shortest_paths(info=1, situation=1)
#print(module_time.time() - t)

#SHORTEST PATHS 2
#t = module_time.time()
#E = network.shortest_paths2(info=0, situation=0, edges=1)
#print(module_time.time() - t)

#TEST 1 SHORTEST PATHS
#pts = [pt for pt in network.points()]
#o = random.choice(pts)
#d = random.choice(pts)
#print("FROM", o)
#print("TO",d)
#plt = network.plot(points=1, lines=True, edges=0)
#path, times, plt = network.single_shortest_path(o, d, plt=plt, route=1, search=0, edges=False)
#print(times)
#path, times, plt = network.shortest_path(o, d, plt=plt, route=1)
#print(times)
##TEST ALL
#i = 0
#j = 0
#ratios =[]
#n = (len(network.stations) + len(network.zones))**2
#for pt1 in network.points() :
#    for  pt2 in network.points():
##        if i > 0 : break
#        path, times, plt = network.single_shortest_path(pt1, pt2)
#        path_, times_, plt_ = network.shortest_path(pt1, pt2)
#        if j % int(n / 100) == 0 : print(round(100 * j / n), "%")
#        if path != path_ :
#            i+=1
#            print(pt1, pt2)
#            print(sum(times))
#            print(sum(times_))
#            print(path)
#            print(path_)
#            ratios.append(sum(times_)/sum(times))
#            plt = network.plot(lines=True, edges=0)
#            network.single_shortest_path(pt1, pt2, plt=plt, route=1)
#            network.shortest_path(pt1, pt2, plt=plt, route=1)
#        j +=1

##LOOK AT THE CHARGE
#plt = network.load_flux(info=1, edges=1)
#plt.show()
#for lid in network.line :
#    network.get_load(lid, info=1)
#    
#keys = sorted(network.charge, key=network.charge.__getitem__)
#for k in keys :
#    print(k, network.charge[k])


#%%
### NEW TESTS
###

        
#n.load_flux(info=1)
#n.save()
#n.random_point().charge(n.charge)
#for i in range(3):
#    n.m_remove_station()
#    n.plot(points=1, lines=1)
#for i in range(3):
#    n.load_flux()
#    n.m_center_stations(0)
#    n.plot(points=1, lines=1)



#family_size = 4
#family = [Network.new(root, "Paris_P1_" + str(n), info=1) for n in range(family_size)]
#print("Fully imported")
#
#for n in family : 
#    n.random_line(2)
#    n.plot(lines=1)
#    
