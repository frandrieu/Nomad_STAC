#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 16:14:09 2021

This code create a shapefile from a NOMAD LNO observation file (1 orbit) with all footprints :
    - polygone of boundaries for each observation Fov
    - point of middle FoV

Only for LNO at the moment
Only the footprint boundaries at the moment (no point geometry)

@author: Frederic Schmidt, GEOPS, UNiv. Paris-Saclay
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas
import pyproj
#### START MODIFICATIONS 01/03/24 !!!!
from shapely.geometry import Polygon, MultiPolygon
#### END MODIFICATIONS 01/03/24 !!!!
import rasterio
import h5py
import os as os






########################################################################################################
####### read the data

WORKING_DIRECTORY = "/Users/fandrieu/Documents/Nomad_STAC"
# filename = "20230203_035932_1p0a_LNO_1_DF_168" #Olympus
# filename = "20230124_234445_1p0a_LNO_1_DF_168" #Olympus, DP_189
# filename = "20221125_082524_1p0a_LNO_1_DF_190" #Olympus, DP_168
# filename = "20221116_042334_1p0a_LNO_1_DP_189" #Olympus, 168 and 189 no 190 !

# filename = "20230201_004835_1p0a_LNO_1_DF_168" #Ascraeus, DF_168
# filename = "20230124_213650_1p0a_LNO_1_DP_168" #Ascraeus, DF_189
#filename = "20211207_103950_1p0a_LNO_1_DP_168" #Arsia, only 168_DP (older) and 168_DF 
filename = "20230105_174515_1p0a_LNO_1_DP_168"
#20221121_060628_1p0a_LNO_1_DF_168
# filename = "20230123_220045_1p0a_LNO_1_DP_168" #Arsia, DF_189

# filename = "20230128_235852_1p0a_LNO_1_DF_189"# Pavonis, DP_168

order = filename[len(filename)-3:len(filename)]
filepath = os.path.normcase(WORKING_DIRECTORY+os.sep+filename+".h5")


#WORKING_DIRECTORY = "/Volumes/SERGE/BLANCO/NOMAD/"
#data_folders = ["hdf5_level_0p3a"]
#filenames = ["20161122_153906_LNO_D_169"]
#data_folder = "hdf5_level_1p0a"
#filename = "20181001_101614_1p0a_LNO_1_DP_190"


# year = filename[0:4]
# month = filename[4:6]
# day = filename[6:8]
# order = filename[len(filename)-3:len(filename)]
# filepath = os.path.normcase(WORKING_DIRECTORY+os.sep+data_folder+os.sep+year+os.sep+month+os.sep+day+os.sep+filename+".h5")
                        
h5f = h5py.File(filepath, "r") #open file


# global parameters
ls = h5f['Geometry/LSubS'][:] #Season Ls
#ptimestamp = h5f['Timestamp'][:] #longitutde
ptime = h5f['Geometry/ObservationDateTime'][:] #observation time


# central point of instananeous FoV
latp0 = h5f['Geometry/Point0/Lat'][:] #latitude
lonp0 = h5f['Geometry/Point0/Lon'][:] #longitutde
incp0 = h5f['Geometry/Point0/IncidenceAngle'][:] #Incidence angle
emep0 = h5f['Geometry/Point0/EmissionAngle'][:] #Emergence angle
phap0 = h5f['Geometry/Point0/PhaseAngle'][:] #Phase angle
lstp0 = h5f['Geometry/Point0/LST'][:] #local solar time
losp0 = h5f['Geometry/Point0/LOSAngle'][:] #Line of Sigth angle


# 4 corner points of instananeous FoV
latp1 = h5f['Geometry/Point1/Lat'][:] #latitude
lonp1 = h5f['Geometry/Point1/Lon'][:] #longitutde

latp2 = h5f['Geometry/Point2/Lat'][:] #latitude
lonp2 = h5f['Geometry/Point2/Lon'][:] #longitutde

latp3 = h5f['Geometry/Point3/Lat'][:] #latitude
lonp3 = h5f['Geometry/Point3/Lon'][:] #longitutde

latp4 = h5f['Geometry/Point4/Lat'][:] #latitude
lonp4 = h5f['Geometry/Point4/Lon'][:] #longitutde


# nb of observation
[nb_footprint, nb_time]= np.shape(latp0)


########################################################################################################
############# create the convex hull for a footprint

polygon_all_footprint = list()
filenames_all = list()
convexhullcentroid_lat_all = list()
convexhullcentroid_lon_all = list()
order_all = list()

for footpos in range(0, nb_footprint):

    #### create a geopandas GeoDataFrame with all corner points
    #namvector = np.linspace(1,4*2,4*2).astype('str')
    
    namvector = np.linspace(1,4*2,4*2).astype('str')
        
    latvector = np.ravel(np.array([latp4[footpos,:], latp1[footpos,:], latp2[footpos,:], latp3[footpos,:]]))
    lonvector = np.ravel(np.array([lonp4[footpos,:], lonp1[footpos,:], lonp2[footpos,:], lonp3[footpos,:]]))
    
#### START MODIFICATIONS 01/03/24 !!!!
    if (np.min(lonvector) < -170.) and (np.max(lonvector) > 170. ):
       lonvector1=lonvector[np.where(lonvector < 0.)]
       lonvector2=lonvector[np.where(lonvector > 0.)]
       latvector1=latvector[np.where(lonvector < 0.)]
       latvector2=latvector[np.where(lonvector > 0.)]
       y1 = latvector1[0] + ((180.-lonvector1[0]) * (latvector2[0] - latvector1[0])) / (lonvector2[0]+180. - lonvector1[0])
       y2 = latvector1[1] + ((180.-lonvector1[1]) * (latvector2[1] - latvector1[1])) / (lonvector2[1]+180. - lonvector1[1])
       newlatvector1=np.append(latvector1, [y1, y2])
       newlonvector1=np.append(lonvector1, [-180., -180.])
       newlatvector2=np.append(latvector2, [y1, y2])
       newlonvector2=np.append(lonvector2, [180., 180.])
       nv1=np.linspace(1,len(newlatvector1),len(newlatvector1)).astype('str')
       df1 = pd.DataFrame(
           {'Point': nv1,
            'Latitude': newlatvector1,
            'Longitude': newlonvector1})
       
       gdf1 = geopandas.GeoDataFrame(
           df1, geometry=geopandas.points_from_xy(df1.Longitude, df1.Latitude))
       
       #Define the CRS (planet Mars)
       gdf1.crs = pyproj.CRS('+proj=longlat +a=3396190 +b=3376200')
       
       
       convexhull1 = gdf1.unary_union.convex_hull
       
       convexhull1bound = convexhull1.boundary.coords.xy #get the convexhull of the boundaries
       convexhull1centroid = convexhull1.centroid.coords.xy #get the center of the convexhull
       
       nbcorner1 = len(convexhull1bound[0])
       shape_footprint1=list()
       for i in  range(0,nbcorner1):
           shape_footprint1.append( (convexhull1bound[0][i], convexhull1bound[1][i]) )
       nv2=np.linspace(1,len(newlatvector2),len(newlatvector2)).astype('str')   
       df2 = pd.DataFrame(
           {'Point': nv2,
            'Latitude': newlatvector2,
            'Longitude': newlonvector2})
       gdf2 = geopandas.GeoDataFrame(
           df2, geometry=geopandas.points_from_xy(df2.Longitude, df2.Latitude))
       
       #Define the CRS (planet Mars)
       gdf2.crs = pyproj.CRS('+proj=longlat +a=3396190 +b=3376200')
       
       
       convexhull2 = gdf2.unary_union.convex_hull
       
       convexhull2bound = convexhull2.boundary.coords.xy #get the convexhull of the boundaries
       convexhull2centroid = convexhull2.centroid.coords.xy #get the center of the convexhull
       
       nbcorner2 = len(convexhull2bound[0])
       shape_footprint2=list()
       for i in  range(0,nbcorner2):
           shape_footprint2.append( (convexhull2bound[0][i], convexhull2bound[1][i]) )
           
       polygon_all_footprint.append(MultiPolygon([Polygon(shape_footprint1), Polygon(shape_footprint2)]))
       filenames_all.append(filename)
       convexhullcentroid_lat_all.append(np.mean([convexhull1centroid[1][0], convexhull2centroid[1][0]])) 
       centrolon=np.mean([convexhull1centroid[0][0]+360, convexhull2centroid[0][0]])
       if centrolon > 180.: centrolon=centrolon-360.
       convexhullcentroid_lon_all.append(centrolon)
       order_all.append( int(order) )
    else:
        df = pd.DataFrame(
            {'Point': namvector,
             'Latitude': latvector,
             'Longitude': lonvector})
        
        #create a geopandas GeoDataFrame with an associated point in corresponding lat/long
        
             
        gdf = geopandas.GeoDataFrame(
            df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
        
        #Define the CRS (planet Mars)
        gdf.crs = pyproj.CRS('+proj=longlat +a=3396190 +b=3376200')
        
        
        convexhull = gdf.unary_union.convex_hull
        
        convexhullbound = convexhull.boundary.coords.xy #get the convexhull of the boundaries
        convexhullcentroid = convexhull.centroid.coords.xy #get the center of the convexhull
        
        nbcorner = len(convexhullbound[0])
        shape_footprint=list()
        for i in  range(0,nbcorner):
            shape_footprint.append( (convexhullbound[0][i], convexhullbound[1][i]) )
            
        polygon_all_footprint.append(Polygon(shape_footprint))
        filenames_all.append(filename)
        convexhullcentroid_lat_all.append(convexhullcentroid[1][0]) 
        convexhullcentroid_lon_all.append(convexhullcentroid[0][0])
        order_all.append( int(order) )
 
        
#####END MODIFICATIONS 01/03/24 !!!!
    
# generate average global values
mean_ls =  np.mean(ls, axis=1)
mean_inc = np.mean(incp0, axis=1)
mean_eme = np.mean(emep0, axis=1)
mean_pha = np.mean(phap0, axis=1)
mean_lst = np.mean(lstp0, axis=1)
mean_los = np.mean(losp0, axis=1)

footprintid = np.linspace(0,nb_footprint-1,nb_footprint).astype('int')


# create a Geodata with all polygones 
polysall = geopandas.GeoSeries( polygon_all_footprint )
gdfall = geopandas.GeoDataFrame({'geometry': polysall, 'Order':order_all, 'filename':filenames_all, 'Spectra_nb':footprintid, 
                                 'Incidence':mean_inc, 'Emergence':mean_eme, 'Phase':mean_pha, 
                                 'Local_sol_time':mean_lst, 'LOS':mean_los, 'Ls':mean_ls, 
                                 'Centroid_lat':convexhullcentroid_lat_all, 'Centroid_long':convexhullcentroid_lon_all,                 
                                 'Start_time':ptime[:,0].astype('str'), 'Stop_time':ptime[:,1].astype('str') })

gdfall.crs = pyproj.CRS('+proj=longlat +a=3396190 +b=3376200')


#save as a shape file
gdfall.to_file(WORKING_DIRECTORY+os.sep+filename+".shp")

#save as GeoJSON
gdfall.to_file(WORKING_DIRECTORY+os.sep+filename+"_1.geojson", driver='GeoJSON')


#### plot the results
fig, ax = plt.subplots(figsize=(15, 15))
gdfall.plot(ax=ax, alpha=0.4)
plt.plot( convexhullcentroid_lon_all, convexhullcentroid_lat_all , '.g') 
plt.title(filename)
plt.xlabel("Longitude (°)")
plt.ylabel("Latitude (°)")
plt.show()

