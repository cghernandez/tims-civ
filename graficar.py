import matplotlib.pyplot as plt
import numpy as np
import os

#Lists all directories 

directorios = os.listdir()
directorios.remove("graficar.py")
directorios = sorted(directorios,
        key = lambda x: int(x),
        reverse = False)

#Empty lists that will be filled with data

indx = []

m_maxpop    = []
m_fails     = []
m_meanpop   = []
s_maxpop    = []
s_fails     = []
s_meanpop   = []

for carpeta in directorios:

    with open(carpeta + "/MEANS","r") as archivo:
        archivo.readline()
        archivo.readline()
        archivo.readline()

        m_maxpop.append(float(archivo.readline()))
        m_fails.append(float(archivo.readline()))
        m_meanpop.append(float(archivo.readline()))

    with open(carpeta + "/STDEVS","r") as archivo:
        archivo.readline()
        archivo.readline()
        archivo.readline()

        s_maxpop.append(float(archivo.readline()))
        s_fails.append(float(archivo.readline()))
        s_meanpop.append(float(archivo.readline()))

    indx.append(carpeta)

plt.title("Mean final population vs number of cities")
plt.xlabel("Number of cities")
plt.ylabel("Mean final population")

plt.plot(indx,m_maxpop,"ro")
plt.show()

plt.title("Mean city failures vs number of cities")
plt.xlabel("Number of cities")
plt.ylabel("Mean city failures")

plt.plot(indx,m_fails, "ro")
plt.show()

plt.title("Mean population per city vs number of cities")
plt.xlabel("Number of cities")
plt.ylabel("Mean population per city")

plt.plot(indx,m_meanpop, "ro")
plt.show()

plt.title("Standard deviation of final population vs number of cities")
plt.xlabel("Number of cities")
plt.ylabel("Standard deviation of final population")

plt.plot(indx,s_maxpop, "ro")
plt.show()

plt.title("Standard deviation of city failures vs number of cities")
plt.xlabel("Number of cities")
plt.ylabel("Standard deviation of city failures")

plt.plot(indx,s_fails, "ro")
plt.show()

plt.title("Standard deviation of population per city vs number of cities")
plt.xlabel("Number of cities")
plt.ylabel("Standard deviation of population per city")

plt.plot(indx,s_meanpop, "ro")
plt.show()


