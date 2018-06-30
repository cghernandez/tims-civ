#!/bin/bash 

for i in $(seq 31 100); do 
	echo $i
	python civniu.py 70 20 >> $i.txt

done
