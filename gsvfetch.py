# gsvfetch.py
# Purpose: Fetches Google street view images for each location of the input point file. This program also creates a point shapefile
#          with the local drive links to the downloaded street view images. Image metadata will be downloaded too as a separate file.
# Usage: Output_Location Tree_locations_shapefile API_key 
# Example: C:\Project\data\outputs  C:\Project\data\Tree_locations.shp AIzaSyDNnEDpuoe1sWO7w6UB4Tz4rEWdZXXXXXX
# Input Tree locations shapefile can be in any coordinate system.
# Acronyms: GSV = Google Street View, p0h0 = Pitch-angle0 Heading-angle0

"C:/Users/vvivekn/Google Drive/NCSU_Courseware/GIS_714_Geocomputing and Simulations/Final_project/GSVs/"
"C:/Users/vvivekn/Google Drive/NCSU_Courseware/GIS_714_Geocomputing and Simulations/Final_project/Data/Roads/Points_along_roads_in_study_area_Raleigh.shp"
"AIzaSyDNnEDpuoe1sYO7w6UB4Tz4rEWdZRD4fXA"

import urllib, arcpy, sys, time, json, os

   
def createImageTaggedShapefile(outWorkspace, treeLocations):
    ''' Creates an output Shapefile that has a Date field, a latitude field, a longitude field and 18 other fields to store
    the local hard drive links of each of the 18 different angle of view images from the same location. '''

    outShapefileName = os.path.splitext(os.path.basename(treeLocations))[0]+"_GSV.shp"
    if not os.path.exists(outShapefileName):
        WGS84 = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.CreateFeatureclass_management(outWorkspace,outShapefileName,"POINT",spatial_reference = WGS84 )
        arcpy.AddField_management(outShapefileName, "Date", "DATE")
        arcpy.AddField_management(outShapefileName, "Latitude", "DOUBLE")
        arcpy.AddField_management(outShapefileName, "Longitude", "DOUBLE")
        arcpy.AddField_management(outShapefileName, "p0h0", "TEXT",field_length = 200) # p = pitch, h = heading
        arcpy.AddField_management(outShapefileName, "p0h60", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p0h120", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p0h180", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p0h240", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p0h300", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p45h0", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p45h60", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p45h120", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p45h180", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p45h240", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p45h300", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p90h0", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p90h60", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p90h120", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p90h180", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p90h240", "TEXT",field_length = 200)
        arcpy.AddField_management(outShapefileName, "p90h300", "TEXT",field_length = 200)
    printArc ("Empty Shapefile Created")    
    return outShapefileName

    

def fetchStreetViews(treeLocations, outWorkspace, API_key):
    '''Fetches Google StreetView images from each location nearest to the input point shapefile and creates an image tagged output shapefile.'''
    # A total of 18 images, each having different pitch angle and heading angle, will be fetched from each point location.
    # The local hard drive links of images so fetched will be written into the output point shapefile.'''

    workSpace = outWorkspace
    arcpy.env.workspace = workSpace
    arcpy.env.overwriteOutput = True 
    # Obtainin the projected coordinate system of input tree locations file
    desc = arcpy.Describe(treeLocations)
    inCS = desc.spatialReference #inCS stands for input Coordinate system
    # Reprojecting Tree locations file to a Geographic Coordinate System to match Google's projection system
 
 
    treeLocations_proj = os.path.splitext(os.path.basename(treeLocations))[0] + "_Reprojected.shp"
    out_coordinate_system = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    arcpy.Project_management(treeLocations, treeLocations_proj, out_coordinate_system)
    treeLocations_proj 
    outShapefile = createImageTaggedShapefile(outWorkspace, treeLocations_proj)
    
    

    # Finding latitude and longitude of each tree location and storing it in two lists, longitude and latitude.
    longitude = []
    latitude = []
    fc = os.path.join(arcpy.env.workspace, treeLocations_proj)
    sc = arcpy.da.SearchCursor(fc, ['SHAPE@XY'])
    for row in sc:
        longitude.append(row[0][0])
        latitude.append(row[0][1])
    del sc

    
    # heading angle can be any value between 0 and 360. We will use 0,60,120,180,240, and 300 as our heading angles (total 6 different values).
    # pitch angle varies from 0 to 90. We will use 0, 45 and 90 as our pitch angles (total 3 different values).
    # Therefore at each photo location, there are 6 * 3 = 18 photos
    pitch = 0
    heading = 0
    GSV_Filename_List = []
    for location in range(len(longitude)):
        for pitch in range(0,91,45):
            for heading in range(0,360, 60):
                url = "https://maps.googleapis.com/maps/api/streetview?location={0},{1}&size=640x640&heading={2}&pitch={3}&fov=120&key={4}".format\
                      (latitude[location],longitude[location], heading, pitch, API_key)

                GSV_Filename = "GSVimages/GSV_{0}_{1}_{2}_{3}.jpg".format(latitude[location],longitude[location], heading, pitch)
                GSV_absPath = os.path.join(workSpace, GSV_Filename)
                GSV_Filename_List.append(GSV_absPath)
                if not os.path.exists(GSV_absPath):
                    urllib.urlretrieve(url, GSV_absPath)
                
               # time.sleep(0.501) #GSV API will blacklist the user if the frequency of requests is very high. This code pauses the execution for 501 milliseconds 
        printArc ("Street view images from a point location successfully downloaded to local disk")    
        photo_details = fetchMetadata(location, pitch, heading, API_key, workSpace, GSV_Filename_List, latitude, longitude)
        date_photo = photo_details[0]
        latitude_photo = photo_details[1]
        longitude_photo = photo_details[2]
        # The following function inserts a row into the output shapefile.
        insertGSVintoShapefile(date_photo, latitude_photo, longitude_photo, GSV_Filename_List, outShapefile)
        GSV_Filename_List = []
    printArc ("Shapefile has been successfully updated with Street view images!")    
    outShapefile_proj = os.path.splitext(os.path.basename(outShapefile))[0] + "_Reprojected.shp"
    spatial_ref = arcpy.Describe(treeLocations).spatialReference
    arcpy.Project_management(outShapefile, outShapefile_proj, out_coordinate_system)
    if __name__ == 'main':
        arcpy.SetParameterAsText(3, outShapefile_proj)
    else:
        arcpy.SetParameterAsText(8, outShapefile_proj)
    
def fetchMetadata(location, pitch, heading, API_key, workSpace, GSV_Filename_List, latitude, longitude):
        '''Fetches the metadata of the Google Street View Images at each location. It should be noted that all the 18 images with different look angles have the
        same metadata. Therefore only one metadata file will be written for each location. '''
        
        metadata_url = "https://maps.googleapis.com/maps/api/streetview/metadata?location={0},{1}&key={2}".format(latitude[location],longitude[location], API_key) 
        response = urllib.urlopen(metadata_url)
        data = json.loads(response.read())
        if data['status'] != 'NOT_FOUND':
            longitude_photo = (data['location']['lng'])
            latitude_photo = (data['location']['lat'])
            date_photo = data['date']

            # Writing metadata to a file
            GSV_metadata_Filename = "GSVmetadata/GSV_{0}_{1}.json".format(latitude[location],longitude[location])
            GSV_metadata_absPath = os.path.join(workSpace,GSV_metadata_Filename)
            f = open(GSV_metadata_absPath, 'w')
            f.write(str(data))
            f.close()
            return date_photo, latitude_photo, longitude_photo
        

def insertGSVintoShapefile(date_photo, latitude_photo, longitude_photo, GSV_Filename_List, outShapefile):
    '''Populates a row in the output shapefile with the date of the street view image, its latitude and longitude, and the local hardrive file paths of the 18
    different images at each location.'''

    # Creating an Insert cursor for the output shapefile
    try:
       ic
    except NameError:
        ic = arcpy.da.InsertCursor(outShapefile,['Date','Latitude','Longitude',\
                                                           'p0h0',  'p0h60',  'p0h120',  'p0h180',  'p0h240',  'p0h300',\
                                                           'p45h0', 'p45h60', 'p45h120', 'p45h180', 'p45h240', 'p45h300',\
                                                           'p90h0', 'p90h60', 'p90h120', 'p90h180', 'p90h240', 'p90h300', 'SHAPE@XY'])
    
    ic.insertRow((date_photo, latitude_photo, longitude_photo, \
                      GSV_Filename_List[0], GSV_Filename_List[1], GSV_Filename_List[2], \
                      GSV_Filename_List[3], GSV_Filename_List[4], GSV_Filename_List[5],\
                      GSV_Filename_List[6], GSV_Filename_List[7], GSV_Filename_List[8],\
                      GSV_Filename_List[9], GSV_Filename_List[10], GSV_Filename_List[11],\
                      GSV_Filename_List[12], GSV_Filename_List[13], GSV_Filename_List[14],\
                      GSV_Filename_List[15], GSV_Filename_List[16], GSV_Filename_List[17],
                      (longitude_photo, latitude_photo)))
    
    printArc("A row has been added to output shapefile") 
    GSV_Filename_List = []

def printArc(message):
    '''Print message for Script Tool and standard output.'''
    print message
    arcpy.AddMessage(message)

if __name__ == "__main__":
    ## Inputs from user
    #1. workspace 
    outWorkSpace = sys.argv[1]
    #2. shapefile containing tree locations 
    treeLocations = sys.argv[2]
    #3. API Key ( Google StreetView Static API ) 
    API_key = sys.argv[3]


    fetchStreetViews(treeLocations, outWorkspace, API_key)
    
    





