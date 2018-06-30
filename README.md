# tims-civ

Each folder contains the data of simulations made with 20 cities, 30 cities ... , 80 cities , and the following files:

civniu.py -> Main simulation program (Read comments in the file)

miscript.sh -> Bash script to run many instances of niuciv sequentially, and store their results on txt files

analysis.py -> Python script that reads the txt output files, calculates the mean and standard deviation of the parameters and stores them on the file MEANS and STDEV


In the directory:

graficar.py -> Python script that reads the files MEANS and STDEV of each folder, and draws the graphics
