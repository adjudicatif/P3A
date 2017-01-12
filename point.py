# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 20:35:26 2016

@author: jean
"""
#%%
### Point
###
class Point(object):
    def __init__(self, pairXY):
        self.X = pairXY[0]
        self.Y = pairXY[1]
        
        self.pid = -1
        self.children = set()#dict()
        
    def __mul__(self, a):
        return Point([self.X * a, self.Y * a])
    def __add__(self, pt):
        return Point([self.X + pt.X, self.Y + pt.Y])
    def __sub__(self, pt):
        return Point([self.X - pt.X, self.Y - pt.Y])
    def __lt__(self, pt):
        return self.X < pt.X or self.Y < pt.Y
    def __truediv__(self, D):
        return Point([self.X / D, self.Y / D])
        
    def __setstate__(self, dict_attr):
        self.__dict__ = dict_attr
    def __getstate__(self):
        return self.__dict__     
        
    def __getattr__(self, attr):
#        print(self, " and tries to reach", attr)
        if attr == "bbox": 
            return (self.X, self.Y, self.X, self.Y)
    def __repr__(self):
        return "["+str(self.X)+", "+str(self.Y)+"]"
    def __str__(self)   :
        return self.__repr__()
        
    def pairXY(self):
        return [self.X, self.Y]
    
    def is_linked(self, pt):
        return self in pt.children and pt in self.children
    def link(self, pt):
        #Eviter tout doublon
#        if not self.is_linked(pt):
        self.children.add(pt)
        pt.children.add(self)
    def unlink(self, pt):
#        while self.is_linked(pt):
        try : self.children.remove(pt)
        except KeyError : pass#Si déjà supprimé quoi
        try : pt.children.remove(self)
        except KeyError : pass
        
    def pt(self):
        return [self.X, self.Y]

    def dist(self, pt):
        return ((self.X - pt.X)**2 + (self.Y - pt.Y)**2)**0.5
    
    def bbox_square(self, d):
        return (self.X - d, self.Y - d, self.X  + d, self.Y + d)
    
    def plot_edge(self, pt, plt, color="Black", alpha=1, zorder=10):
        X = [self.X, pt.X]
        Y = [self.Y, pt.Y]
        plt.plot(X, Y, color=color, alpha=alpha, zorder=zorder)
        return plt
        
        
    def set_to_plot(pts):
        X = []
        Y = []
        for pt in pts : 
            X.append(pt.X)
            Y.append(pt.Y)
        return X, Y
        
        
    def charge(self, charge, modes=None, ratio=0, tot=0):
        E= 0.000001
        subtot = {"metro":E, "foot":E,"no_network":E}
        if modes == None :
            modes = subtot.keys()
        for c in self.children :
            for mode in modes:
                subtot[mode] += charge[self, c].subtot[mode]
                subtot[mode] += charge[c, self].subtot[mode]
        if ratio : 
            return subtot["no_network"] / sum(subtot.values())
            return (subtot["no_network"]) / (subtot["metro"] + subtot["no_network"])
        elif tot :
            return sum(subtot.values())
        return subtot

            
class Zone(Point):
    def __init__(self, pt, pid):
        Point.__init__(self, [pt.X, pt.Y])
        self.pid = pid
        self.children = set() #dict()#[pid] [[station, time]]
        
    def plot(self, plt, marker='+', color="grey", point=True, edges=False, alpha=1):
        if point :
            plt.scatter(self.X, self.Y, marker=marker, color=color)
        if edges :
            for s in self.children :
                plt = self.plot_edge(s, plt, color="grey", alpha=alpha)
        return plt
    
    def __repr__(self):
        return "Z-"+str(self.pid)#+" in ["+str(round(self.X,3))+", "+str(round(self.Y,3))+"]"
        
class Station(Point):
    def __init__(self, pt, pid, line):
        Point.__init__(self, [pt.X, pt.Y])
        self.pid = pid
        self.lid = line.lid
        self.line = line
        
        self.children = set()#dict() #[pid] DEPRECATED : [[station, time]]
    def plot(self, plt, marker='o', color="red", point=True, edges=False, alpha=1, zorder=0):
        if point :        
            plt.scatter(self.X, self.Y, marker=marker, color=color, zorder=0)
        if edges :
            for s in self.children :
                if s.lid != self.lid :
                    plt = self.plot_edge(s, plt, alpha=alpha)
        return plt
    
    def __repr__(self):
        return "S-"+str(self.pid)+"/L-"+str(self.line.lid)#+"["+str(round(self.X,3))+", "+str(round(self.Y,3))+"]"
        
    def same_line(self, s):
        return isinstance(s, Station) and self.line.lid == s.line.lid
