# Urban Heat MiniCubes: An AI-Ready Dataset for Urban Heat Research

## Overview
Urban heat is amplified by impermeable surfaces and heterogeneous built environments, yet street-level variability remains difficult to quantify because multi-sensor observations are rarely available in consistent, analysis-ready form at the necessary spatiotemporal scales. We present "Urban Heat MiniCubes", a publicly available, FAIR-oriented dataset designed for machine learning applications in urban heat research. The dataset provides harmonized $90\times90$ km gridded data cubes for 48 cities in the Western Hemisphere spanning 2022-2023, with variables reprojected and collocated to a common grid to reduce preprocessing (e.g., reprojection, resampling, and spatiotemporal alignment). Urban Heat MiniCubes includes two complementary modalities: (i) higher-spatial-resolution, lower-frequency observations from Landsat 8/9 (e.g., surface reflectances) and Sentinel-1 (e.g., synthetic aperture radar backscatter), and (ii) higher-temporal-frequency, coarser observations from GOES-R (e.g., longwave infrared brightness temperatures) and a microwave land surface temperature product.

## What you will find in this repository
* Code to download and process the data in the dataset
* Code to reproduce figures found in the preprint
* Yaml files to create the necessary conda environments

## Data sources and processing
Urban Heat MiniCubes is comprised of remotely sensed data from a number of satellites, including Landsat 8/9, Sentinel-1, and GOES-16/17/18. The code in this repository shows how to download data from these satellites from Google Earth Engine. These data are also publicly available online. 
