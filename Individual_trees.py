# Individual_trees.py
# Purpose: Creates a tree canopy polygon shapefile and a point shapefile representing tree locations and displays them on a map.
# Usage: Input_LASfile Output_Location Buildings_footprint_inverted resolution Road_Network API_Key 
# Example: C:\Project\data\LiDAR\30394_1.las C:\Project\data\outputs C:\Project\data\features\Bfoot_inv.shp 2 C:\Project\data\Road.shp AIzaSyDNnEDpuoe1sWO7w6UB4Tz4rEWdZXXXXXX
# Abbreviations: CHM = Canopy Height Model, DSM = Digital Surface Model, DEM = Digital Elevation Model.
import arcpy, sys, os

def createElevationModels(LasFiles, outL, resolution):
    '''Computes the Digital Elevation Model (DEM) and Digital Surface Model(DSM) from input Lasfiles'''
    # This function stores DEM and DSM into the output location input as a parameter.
    # The LasFiles parameter could be semicolon separated string of LAS file names. The third parameter specifies the spatial resolution if the required output.
    # The unit of the spatial resolution (meters/feet) will depend on the projection system of the LAS Files.

    arcpy.env.workspace = outL
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension('Spatial')

    # Steps involved in creating a DEM or DSM are
    # LAS File --> LAS Dataset --> LAS Dataset Layer --> Raster (DEM/DSM)
    # creating a LAS Dataset from LAS files(s)    
    LasD = os.path.join(outL,"LasD.lasd")
    arcpy.management.CreateLasDataset(LasFiles, LasD)

    # creating a LAS Dataset Layer for creating DSM. The classification codes for the resulting layer has to be chosen in this step.
    # Since this layer is being created for a DSM, all classification codes are required. No classificationodes are given as parameters
    # in the MakeLasDatasetLayer() command because all codes are included by default if no classification codes are explicitly given as parameters.
    arcpy.management.MakeLasDatasetLayer(LasD, "LasD_LasDatasetLayer")
    # creating DSM with a spatial resolution of 2 feet. 
    arcpy.conversion.LasDatasetToRaster("LasD_LasDatasetLayer", "DSM.tif", "ELEVATION", "BINNING MAXIMUM LINEAR", "FLOAT", "CELLSIZE", resolution, 1)
    printArc("DSM.tif Created")

    # creating a LAS Dataset Layer for creating DEM. The classification codes 2 is for Ground and 13 is for roads.
    arcpy.management.MakeLasDatasetLayer(LasD, "LasD_LasDatasetLayer_DEM", "2;13")
    # creating DEM with a spatial resolution of 2 feet. 
    arcpy.conversion.LasDatasetToRaster("LasD_LasDatasetLayer", "DEM.tif", "ELEVATION", "BINNING MINIMUM LINEAR", "FLOAT", "CELLSIZE", resolution, 1)
    printArc("DEM.tif Created")

def createCHM(LasFiles, outL, resolution):
    ''' Computes a Canopy Height Model(CHM) from input LasFiles.'''
    # CHM = DSM - DEM.
    # This function takes three parameters as input. The first parameter is input LAS Files. This can be a single LAS file or more than one LAS File.
    # Multiple LAS files should be input as a single semicolon separated string. The second parameter is the output location. The third parameter is the resolution
    # of the output. The unit of the spatial reolution (meters/feet) will depend on the projection system of the LAS Files.
    
    createElevationModels(LasFiles, outL, resolution)
    arcpy.env.workspace = outL
    arcpy.env.overwriteOutput = True
    dsm_obj = arcpy.Raster("DSM.tif")
    dem_obj = arcpy.Raster("DEM.tif")
    chm_obj = dsm_obj - dem_obj
    chm_obj.save("CHM.tif")
    printArc("CHM.tif Created")
    del chm_obj

def removeBuildings(workingDir, rast_fileName, invFootprint):
    '''Removes buildings from the input raster.'''
    # This tool clips the input raster rast_fileName with the input vector invFootprint
    
    arcpy.env.workspace = workingDir
    arcpy.env.overwriteOutput = True
    desc = arcpy.Describe(invFootprint)
    xmin = desc.extent.XMin
    xmax = desc.extent.XMax
    ymin = desc.extent.YMin
    ymax = desc.extent.YMax
    invFootprint_Extent = "{0} {1} {2} {3}".format(xmin, ymin, xmax, ymax)
    outFileName = os.path.splitext(rast_fileName)[0] + "_Clip.tif"
    arcpy.management.Clip(rast_fileName, invFootprint_Extent, outFileName, invFootprint, "-3.402823e+38", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
    printArc("Buildings clipped off")

def LAStoTreeCanopyPolygons(inLasFiles, outLocation, resolution, bFootprintInv):
    '''Creates a polygon shapefile representing the tree canopies of all the trees within the input Las files.'''
    # This function contains three parameters.The first parameter inLasFiles could be the file path of a single LAS file or semicolon separated path names
    # of LAS files. The parameter outLocation takes output folder location as as a string. The parameter resolution takes a floating point number.
    # The parameter bFootprintInv takes a shapefile representing inverted building footprints as input.

    createCHM(inLasFiles, outLocation, resolution)
    removeBuildings(outLocation, "CHM.tif", bFootprintInv)
    a = RasterObjects()
    
    # Watershed delineation and obtaining the tree canopy as polygons
    CHM_Fill = arcpy.sa.Fill(a.chm_obj_inv, 1)
    CHM_FlowDirection = arcpy.sa.FlowDirection(CHM_Fill)
    CHM_Basin = arcpy.sa.Basin(CHM_FlowDirection)
    arcpy.RasterToPolygon_conversion(CHM_Basin, "Tree_Canopy_out")
    printArc("Tree Canopy polygon shapefile Created.")
    
    a.destroyObjects()
    del CHM_Fill
    del CHM_FlowDirection
    del CHM_Basin

class RasterObjects:
    '''Creates and deletes raster objects that are needed by multiple functions'''
    def __init__(self):
        self.chm_obj = arcpy.Raster("CHM_Clip.tif")

        # Assigning pixels less than 2m to NoData in the CHM. This will produce a CHM that contains
        # only trees (The assumption is that there is nothing taller than 2m except buildings and trees within the study area.)
        self.maskRas = arcpy.sa.GreaterThan(self.chm_obj, 2)
        self.chm_obj_onlyTrees = self.chm_obj * self.maskRas

        #Inverting the values of the chm raster object. Inverting here means that the higher values will become the lower values and vice versa.
        self.chm_obj_inv = -1 * (self.chm_obj_onlyTrees - self.chm_obj_onlyTrees.maximum) + self.chm_obj_onlyTrees.minimum

    def destroyObjects(self):
        del self.chm_obj
        del self.chm_obj_inv
        del self.maskRas
        del self.chm_obj_onlyTrees


    

def TreeLocations():
    '''Creates a point shapefile representing the location of trees.'''
    b = RasterObjects()
    
    # Finding the tree locations using Focal Statistics
    Focal_stats_raster = arcpy.sa.FocalStatistics(b.chm_obj_onlyTrees, "Circle 10 CELL", "MAXIMUM", "DATA")

    # Creating the tree locations as a raster
    chm_obj_onlyTrees_NullModified =  arcpy.sa.Con(b.chm_obj_onlyTrees, b.chm_obj_onlyTrees, -100, 'Value > 0')
    Tree_points_raster = arcpy.sa.EqualTo(Focal_stats_raster, chm_obj_onlyTrees_NullModified)
    Tree_points_raster_final = arcpy.sa.SetNull(Tree_points_raster, Tree_points_raster, "Value = 0")
    Tree_points_raster_final.save("Tree_point_raster.tif")

    # Converting tree locations raster to vector.
    arcpy.RasterToPoint_conversion(Tree_points_raster_final, "Tree_Points")
    printArc("Tree points file has been created.")
    b.destroyObjects()
    del Tree_points_raster
    del Focal_stats_raster

def printArc(message):
    '''Print message for Script Tool and standard output.'''
    print message
    arcpy.AddMessage(message)

if __name__ == '__main__':
    import gsvfetch
    arcpy.CheckOutExtension('Spatial')
    ## Inputs from user
    # 1. Input LAS File
    inLasFiles = sys.argv[1]

    #2. Output Location
    outLocation = sys.argv[2]

    #3 Buildings footprint inverted
    bFootprintInv = sys.argv[3]

    #4 Spatial resolution of elevation Models
    resolution = float(sys.argv[4])

    #5 Road Network
    roads = sys.argv[5]

    #5. API Key ( Google StreetView Static API ) 
    API_key = sys.argv[6]

    inLasFiles = inLasFiles.split(";")
    arcpy.env.workspace = outLocation
    arcpy.env.overwriteOutput = True

    
    LAStoTreeCanopyPolygons(inLasFiles, outLocation, resolution, bFootprintInv)
    TreeLocations()
    roads_buffered = "roads_buffered.shp"
    arcpy.Buffer_analysis(roads, roads_buffered, "80 Feet")
    arcpy.Clip_analysis("Tree_Points.shp", roads_buffered, "Tree_points_near_road.shp")
    arcpy.Clip_analysis("Tree_Canopy_out.shp", roads_buffered,  "Tree_canopy_road.shp")
    arcpy.SetParameterAsText(6, "Tree_canopy_road")
    arcpy.SetParameterAsText(7, "Tree_points_near_road")
    gsvfetch.fetchStreetViews("Tree_points_near_road_subset.shp", outLocation, API_key)
    
 