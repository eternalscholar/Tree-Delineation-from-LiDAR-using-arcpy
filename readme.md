**Individual Tree Delineation with Street View Visualization**

**Synopsis: **The purpose of this project is to extract individual trees
crowns from input LAS file as a polygon shapefile, extract the locations
of each tree as a point shapefile, extract the images of the trees
through Google Street view API and display all of them on a map. Only
those tree crowns and tree locations which are on either sides of the
streets will be displayed on the map.


**Extended abstract:** The objective of this project is to create two
arcpy GUI tools for individual tree delineation from a LiDAR data file
(LAS file) and obtain the Google street view images of the trees so
delineated. The delineation is twin fold with individual tree canopy
extraction and individual tree location extraction. The first tool takes
a LAS data file as input and produces two vector layers, a polygon layer
representing tree canopy and a point layer representing tree locations.
These two files will be displayed on the map. The second tools takes the
point layer (tree locations) created by the first tool as input and
extracts Google street view images and their metadata and stores them
locally in the output folder location. Also, a new point layer will be
created that represents the locations where the street view images were
captured. For each location in this file, we would download 18 images
with different look angles (different pitch angles and heading angles).
This file will therefore have 18 fields in its attribute table
representing each of the different look angles and stores the
corresponding local drive link to the images within the cells of the
table. These images can be viewed in ArcGIS by enabling Hyperlinking to
an attribute within the point layer.

The canopy of trees are obtained with the help of applying watershed
delineation algorithm on inverted elevation model. The difference in
elevation between a Digital Surface Model (DSM) and Digital Elevation
Model (DEM) is called a Canopy Height Model (CHM). By inverting the CHM
and applying a watershed delineation algorithm, the canopy of trees
within the study area could be delineated. The location of the trees are
found with the help of Focal Statistics tool within ArcGIS. Street view
images were sourced from Google Street View Static API.

**Keywords: **LiDAR, Trees, Canopy, Google Street View, Canopy Height
Model (CHM)

**Mapping**: Three vector layers will be displayed on the map after
running both the tools. A polygon shapefile representing trees, a point
layer representing tree locations and another point layer representing
streetview locations. Mapping module is used in a separate script tool
to export screenshots.

