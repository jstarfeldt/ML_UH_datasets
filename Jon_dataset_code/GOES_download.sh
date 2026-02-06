#!/bin/bash

# Wall time limit
#SBATCH -t 4:00:00

# Number of CPU nodes
#SBATCH -n 1

# Number of CPU cores
#SBATCH -c 30

# Memory per CPU core
#SBATCH --mem-per-cpu=512

#export PATH=/home/jonstar/scratch/condaroot/miniforge3-24.11.3/bin:$PATH
#source activate heat
~/scratch/conda-pack-unpacker.sh -f ~/scratch/heat.tar.gz
if [ $? -ne 0 ]; then
    echo "[ERROR] Error unpackaging ~/scratch/foo.tar.gz"
    exit 1
fi

echo "First argument: $1"

cd /home/jonstar/ML_UH_datasets/Jon_dataset_code
#/tmp/$USER/heat/bin/python GOES_download_new.py --city=$1 --n=25994 --startFile=0 --cpus=30
/tmp/$USER/heat/bin/python GOES_download_new.py --city=$1 --n=105120 --startFile=0 --cpus=32
#python GOES_download_new.py --city=$1 --n=5000 --startFile=5000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=10000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=15000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=20000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=25000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=30000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=35000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=40000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=45000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=50000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=55000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=60000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=65000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=70000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=75000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=80000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=85000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=90000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5000 --startFile=95000 --cpus=30
#python GOES_download_new.py --city=$1 --n=5120 --startFile=100000 --cpus=30
