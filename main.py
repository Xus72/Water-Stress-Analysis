import cv2 as cv
from matplotlib import pyplot as plt
from pyhdf.SD import SD, SDC
import os
import numpy as np
import csv
from math import sin,pi,e

#Datos estacion meteorologicos
meteo_path = 'Data/Almonte.csv'

#LST MODIS AQUA
myda11_path = 'Data/MYDA11_LST/'

#LST MODIS TERRA
moda11_path = 'Data/MODA11_LST/'

albedo_path = 'Data/MCD43A3/'

meteo_data = list()
myda11_files = list()
moda11_files = list()
albedo_files = list()

#Lectura datos meteorologicos
with open(meteo_path,'r') as meteo_file:
    csv_reader = csv.reader(meteo_file, delimiter=';')
    meteo_data = [row for row in csv_reader]
    meteo_file.close()

#Carga datos LST MODIS AQUA
for root, dir, files in os.walk(myda11_path):
    myda11_files = [myda11_path + filenames for filenames in files]

#Ordenamos los ficheros de mayor a menor
myda11_files.sort()

#Carga datos LST MODIS TERRA
for root, dir, files in os.walk(moda11_path):
    moda11_files = [moda11_path + filenames for filenames in files]

for root, dir, files in os.walk(albedo_path):
    albedo_files = [albedo_path + filenames for filenames in files]

#Ordenamos los ficheros de mayor a menor
moda11_files.sort()

myda11_hdf = SD(myda11_files[0], SDC.READ)

moda11_hdf = SD(moda11_files[0], SDC.READ)

albedo_hdf = SD(albedo_files[1], SDC.READ)

myda11_lst_day = myda11_hdf.select('LST_Day_1km')[270:375,450:607]

myda11_day_time = myda11_hdf.select('Day_view_time')[270:375,450:607]

myda11_emis_31 = myda11_hdf.select('Emis_31')[270:375,450:607]

myda11_emis_32 = myda11_hdf.select('Emis_32')[270:375,450:607]

moda11_day_time = moda11_hdf.select('Day_view_time')[270:375,450:607]

moda11_lst_day = moda11_hdf.select('LST_Day_1km')[270:375,450:607]

moda11_emis_31 = moda11_hdf.select('Emis_31')[270:375,450:607]

moda11_emis_32 = moda11_hdf.select('Emis_32')[270:375,450:607]

bsa_albedo = albedo_hdf.select('Albedo_BSA_shortwave')[270:375,450:607]

wsa_albedo = albedo_hdf.select('Albedo_WSA_shortwave')[270:375,450:607]

def t_air(meteo_data,modis_overpass):
    tmax = meteo_data[0][2]
    hmax = meteo_data[0][3]
    tmin = meteo_data[0][4]
    hmin = meteo_data[0][5]
    N = 12
    d = 18 - float(hmax.replace(':','.'))
    c = 6 - float(hmin.replace(':','.'))
    t_air = np.zeros(modis_overpass.shape)
    for i in range(modis_overpass.shape[0]):
        for j in range(modis_overpass.shape[1]):
            modis_time = modis_overpass[i][j] * 0.1
            m = modis_time - (12 - (N/2) + c)
            t_air[i][j] = (float(tmax) - float(tmin))*sin((pi*m)/(N+2*d))
    return t_air

def r_In_Longwave_Radiation(t_air):
    sigma = 5.68e-18
    d = 7.77e-4
    c = 0.261
    r = np.zeros(t_air.shape)
    for i in range(t_air.shape[0]):
        for j in range(t_air.shape[1]):
            r[i][j] = sigma * ((t_air[i][j]+273.15)**4) * (1-(c*(e**(-d*(t_air[i][j]**2)))))
    return r

def r_Out_Longwave_Radiation(myda11_lst, myda11_emis_31, myda11_emis_32, moda11_lst, moda11_emis_31, moda11_emis_32):
    emis = np.zeros(myda11_emis_31.shape)
    lst = np.zeros(myda11_lst.shape)
    r = np.zeros(myda11_lst.shape)
    sigma = 5.68e-18
    for i in range(myda11_emis_31.shape[0]):
        for j in range(myda11_emis_31.shape[1]):
            if myda11_emis_31[i][j] == 0:
                emis_31 = moda11_emis_31[i][j] * 0.002
            else:
                emis_31 = myda11_emis_31[i][j] * 0.002
            if myda11_emis_32[i][j] == 0:
                emis_32 = moda11_emis_32[i][j] * 0.002
            else:
                emis_32 = myda11_emis_32[i][j] * 0.002
            emis[i][j] = np.mean([emis_31,emis_32])

    for i in range(myda11_lst.shape[0]):
        for j in range(myda11_lst.shape[1]):
            if myda11_lst[i][j] == 0:
                lst[i][j] = moda11_lst[i][j] * 0.02
            else:
                lst[i][j] = myda11_lst[i][j] * 0.02

    for i in range(r.shape[0]):
        for j in range(r.shape[1]):
            r[i][j] = -emis[i][j] * sigma * (lst[i][j]**4)

    return r

def daily_shortwave_radiation(meteo_data, bsa, wsa):
    r = np.zeros(bsa.shape)
    for i in range(bsa.shape[0]):
        for j in range(bsa.shape[1]):
            albedo = (0.8 * (bsa[i][j] * 0.001)) + (0.2 * (wsa[i][j] * 0.001))
            r[i][j] = float(meteo_data[-1][10]) * (1 - albedo)
    return r

def shortwave_radiation(daily_shortwave):
    t = 1
    N = 12
    r = np.zeros(daily_shortwave.shape)
    j = 2/(sin((pi*t)/N))
    for i in range(daily_shortwave.shape[0]):
        for z in range(daily_shortwave.shape[1]):
            r[i][z] = (daily_shortwave[i][z]/j)*(24/N)
    return r

t_aire = t_air(meteo_data[1:], myda11_day_time)
r_in = r_In_Longwave_Radiation(t_aire)
r_out = r_Out_Longwave_Radiation(myda11_lst_day,myda11_emis_31,myda11_emis_32,moda11_lst_day,moda11_emis_31,moda11_emis_32)
r_sa = daily_shortwave_radiation(meteo_data[1:], bsa_albedo, wsa_albedo)
r_short = shortwave_radiation(r_sa)



