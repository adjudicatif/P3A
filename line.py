# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 22:26:08 2016

@author: jean
"""
import pandas as pd
import numpy as np
try:
    import cPickle as pickle
except:
    import pickle
from point import *


class Line:
    e_par_km = 1 * 10**8
    e_par_station = 3 * 10**7
    e_par_train = 1 * 10**7
    
    ###
    ### PROPERTIES
    ###
    
    def __init__(self, lid, network, name=None):
        self.lid = lid
        self.station = dict()
        self.where = dict() #inverse de station
        self.stop_time = 15 / 3600 #30 s en h
        self.speed = 50
        self.f = 30 #nb par heures
        
        self.network = network
        if name ==  None : self.name = "L" + str(self.lid)
        else : selt.name = name
        
        self.direct = None
        self.indirect = None
            
    def __repr__(self):
        print("Line", self.lid, ":")
        print(self.station)
        return ""
    def __len__(self): return len(self.station)
    def __getitem__(self, idx): return self.station[idx]
    def __setitem__(self, idx, val): self.station[idx] = val

    def times(self):
        t = []
        for s1, s2 in self.pairs():
            t.append(self.network.time(s1, s2))
            t.append(self.network.time(s2, s1))
        return t
        
    def dists(self) :
        d = []
        for s1, s2 in self.pairs():
            d.append(s1.dist(s2))
            d.append(s2.dist(s1))
        return d
        
    def trains(self):
        return self.f * sum(self.times())
                
    def pairs(self) :
        for i in self.station :
            if i > 0 :
                yield self[i-1], self[i]
    ###
    ### FILES
    ###
    
    def import_points(file):
        with open(file, "rb") as file :
            mon_pickler = pickle.Unpickler(file)
            points = mon_pickler.load()
                        
        return points
                        
    
    def export_points(self):
        points = []
        for s in self.station.values() :
            points.append([s.X, s.Y])
        return points
        
    ###
    ### BUILD
    ###
        
    def add(self, station, where=None):
        """Ajoute une station à la ligne, par défaut à la fin"""
        if where == None :
            where = len(self)
        #décalage de toutes les station :
        for i in np.arange(len(self), where, -1) :
            #on fait de la place
            self[i] = self[i-1]
            self.where[self[i]] = i
        #on rompt le lien entre i et i-1 si on insère en i
        if where > 0 and where + 1 < len(self.station) :
            self[where].unlink(self[where - 1])
        #insertion
        self.station[where] = station
        self.where[station] = where
        #Ajout des voisins
        if where > 0 :
            station.link(self[where - 1])
        if where + 1 < len(self.station) :
            station.link(self[where + 1])
        return self.station
        
    def remove(self, station):
        """Enlève une station à la ligne"""
        #Variable à partir de quand enlever 1
        remove_one = False
        for i in range(len(self.station)) :
            #On décale qu'APRES la station
            if remove_one :  
               self.station[i - 1] = self.station[i]
               self.where[self.station[i - 1]] = i - 1
            if self[i].pid == station.pid :
                #1 On déconnecte les voisins
                if i > 0 :
                    station.unlink(self[i - 1])
                if i + 1 < len(self.station) :
                    station.unlink(self[i + 1])
                #2 on les connecte entre eux si on est pas une extrémité
                if i > 0 and i + 1 < len(self.station) :
                    self[i - 1].link(self[i + 1]) 
                #On indique qu'il faut à présent enlever 1 à tous ceux après
                remove_one = True
                self.where.pop(station)
        #Il reste qu'une valeur à enlever : la dernière qui est en double
        self.station.pop(len(self.station) - 1)
        return self.station
        
    
    def plot(self, plt, points=True, edges=False):
        X = []
        Y = []
        for n, station in self.station.items():
            X.append(station.X)
            Y.append(station.Y)
            plt = station.plot(plt, point=points, edges=edges, zorder=20)
        plt.plot(X, Y, label=self.lid, marker="o", zorder=0)
        return plt
        
    ###
    ### WORK
    ###
        
    def load(self, load):
        self.direct = load[0]
        self.indirect = load[1]
        
    def costs(self):
        rails = sum(self.dists()) / 2 * self.e_par_km #construction
        
        stations = len(self) * self.e_par_station  #stations
        
        trains = self.trains() * self.e_par_train #trains
        
        return [rails, stations, trains]
        

#%%
        