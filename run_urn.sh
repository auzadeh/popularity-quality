#!/bin/bash
#PBS -l nodes=1:ppn=16,walltime=00:58:00:00
#PBS -N collect1
#PBS -V
#PBS -m ae
#PBS -d /N/u/azadnema/Karst/popularity/
#PBS -q preempt
python urn.py

