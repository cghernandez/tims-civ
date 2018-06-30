import os
import pandas as pd

#THIS FILE STORES EACH SIMULATION'S OUTPUT IN A PANDAS DATAFRAME,
#TO EXTRACT MEAN AND STANDARD DEVIATION

archivos = os.listdir()
archivos.remove("WORLDMAP.txt")

cuenta = 0

for archivo in archivos:
    
    if archivo.endswith(".txt"):
        
        if cuenta == 0:
            df = pd.read_csv(archivo, header = None, index_col = 0)
            df = df.transpose()
            cuenta += 1


        else:
            dfniu = pd.read_csv(archivo, header = None, index_col = 0)
            dfniu = dfniu.transpose()

            df = df.append(dfniu, ignore_index = True)

proms = df.mean()
desv = df.std()

with open("MEANS","w") as archivo:

    for i in proms:
        archivo.write(str(i) + "\n")

with open("STDEVS","w") as archivo:

    for i in desv:
        archivo.write(str(i) + "\n")
