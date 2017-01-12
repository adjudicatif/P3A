# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 22:24:35 2016

@author: jean
"""
from heapq import heappush, heappop
import time as module_time
import numpy as np
from point import Point, Station, Zone
from line import Line

class Charge(object):
    def __init__(self, pt1=None, pt2=None):
        object.__init__(self)
        self.pt1 = pt1
        self.pt2 = pt2
        self.tot = 0
        self.subtot = {"metro":0, "foot":0,"no_network":0}
#        self.charge = dict()
#        self.mode = dict()
        
    def __repr__(self):
        rep = " "
        for mode, flux in self.subtot.items():
            rep += " " + mode + ":" + str(round(flux))
        return rep
        
    def __gt__(self, c):
        return self.tot > c.tot
    def __truediv__(self, r):
        self.tot = self.tot / r
        for mode in self.subtot :
            self.subtot[mode] = self.subtot[mode] / r
        return self
        
    def add(self, pt1, pt2, flux, mode):
        self.tot += flux
        self.subtot[mode] += flux
#        self.charge[pt1, pt2] = flux
#        self.mode[pt1, pt2] = mode
        
    def merge(self, c):
        self.tot += c.tot
        for mode in self.subtot :
            self.subtot[mode] += c.subtot[mode]
            
    def modes(self, modes):
        tot = 0
        for mode in modes :
            tot += self.subtot[mode]
        return tot
        
class Path(object):
    def __init__(self, network):
        object.__init__(self)
        self.N = network
        self.by = dict()
        self.by_no_network = dict()#for shortest paths
        self.time_no_network = dict()
        self.time = dict()
        self.mode = dict() #metro, foot, no_network
        #INIT by_no_network :
        self.shortest_paths2(without_metro=True)
        #DEPRECATED
        self.paths = dict() #for shortest paths      

    
    def pairs(self, pt1, pt2):
        if self.get_mode(pt1, pt2) == "metro" :
            by = self.by
        else:
            by = self.by_no_network
        av = pt1
        ap = by[pt1, pt2]
        while av.pid != pt2.pid :
            yield av, ap
            ap = by[ap, pt2]
            av = by[av, pt2]
    
    def get_time(self, pt1, pt2, mode=None):
        if mode == "no_network" :
            return min(self.time_no_network[pt1, pt2],
                       self.N.no_network_time(pt1, pt2))
        else :
            if self.get_mode(pt1, pt2) == "metro" :
                return self.time[pt1, pt2]
            elif self.get_mode(pt1, pt2) == "foot" :
                return self.time_no_network[pt1, pt2]
            elif self.get_mode(pt1, pt2) == "no_network" :
                return self.N.no_network_time(pt1, pt2)
    
    def get_mode(self, pt1, pt2):
        if (pt1, pt2) not in self.mode : 
            self.mode[pt1, pt2] = "no_network"
        return self.mode[pt1, pt2]
        
    def update_mode(self, pt1, pt2, time, without_metro=False):
        #assert self.time[pt1, pt2] est défini
        #get_time APPEL get_mode QUI définit un mode au passage
        if time < self.N.no_network_time(pt1, pt2):
            #On a tous le sby entr pt1 et pt2 si on fait la requête !
            if (not without_metro) and self.use_metro(pt1, pt2):
                self.mode[pt1, pt2] = "metro"
            else :
                self.mode[pt1, pt2] = "foot"
        else:
            self.mode[pt1, pt2] = "no_network"
    
    def use_metro(self, pt1, pt2):
        if pt1.pid == pt2.pid :
            return False
        else :
        #Attention, utiliser by car on doit absolument utiliser celui là
            return isinstance(pt1, Station) or isinstance(pt2, Station) or self.use_metro(self.by[pt1, pt2], pt2)
    
    def shortest_path(self, o, d, plt=None, route=False, info=0):
        self.N.printi(info*2, "Shortest path")
        if len(self.by) == 0 :
            self.N.printi(info*2, "Calcule all shortest paths")
            self.shortest_paths2()
            
        path = [o]
        times = []
        use_metro = False
        #On a qu'à remonter la piste
        for pt1, pt2 in self.pairs(o, d):
            times.append(self.N.time(pt1, pt2))
            path.append(pt2)
        #Plotter
        if route :
            plt = self.N.plot(points=1, lines=1, ion=1)
            plt.scatter(o.X, o.Y, marker='o', color='blue')#, ms=3)
            plt.scatter(d.X, d.Y, marker='x', color='blue')#, ms=3)
            X,Y = Point.set_to_plot(path)
            plt.plot(X,Y, ':', color='blue', lw=3, label="all paths method")
            self.N.draw(plt)
        return path, times, use_metro
        
    def shortest_paths2(self, info=0, without_metro=False, plt=None, situation=False, edges=False):
        self.N.printi(info*2, "Shortests paths 2")
        #Appel ini
        if without_metro :
            self.N.printi(info, "Init by_no_network")
            time = self.time_no_network
            by = self.by_no_network
        #Si appel mais pas de ligne : inutile de refaire le taff
        elif len(self.N.line) == 0 and self.by_no_network != None :
            self.N.printi(info, "Pas de ligne et déjà init")
            return 
        else:
            self.N.printi(info, "Resettle paths")
            time = self.time
            by = self.by
        #Pour chaque pt comme destination !!!
        #ON IVNERSE L4ORDRE !!!
        for d in self.N.points():
            self.N.printi(info*4, d)
            to_visit = []
            visited = dict()
            
            if situation:  
                plt = self.N.plot()
#                    plt = self.N.plot(points=1, ion=1) 
                plt.scatter(d.X, d.Y, marker='x', color='blue', zorder=10)#, ms=3)
                self.N.draw(plt)
            
            heappush(to_visit, (self.N.time(d, d), [d, d]))
            i = 0
            #astuce pour éviter d'avoir à finir les to_visit ET bakcup au 
            while len(visited) < len(self.N.stations) + len(self.N.zones) and len(to_visit) > 0:
                #On récupère le point le plus près
                time_current, [pt_current, parent_current] = heappop(to_visit)
                #SI on est pas déjà passé
                if not pt_current in visited.keys() :
                    #AJOUT
                    self.N.printi(info*8, str(pt_current) + " > "+str(d)+" by " + str(parent_current))
                    by[pt_current, d] = parent_current
                    time[pt_current, d] = time_current
                    self.update_mode(pt_current, d, time_current, without_metro=without_metro)
                    #On le note comme visité avec la mention "+ proche" du coup
                    visited[pt_current] = [parent_current, self.N.time(pt_current, parent_current)]
                    #On plotte pour que ce soit dessus
                    if situation :
                        plt.scatter(pt_current.X, pt_current.Y, marker='x', color="black", zorder=2)
                        i += 1
                        plt.title(str(i))
                        if edges :
                            plt.plot([parent_current.X, pt_current.X],
                                     [parent_current.Y, pt_current.Y], color="black", alpha=0.5, zorder=2)
                        self.N.draw(plt)
                    #Pour chaque enfant
                    for pt_child in pt_current.children:
                        # on l'ajoute à la liste, le filtre sur les déjà vus est plus haut
                        #Si on fait qu'avec les cars, on élimine du trajet les stations
                        #NB On inverse le sens du time !!!!!         v : ici on revient      v : le parent est pt_current
                        heappush(to_visit, (time_current + self.N.time(pt_child, pt_current), [pt_child, pt_current]))
                        if situation :
                            plt.scatter(pt_child.X, pt_child.Y, marker='o', color="red", alpha=1, zorder=1)
            if situation :
                plt.show()
                            
        return plt
        
        #!!!!!!!!DEPRECATED!!!!!!!!!!!
#    def shortest_paths(self, plt=None, info=0, situation=False):
#        if len(self.N.line) == 0 :
#            without_metro = True
#        if without_metro :
#            self.N.printi(info*4, "by car")
#            self.by_car = dict()
#            by = self.by_car()
#        else :
#            self.by = dict()
#            by = self.by
#            
#        t = module_time.time()
#        self.N.printi(info, "Calculating all shortest paths")
#        #Création de la matrice d'adjacence
#        self.paths = dict()
#        t = module_time.time()
#        for pt1 in self.N.points():
#            #Par défaut +oo
#            for pt2 in self.N.points():
#                self.paths[pt1, pt2] = np.inf
#            #Sauf pour les arcs directs !!
#            for child in pt1.children:
#                self.paths[pt1, child] = self.time(pt1, child)
#                by[pt1, child] = child
##        Calcul
##        print("INIT :", module_time.time() - t)
#        
#        t = module_time.time()
#        for pivot in self.N.points():
#            for pt1 in self.N.points():
#                for pt2 in self.N.points():
#                    if self.paths[pt1, pivot] + self.paths[pivot, pt2] < self.paths[pt1, pt2] :
#                        self.paths[pt1, pt2] = self.paths[pt1, pivot] + self.paths[pivot, pt2]
#                        by[pt1, pt2] = by[pt1, pivot]
#                        if pt1.pid == pivot.pid or pt2.pid == pivot.pid :
#                            print("UPDATED EVEN IF WAS A PIVOT")
##        print("SINGLE PROCESS", module_time.time() - t)
#        t = str(round(module_time.time() - t))
#        self.printi(info*2, "took "+t+" s")
        
    def single_shortest_path(self, o, d, plt=None, route=False, search=False, edges=False):
        to_visit = []
        visited = dict()
        
        if route:  
            plt.scatter(o.X, o.Y, marker='o', color='blue', zorder=10)#, ms=3)
            plt.scatter(d.X, d.Y, marker='x', color='blue', zorder=10)#, ms=3)
        
        heappush(to_visit, (self.N.time(o, o), [o, o]))
        i = 0
        while len(to_visit) > 0:
            #On récupère le point le plus près
            time_current, [pt_current, parent_current] = heappop(to_visit)
            #SI on est pas déjà passé
            if not pt_current in visited.keys() :
                #On le note comme visité avec la mention "+ proche" du coup
                visited[pt_current] = [parent_current, self.N.time(parent_current, pt_current)]
                #On plotte pour que ce soit dessus
                if search :
                    plt.scatter(pt_current.X, pt_current.Y, marker='x', color="black", zorder=2)
                    i += 1
                    plt.title(str(i))
                    self.N.draw(plt)
                    if edges :
                        plt.plot([parent_current.X, pt_current.X],
                                 [parent_current.Y, pt_current.Y], color="black", alpha=0.5, zorder=2)
                #Si c'est l'arrrivée : stop
                if pt_current.pid == d.pid :
                    break
                #Sinon on ajoute les sommets qu'il atteint
                else :
                    #Pour chaque enfant
                    for pt_child in pt_current.children:
                        # on l'ajoute à la liste, le filtre sur les déjà vus est plus haut
                        heappush(to_visit, (time_current + self.N.time(pt_current, pt_child), [pt_child, pt_current]))
                        if search :
                            plt.scatter(pt_child.X, pt_child.Y, marker='o', color="red", alpha=1, zorder=1)
                            if edges :
                                #Que si on est sur la fin à contacter la destination
                                if pt_child.pid == d.pid :
                                    print("from ", pt_current, "reached in total = ", time_current + self.N.time(pt_current, pt_child),)
                                    plt.plot([pt_child.X, pt_current.X],
                                             [pt_child.Y, pt_current.Y], color="red", alpha=0.5, zorder=1)
                        

       #On remonte le fil
        path = []
        ptr = d
        while ptr.pid != o.pid :
            path.append(ptr)
            [ptr, time] = visited[ptr]
        path.append(o)
        path.reverse()
        #On recalcule le temps en remontant le chemin
        times = []
        prec = o
        for suiv in path:
            if suiv.pid == o.pid: continue #vire o du listing
            times.append(self.N.time(prec, suiv))
            prec = suiv
        if route :
            X,Y = Point.set_to_plot(path)
            plt.plot(X,Y, '--', color='red', lw=3, label="single path method")
            self.N.draw(plt)
        return path, times
