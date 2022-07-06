**Individual Tree Delineation with Street View Visualization**

**Synopsis: **The purpose of this project is to extract individual trees
crowns from input LAS file as a polygon shapefile, extract the locations
of each tree as a point shapefile, extract the images of the trees
through Google Street view API and display all of them on a map. Only
those tree crowns and tree locations which are on either sides of the
streets will be displayed on the map.

![](media/image1.jpeg){width="7.061805555555556in"
height="4.833333333333333in"}

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

**Pseudocode:**

***Tool1:***

GET LAS data file\
GET Output Location\
GET Inverted Building footprint file\
GET spatial resolution for elevation models\
GET Road network file\
GET API key for Google Street View

FUNC LAStoTreeCanopyPolygons(input LAS File, output Location,
resolution, inverted building Footprint file)\
FUNC createCHM (input LAS File, output Location, resolution)

FUNC createElevationModels(LasFiles, output Location, resolution) CREATE
Las Dataset from LAS file\
CREATE Las Dataset layer from the Las Dataset created above\
CREATE DSM using the Las Dataset layer created above\
CREATE DEM using the Las Dataset layer created above

> END FUNC
>
> CALCULATE DSM - DEM

END FUNC

FUNC removeBuildings(output Location, input CHM, inverted building
Footprint file)\
CALL Clip tool on the input CHM with the inverted building footprint
file\
END FUNC

> CALL Fill tool\
> CALL Flow Direction tool\
> CALL Basin tool\
> CALL Raster to Polygon tool

END FUNC

FUNC TreeLocations ()

CALL Focal Statistics tool on CHM created by LAStoTreeCanopyPolygons
function.\
CALL Raster to Points tool

END FUNC

***Tool2:***

GET Output Location\
GET Tree locations point file\
GET API key for Google Street View

FUNC fetchStreetViews (tree Locations file, output Workspace, API_key)\
CREATE an empty Shapefile with WGS84 GCS system.

FOR each point location in tree Locations file:

> FOR each pitch angle:
>
> FOR each heading angle:
>
> CREATE Url\
> DOWNLOAD street view image
>
> END FOR
>
> END FOR
>
> FUNC fetchMetadata(location, pitch, heading)\
> DOWNLOAD metadata\
> WRITE metadata to a file as json\
> EXTRACT date, latitude and longitude of the Street view image from
> metadata\
> END FUNC
>
> FUNC insertGSVintoShapefile(date of photo, latitude of photo,
> longitude of photo, output shapefile name)
>
> INSERT date and the local drive paths of street view images into
> output file
>
> END FUNC

ENDFOR\
ENDFUNC

**GUI:**

![](media/image2.png){width="6.5in" height="2.036111111111111in"}Tool 1:
LAS to Tree Canopy

![](media/image3.png){width="6.5in" height="2.0430555555555556in"}Tool
2: Fetch Google Street View Images of Trees

Tool 1:

  -----------------------------------------------------------------------------------------------------------------------------
  **Parameter**   **Data     **Type**   **Direction**   **Default**                                                **Filter**
                  Type**                                                                                           
  --------------- ---------- ---------- --------------- ---------------------------------------------------------- ------------
  Input LAS file  File       Required   Input           ../data/LiDAR/30394_1.las                                   

  Output Location Folder     Required   Input           ../data/outputs                                            

  Inverted        Feature    Required   Input           ../data/features/Building_footprint_inverted_30394_1.shp   
  Building        class                                                                                            
  Footprints file                                                                                                  

  Spatial         Double     Required   Input           2                                                          
  Resolution                                                                                                       

  Road Network    Feature    Required   Input           ../data/features/Charlotte/Road_Charlotte_30394_1.shp      
                  class                                                                                            

  API_key         String     Required   Input           AIzaSyDNnEDpuoe1sYO7w6UB4Tz4rEWdZRD4fXA                    

  Output Tree     Feature    Derived    Output                                                                     
  Canopy          class                                                                                            

  Output Tree     Feature    Derived    Output                                                                     
  Points          class                                                                                            
  -----------------------------------------------------------------------------------------------------------------------------

Tool 2:

  ---------------------------------------------------------------------------------------------------------------
  **Parameter**   **Data     **Type**   **Direction**   **Default**                                  **Filter**
                  Type**                                                                             
  --------------- ---------- ---------- --------------- -------------------------------------------- ------------
  Input workspace Folder     Required   Input           ../data                                       

  Shapefile       Feature    Required   Input           ../data/features/Tree_points_near_road.shp   
  representing    Class                                                                              
  tree locations                                                                                     

  Google Street   String     Required   Input           AIzaSyDNnEDpuoe1sYO7w6UB4Tz4rEWdZRD4fXA      
  View Static                                                                                        
  API_key                                                                                            

  Output          Feature    Derived    Output                                                       
  Streetview      class                                                                              
  locations                                                                                          
  ---------------------------------------------------------------------------------------------------------------
