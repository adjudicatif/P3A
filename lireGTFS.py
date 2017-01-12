# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 17:51:46 2017

@author: jean
"""

import pandas as pd
import os

root = "F:/Google Drive/Polytechnique/3A/P3A/DATA/RATP_GTFS_LINES/"
folders = os.listdir(root)
i = 0
for folder in folders:
#    if "BUS" not in folder :
    if "METRO" in folder:
        current_folder = root+folder+"/"
        #La route 
        routes = pd.read_csv(current_folder + "routes.txt", sep=",")
        
        #Les arrêts
        stops = pd.read_csv(current_folder + "stops.txt", 
                                 sep=",")
        stops_mean = stops.groupby("stop_name").mean()
        stops_mean.sort_values("stop_id")
        
        stops_mean["X"] = stops_mean["stop_lon"]
        stops_mean["Y"] = stops_mean["stop_lat"]
        
        origin_deg = { 'lon':2.337, 'lat':46.8} #Selon fichier sur R
        origin = {'X':600000, 'Y':2200000}
        for ax in origin :
            stops_mean[ax] = (stops_mean[ax]  - origin_deg[ax]) * 6371 * 3.1415 / 180
        i +=1 
        
        print(stops_mean.loc["Châtelet"])
        print(stops_mean.loc["Nation"])
        if i > 0 : break

    
