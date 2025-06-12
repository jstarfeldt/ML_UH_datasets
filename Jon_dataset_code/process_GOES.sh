#!/bin/bash

# Wall time limit
#SBATCH -t 4:00:00

# Number of CPU nodes
#SBATCH -n 1

# Number of CPU cores
#SBATCH -c 30

# Memory per CPU core
#SBATCH --mem-per-cpu=512

#source /home/jonstar/scratch/condaroot/Miniforge3-24.11.3-2-Linux-x86_64.sh
#mamba activate heat
export PATH=/home/jonstar/scratch/condaroot/miniforge3-24.11.3/bin:$PATH
source activate heat

echo "First argument: $1"

cd /home/jonstar/ML_UH_datasets/Jon_dataset_code
python process_GOES.py --city=$1 --cpus=30
