import cv2 as cv
from matplotlib import pyplot as plt
from pyhdf.SD import SD, SDC
import os
import numpy as np
import csv
from math import sin,pi

#Datos estacion meteorologicos
meteo_path = 'Data/Almonte.csv'

#LST MODIS AQUA
myda11_path = 'Data/MYDA11_LST/'

#LST MODIS TERRA
moda11_path = 'Data/MODA11_LST/'

meteo_data = list()
myda11_files = list()
moda11_files = list()

#Lectura datos meteorologicos
with open(meteo_path,'r') as meteo_file:
    csv_reader = csv.reader(meteo_file, delimiter=';')
    meteo_data = [row for row in csv_reader]
    meteo_file.close()

#Carga datos LST MODIS AQUA
for root, dir, files in os.walk(myda11_path):
    myda11_files = [myda11_path + filenames for filenames in files]

#Ordenamos los ficheros de mayor a menor
myda11_files.sort(reverse=True)

#Carga datos LST MODIS TERRA
for root, dir, files in os.walk(moda11_path):
    moda11_files = [filenames for filenames in files]

#Ordenamos los ficheros de mayor a menor
moda11_files.sort(reverse=True)


