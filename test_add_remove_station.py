# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 16:25:54 2016

@author: jean
"""
import numpy as np
import pandas as pd
import time as time

from network import Network

root = 'F:/Google Drive/Polytechnique/3A/P3A/'

test = "test_add_remove_station"
name = "Paris_" + test
serie = "U" 



interval = [1, 100] #de n_stations
max_evals = 1
n_tests = 5  

space = {"nConsecutive":[1, 2, 3, 5, 10, 20, 30],
         "nCycle":[1, 2, 3]}

metro = pd.DataFrame(columns=["conf", "before", "during", "after"])

def rapport(n, conf, t, i):
    print("...")
    path = root + test + "/"  + serie + "_C"+str(conf) + "_T"+str(t) + "_S"+str(i)
    plt = n.plot(lines=1, ion=0)
    plt.savefig(path + ".png")
    plt.close()
    n.load_flux()
    with open(path + ".txt", "w") as file:
        file.write(str(i) + "\n")
        times, flux = n.cost(info=0)
        file.write("times : " + str(times) + "\n")
        file.write("flux : " + str(flux) + "\n")
        file.write("\n")
        
        for line in n.line.values():
            file.write(str(line.lid) + str(n.get_load(line, tot=1)) + "\n\n")
    print("SAVED", path[len(root):])
    
    return flux.subtot["metro"]
    

def objective(args):
    n_stations = args
    loss = 0
    std = 0
    MIN = np.inf
    MAX = 0
    t = time.time()
    
    for t in range(n_tests) :
        conf = (n_stations)
                
        n = Network.open_file(root + "DATA/Paris.ntwk")
        before = rapport(n, conf, t,  0)
        
        for i in range(n_stations):
            n.m_add_station()
        during = rapport(n, conf, t, 1)
                    
        for i in range(n_stations):
            n.m_remove_station()
        after = rapport(n, conf, t, 2)  
        
        metro.loc[len(metro)] = [conf, before, during, after]
        loss -= after
        std += (after - before)**2  
        MIN = min(MIN, after)
        MAX = max(MAX, after)
        
        
    return {'loss': loss / n_tests,
            'status': 0,
            'std': (std / n_tests)**0.5,
            'time': time.time() - t,
            'MIN': MIN,
            'MAX': MAX}
            
      
for n_stations in space :
    rep = objective(n_stations)
    print(rep['loss'])
    print(rep['std'])
    print(round(rep['time']))
      
#trials = hyperopt.Trials()
#best = hyperopt.fmin(objective,
#            space=(hyperopt.hp.qloguniform('n_stations', 
#                                 np.log(interval[0]), 
#                                 np.log(interval[1]), 
#                                 1)),
#            algo=hyperopt.tpe.suggest,
#            max_evals=max_evals,
#            trials=trials)


print(metro.describe().round())
ax = metro.plot(x="conf", y="before")
metro.boxplot(column="after", by="conf", ax=ax)
metro.to_csv(root + test + "/" + name + "_S" + serie + ".csv")


#rep = dict()

#def rapport(n, i):
#    global n
#    print("...")
#    path = root + test + "/"  + serie + "_"+str(i)
#    plt = n.plot(lines=1, ion=0)
#    plt.savefig(path + ".png" )
#    plt.close()
#    n.load_flux()
#    with open(path + ".txt", "w") as file :
#        file.write(str(i) + "\n")
#        times, flux = n.cost(info=0)
#        rep[3*s + i] = flux
#        file.write("times : " + str(times) + "\n")
#        file.write("flux : " + str(flux) + "\n")
#        file.write("\n")
#        
#        for line in n.line.values() :
#            file.write(str(line.lid) + str(n.get_load(line, tot=1)) + "\n\n")
#    print("SAVED", i)
#        
#n_series= 10  
# 
#n_stations = 20
#
#for s in range(n_series) :
#    serie = "T"  +str(s)
#    print("serie", serie, " / ", n_series)
#
#    
#            
#    
#    n = Network.open_file(root + "DATA/Paris.ntwk")
#    rapport(n, 0)
#    
#    for i in range(n_stations):
#        n.m_add_station()
#    rapport(n, 1)
#                
#    for i in range(n_stations):
#        n.m_remove_station()
#    rapport(n, 2)           
#    
#from paths import Charge
#import pandas as pd
#
#metro = pd.DataFrame(columns=["before", "during", "after"])
#for s in range(n_series):
#    metro.loc[s] = [rep[3*s + 0].subtot["metro"],
#                    rep[3*s + 1].subtot["metro"],
#                    rep[3*s + 2].subtot["metro"]]
#print(metro.describe().round())