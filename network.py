# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 22:24:35 2016

@author: jean
"""
#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import time as module_time
import random

try:
    import cPickle as pickle
except:
    import pickle
import sys
sys.setrecursionlimit(10000) #Sinon ca marche pas

from rtree import index
from heapq import heappush, heappop

from point import Point, Zone, Station
from line import Line
from paths import Path, Charge

### NETWORK 
class Network(object):
    no_network_speed = 20 #km / h
    parking_time = 15 / 60 #h
    walking_speed = 5 #km h
    waiting_factor = 2 #to penalize the wait of a train
    max_dist = 0.5 #km
    zone_connectivity =  7#number of connected neighbohors of 
    
    add_station_new_line = 0.5
    add_station_max_dist = 1
    
    s_limit = 100 #limit of lines
    z_limit = 10000#limit of ids
    
    pause = 0.000001
    n_proc = 4
    
    def __init__(self, name="Network", root="F:/"):
        """Initialiser le fichier.
        - pid >> pid"""
        object.__init__(self)
        #Info
        self.name = name
        self.root = root
        #Caractéristqieus
        self.map = index.Index()
        self.map_stations = index.Index()
        self.stations = dict()
        self.line = dict()
        self.flux = dict()
        self.zones =  dict() # [pid] [zone]
        self.charge = dict() # [pt1, pt2] [value]
        self.corrupted_charge = False
        self.path = None #Init à set_data
        #
        self.paths = None
        self.by = None # [pt1, pt2] [[next_pt, time]]
    
    ###
    ### PROPERTIES
    ###
                     
    def __getitem__(self, idx): 
        if idx < Network.s_limit :
            return self.line[idx]
        elif idx < Network.z_limit :
            return self.stations[idx]
        else:
            return self.zones[idx]
            
    def __delitem__(self, idx):
        if idx < Network.s_limit :
            self.remove_line(idx)
        elif idx < Network.z_limit :
            self.remove_station(self[idx])
        else:
            print(idx, "NOT REMOVED BECAUSE ZONE")
    
    def random_point(self):
        return self[random.choice(list(self.zones))]
            
    def points(self):
#        pts = set()
        for k, v in self.zones.items() :
            yield v
#            pts.add(v)
        for k, v in self.stations.items():
            yield v
#            pts.add(v)
            
    def pid_get(self, pid):
        if pid > self.z_limit :
            return self.zones[pid]
        else:
            return self.stations[pid]
            
    ###
    ### FILES
    ###
            
    def new(root, name, limit=7600000, info=0):
        if info > 0 : 
            print("importing CSVs")
            t = module_time.time()
        coord = pd.read_csv(root+"COORD.csv", header=None)
        coord = coord.rename(columns={0:'X',1:'Y'})
        
        zones = pd.read_csv(root+'ZONES.csv', header=None)
        zones = zones.rename(columns={0:'pid'})
        
        points = coord
        points['pid'] = zones
        points['pid'] = points['pid'].astype(int)
        points = points.set_index('pid')
        
        origin = {'X':600000, 'Y':2200000} #Selon fichier sur R
        for ax in origin :
            points[ax] = (points[ax]  - origin[ax]) / 1000
        
        flux = pd.read_csv(root+'Mat2010.csv', sep=";", header=None)
        flux = flux.rename(columns={0:'O',1:'D',2:'n'})
        flux = flux.drop([3], axis=1)
        flux['O'] = flux['O'].astype(int)
        flux['D'] = flux['D'].astype(int)

        points_ = points.loc[:limit]
        flux_ = flux[np.logical_and(flux['O'] < limit, flux['D'] < limit)]
        flux_ = flux_.set_index(['O','D'])
        
        #Create the network
        network = Network(name=name, root=root)
        network.set_data(points_, flux_)
        
        if info > 0 :
            print("\ttook", round(module_time.time() - t))
        return network
            
    def open_file(file):
        with open(file, 'rb') as fichier:
            mon_pickler = pickle.Unpickler(fichier)
            dict_attr = mon_pickler.load().__dict__
        rep = Network()
        
        for attr, val in dict(dict_attr).items():
            rep.__setattr__(attr, val)
        
        #En fait les pts sont pas dedans, il faut les remettre
        for pt in rep.points():
            rep.map.add(pt.pid, pt.bbox)
            if isinstance(pt, Station):
                rep.map_stations.add(pt.pid, pt.bbox)
        return rep
        
    def save(self, info=1):
        try :
            del self.plt
        except AttributeError:
            pass
        
        with open(self.root + self.name + ".ntwk", 'wb') as fichier:
            mon_depickler = pickle.Pickler(fichier)
            mon_depickler.dump(self)
        self.printi(info*2, "Saved as "+self.name)
        
    def import_line(self, file):
        points = Line.import_points(file)
        line = self.new_line(points)
        return line
    
    def export_line(self, lid, name=None):
        if name == None :
            name = self.name + "_L" + str(lid) + ".line"
            
        with open(self.root + name, "wb") as file :
            mon_depickler = pickle.Pickler(file)
            mon_depickler.dump(self[lid].export_points())

    ###
    ### BUILD NETWORK
    ###
        
    def link(self, pt):
        #Si on est à un station
        if isinstance(pt, Station):
            station = pt
            #erase previous links (but not of those within the line)
            for s in station.children:
                if s.lid != station.lid :
                    station.unlink(s)
            #a link is created if it is enough close from an other station
            for pid in self.map.intersection(station.bbox_square(Network.max_dist)) :
                #On ne relie pas les pts sur eux mêmes
                if pid == station.pid :
                    continue
                #Check if it is a station not on the same line
                else :
                    pt = self.pid_get(pid)
                    if isinstance(pt, Station) and pt.lid == station.lid : pass
                    else : station.link(pt)
        #a priori utilisé qu'à l'initialisation !
        elif isinstance(pt, Zone):
            zone = pt
            #erase ALL previous links pour éviter les doublons !
            #!!!!!!!PB excentré : bois de boulogne !!
#            while len(zone.children) > 0:
#                pt.unlink(zone.children.pop())
            #create links with nearest neighbors
            for pid in self.map.nearest(zone.bbox, num_results=Network.zone_connectivity):
                #On ne relie pas les pts sur eux mêmes
                if pid == zone.pid : continue
                else : 
                    pt = self.pid_get(pid)
                    zone.link(pt)
                    
    def add_station(self, pt, line, where=None, info=0):
        pid = Network.s_limit
        while pid in self.stations : 
            pid += 1
            #Si on est hors des bornes
            if pid >= Network.z_limit : raise KeyError
        station = Station(pt, pid, line)
        #ajout à la map des stations
        self.map.insert(pid, station.bbox)
        self.map_stations.insert(pid, station.bbox)
        self.stations[pid] = station
        #ajout à la ligne
        line.add(station, where)
        #cherche les plus proches voisin pour faire une connexion
        self.link(station)
        self.printi(info, "add_station "+str(pt)+" in "+str(line.lid))
        
        return station
        
    def remove_station(self, s, info=0):
        self.printi(info*2, "removing " +str(s))
        line = self[s.lid]
        #On déconnecte du graphe
        while len(s.children) > 0 :
            s.unlink(s.children.pop())
        #On supprime de la ligne
        line.remove(s)
        #on supprime du graphe
        self.map.delete(s.pid, s.bbox)
        self.map_stations.delete(s.pid, s.bbox)
        self.stations.pop(s.pid)
        #Si la ligne st vide on la supprime
        if len(line) == 0 :
            self.line.pop(line.lid)
        
    def new_line(self, pts=[], info=0):
        self.printi(info*2, "New line creating ")
        #create the line
        lid = 0
        while lid in self.line : 
            lid += 1
            #Si on est hors des bornes
            if lid >= Network.s_limit : raise KeyError
        self.line[lid] = Line(lid, self)
        self.printi(info*2, "New line created"+str(lid))
        #add the map
        for pairXY in pts :
            pt = Point(pairXY)
            self.add_station(pt, self.line[lid], info=info*2)
        #update list of map
        self.printi(info, "New line stations inserted ")
        
        return self.line[lid]
        
    def random_line(self, n_stations=10):
        zones = random.sample(list(self.zones), n_stations)
        pts = []
        for zid in zones :
            pts.append(self[zid].pairXY())
        return self.new_line(pts)
        
    def remove_line(self, lid, info=0):
        line = self[lid]
        while len(line) > 0 :
            self.printi(info*2, line)
            self.remove_station(line[0], info=info)
        #La ligne se supprime après la suppression de la dernière station
            
    def draw_line(self, plt=None):
        if plt ==None :
            self.plt = self.plot(ion=0, lines=1, points=1)
        line = self.new_line()
        
        def onclick(event):
            self.add_station(Point([event.xdata, event.ydata]), line)
            line.plot(self.plt, points=1)
            self.plt.draw()
        
        self.plt.connect("button_press_event", onclick)
        self.plt.show(block=True)
        
    ###
    ### USE NETWORK
    ###
	
    def printi(self, info, message):
        if info > 0 : 
            ns = ""
            for i in range(int(np.log2(info))):
                ns += "  "
            print(ns, message)       

        
    def set_data(self, points, flux) :
        self.flux = dict()
        self.zones =  dict()
        for pid, pairXY in points.iterrows() :
            zone = Zone(Point(pairXY), pid)
            self.zones[pid] = zone
            self.map.insert(pid, zone.bbox)
        for pid, zone in self.zones.items():
            self.link(zone)
        for [pid1, pid2], flux in flux.iterrows():
            self.flux[self.pid_get(pid1), self.pid_get(pid2)] = flux['n']
        #Maintenant on peut fharger le path
        self.path = Path(self)
    
    def draw(self, plt):
        if plt.isinteractive():
            plt.draw()
#            plt.pause(Network.pause)
    
    def plot(self, plt=None, ion=1, 
             points=0, lines=0, edges=0, 
             points_load=0, edges_load=0, modes=["metro"]):
        """PLOT anything in the graphe"""
        #PLT
        if plt == None :
            plt = pyplot
            fig = plt.figure(figsize=(12,10))
        #ION
        if ion :
            plt.ion()
        #POINTS
        for pid, z in self.zones.items() : 
            plt = z.plot(plt, point=points, edges=edges)
        #LINES
        if lines :
            for lid, l in self.line.items() :
                plt = l.plot(plt, points=points, edges=edges)
        #POINTS_LOAD
        if points_load :
            charges = []
            for pt in self.points():
                charges.append(pt.charge(self.charge, ratio=1))
#            charges = charges / max(charges)
            for pt, charge in zip(self.points(), charges):
                plt.scatter(pt.X, pt.Y, c="black", alpha=charge)
        #EDGES LOAD
        if edges_load :
            MAX = 0 
            for c in self.charge.values():
                if c.modes(modes) > MAX : MAX = c.modes(modes)
            for (pt1, pt2), ch in self.charge.items() :
                    mil = (pt1 + pt2)  / 2
                    plt = mil.plot_edge(pt2, plt, alpha=(ch.modes(modes) / MAX), zorder=10)
        plt.legend()
        self.draw(plt)
        return plt
        
    def close_from(self, pairXY):
        for pt in self.map.nearest(Point(pairXY).bbox, num_results=1):
            return pt
    
    def time(self, pt1, pt2):
        #A cause du temps d'attente : il faut rendre le fait que faire un pt fixe coûte 0
        if pt1.pid == pt2.pid :
            return 0
        #Si on reste sur la même ligne mais qu'on change de station
        elif isinstance(pt1, Station) and isinstance(pt2, Station) and pt1.lid == pt2.lid:
            return pt1.dist(pt2) / self[pt1.lid].speed + self[pt1.lid].stop_time
        #Si on va à un quai = [enter the network, changement de ligne]
        elif isinstance(pt2, Station):
            pt = pt1
            s = pt2
            waiting_time = Network.waiting_factor / self[s.lid].f 
            return pt.dist(s) / Network.walking_speed + waiting_time
        #sinon on quitte le métro OU on marche : pas de différence
        else:
            return pt1.dist(pt2) / Network.walking_speed 
        
   
    ###
    ### WORK
    ###

        
    def load_flux(self, info=0, plt=None, edges=False, modes=["metro"]) :
        
        #Il faut toujorus reprendre à zéro
        self.printi(info*2, "Calculating shortest paths and choose transportation mode")
        t = module_time.time()
        self.path.shortest_paths2()
        t =str(round(module_time.time() - t))
        self.printi(info*4, "took "+t+" s")
        
        self.printi(info*2, "Loading flux on the network") #WAS 2s if no structure like charge
        t = module_time.time()
        #Calcule
        self.charge = dict()
        #INIT à 0 pour tout children
        for pt1 in self.points():
            for child in pt1.children:
                self.charge[pt1, child] = Charge(pt1, child)
        for (pt1, pt2), flux in self.flux.items() :
            if pt1.pid == pt2.pid : 
                continue
            for av, ap in self.path.pairs(pt1, pt2) :
                try :
                    self.charge[av, ap].add(pt1, pt2, flux, self.path.get_mode(pt1, pt2))
                except KeyError :
                    #Le pb vient que sir flux a pas les bonnes entrées
#                        print(pt1, pt2)
                    pass
                    
        t =str(round(module_time.time() - t))
        self.printi(info*4, "took "+t+" s")
        
        #Plot
        if edges :
            self.printi(info*2, "Plotting flux on the network")
            t = module_time.time()
            
            if plt == None :
                plt = self.plot(ion=0, lines=1, edges=0)
            self.plot(plt=plt, edges_load=1)
            
            t =str(round(module_time.time() - t))
            self.printi(info*4, "took "+t+" s")
        
        self.corrupted_charge = False
        
        return plt
        
    def get_load(self, obj, tot=1, mode=1, info=0):
#        obj = self[idx]
        if isinstance(obj, Line) :
            line = obj
            if tot :
                line_direct = Charge()
                line_indirect = Charge()
                for s in line.station.values() :
                    for c in s.children :
                        if not s.same_line(c) :
                            line_direct.merge(self.charge[c, s])
                            line_indirect.merge(self.charge[s, c])
                return line_direct, line_indirect
                
            else :
                #Sens direct
                direct = []
                for i in range(len(line) - 1) :
                    direct.append(self.charge[line[i], line[i+1]])
                #Sens indirect
                indirect = []
                for i in range(len(line) - 1, 0, -1) :
                    indirect.append(self.charge[line[i], line[i-1]])
                #Pour avoir le même sens de lecturey
                indirect.reverse()
                #Info
                if info > 0:
                    print("\nLine", line.lid, np.mean(direct), np.mean(indirect))
                    for sens in [direct, indirect] :
                        print(sens)
                        #Il faut
                        pyplot.plot(range(len(sens)), sens)
                    pyplot.title("Charge for line " + str(line.lid))
                    pyplot.show()
                    
                return direct, indirect
            
        if isinstance(obj, Point):
            pt = obj
            
            direct = [] #entrant
            indirect = [] #sortant
            for c in pt.children :
                direct.append(self.charge[c, pt])
                indirect.append(self.charge[pt, c])
                
            if tot :
                #Merge the answers
                rep_direct = Charge()
                rep_indirect = Charge()
                for charge in direct : rep_direct.merge(charge)
                for charge in indirect : rep_indirect.merge(charge)
                return rep_direct, rep_indirect

            else :
                return direct, indirect
            
    
    def no_network_time(self, pt1, pt2):
        return Network.parking_time + pt1.dist(pt2) / Network.no_network_speed
    
    def cost(self, info=0):
        """Présuppose qu'on a chargé les flux avant !!!!!!"""
        
        if info > 0 : 
            print("\nRecapitulatif des coûts et bénéfices")
            print("COUTS:")
        #Cost of lines
        line_costs = []
        for line in self.line.values():
            costs = line.costs()
            line_costs.append(costs)
            if info > 0 :
                print("Ligne :", line.lid, costs)
        
        #Apport
        if info > 0 :
            print("BENEFICES:")
            t = module_time.time()
        times = Charge()
        fluxs = Charge()
        without_time = 0
        without_flux = 0
        
        for (pt1, pt2), flux in self.flux.items() :
            time = self.path.get_time(pt1, pt2)
            mode = self.path.get_mode(pt1, pt2)
            times.subtot[mode] += time * flux
            fluxs.subtot[mode] += flux
            without_time += self.path.get_time(pt1, pt2, mode="no_network") * flux
            without_flux += flux
        
            
        if info > 0 :
            t =str(round(module_time.time() - t))
            self.printi(info*4, "took "+t+" s")
            print("Temps SANS :", round(without_time))
            print("Temps AVEC :", round(times.tot))
            for mode, time in times.subtot.items():
                print("\tdont", mode, " :", time)
            print("> Gains :", round(without_time - times.tot))
            print("\n")
            print("Utilisation SANS :", round(without_flux))
            print("Utilisation AVEC :", round(flux.tot))
            for mode, flux in fluxs.subtot.items():
                print("\tdont", mode, " :", flux)
            
        return times, fluxs
            
    ###
    ### MUTATIONS
    ###
    
    #bof efficace
    def m_center_stations(self, lid):
        for s in self[lid].station.values():
            pt = Point([0, 0])
            i = 0
            for c in s.children:
                charge = self.charge[s, c].tot + self.charge[c, s].tot
                pt = pt + c * charge
                i += charge
            s.X = pt.X / i
            s.Y = pt.Y / i
            
    def m_remove_station(self, info=0):
        p = []
        for s in self.stations.values():
            try :
                p.append(1 / s.charge(self.charge, tot=1))
            except KeyError :
                p.append(0)
                if not self.corrupted_charge :
                    print("You must reload the flux because charge lacks pts")
                    self.corrupted_charge = True
        p = p / np.sum(p)
        s = self[np.random.choice(list(self.stations), p=p)]
        self.printi(info*2, "removes"+str(s))
        self.remove_station(s)
             
    def m_add_station(self, info=0):
        #Determine where to put it
        p = []
        pts = []
        for pt in self.points():
            try :
                p.append(pt.charge(self.charge, modes=["no_network", "foot"], tot=1))
                pts.append(pt)
            except KeyError :
                if not self.corrupted_charge :
                    print("You must reload the flux because charge lacks pts")
                    self.corrupted_charge = True
        p = p / np.sum(p)
        pt = np.random.choice(pts, p=p)
        
        #Closest station :
        for sid in self.map_stations.nearest(pt.bbox, num_results=1):
#            print(sid)
            s1 = self[sid] 
            
        #determine whether add it or create a new line :
        p = min(Network.add_station_new_line, 
                Network.add_station_max_dist / pt.dist(s1))
        if np.random.random() < p :
            #where to introdu.lidce it ?
            d =  pt.dist(s1)
            s2 = s1
#            print(s2, "init with", d)
            for c in s1.children :
                #In fact for the previous and next ones
                if isinstance(c, Station) and c.lid == s1.lid:
                    if pt.dist(c) < d :
                        s2 = c
                        d = pt.dist(c)
#                        print(s2, "changed with", d)
            #we introduce just at the maximum where position
            where = max(s1.line.where[s1], s1.line.where[s2])
#            print("s1 was", s1.line.where[s1])
#            print("where", where)
            rep = self.add_station(pt, s1.line, where=where)
        else :
            rep = self.new_line(pts=[pt.pairXY()])
            
        return rep
        

