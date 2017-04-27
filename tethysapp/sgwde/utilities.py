# import subprocess
# from PIL import Image
# import gdal
import numpy as np #Need this for parsing the arrays
from netCDF4 import Dataset #Need this parsing the netcdf file
# import urllib2, json, mimetypes,os,urlparse
# import ftplib
# from StringIO import StringIO
# from zipfile import ZipFile
# import gzip
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# from matplotlib.colors import LogNorm, SymLogNorm
# import scipy.ndimage
# from mpl_toolkits.basemap import Basemap
# import numpy
import os,os.path
from datetime import datetime, timedelta
import json
from json import dumps
import time, calendar
import functools
import fiona #Important Module: Need this for reading the uploaded shapefile
import geojson #Need this for working with geojson objects
import pyproj #Need this to reproject the wrf cetcdf file
import shapely.geometry #Need this to find the bounds of a given geometry
import shapely.ops
import os, tempfile, shutil

#Sample code on how to get the value for given point
# def get_val():
#     file  ='/home/tethys/wrf/wrfout_d02_2017-03-09_21:00:00'
#     nc_file = Dataset(file,'r')
#     precip = nc_file.variables['T02_MEAN'][0,:,:]
#     lats = nc_file.variables['XLAT'][0,:,:]
#     lons = nc_file.variables['XLONG'][0,:,:]
#     stn_lat = float('20.7')
#     stn_lon = float('70.8')
#     abslat = np.abs(lats - stn_lat)
#     abslon = np.abs(lons - stn_lon)
#     c = np.maximum(abslon,abslat)
#     x, y = np.where(c == np.min(c))
#     grid_temp = precip[x[0], y[0]]

#Function for getting the mean value of a variable over given bounds. This works for getting the mean values of the polygon and the shapefile.
def get_mean(bounds,variable):

    #Initializing an empty json object. This object will have contain the results.
    graph_json= {}

    #Before you specify the file directory be sure to download and unzip all the wrf files onto the server machine. Change the name of the file directory as you see fit.
    file_dir = '/wrf/'

    #Defining minx,miny,max,maxy
    miny = float(bounds[1])
    minx = float(bounds[0])
    maxx = float(bounds[2])
    maxy = float(bounds[3])

    ts_plot = []

    #Looping through the files in the directory. Each file is a timestep.
    for file in os.listdir(file_dir):
        nc_fid = Dataset(file_dir + file, 'r')  #Reading the netCDF file
        lats = nc_fid.variables['XLAT'][0, :, :]    #Defining the latitutde array
        lons = nc_fid.variables['XLONG'][0, :, :]   #Defining the longitude array
        field = nc_fid.variables[variable][0, :, :] #Defining the variable array
        abslat = np.abs(lats - miny)    #Finding the absolute lat for minx
        abslon = np.abs(lons - minx)    #Finding the absolute lon for miny
        abslat2 = np.abs(lats - maxy)   #Finding the absolute lat for maxx
        abslon2= np.abs(lons - maxx)    #Finding the absolute lat for mixy

        #Finding the index of the minx,miny
        c = np.maximum(abslon, abslat)
        minx_idx, miny_idx = np.where(c == np.min(c))

        #Finding the index of maxx,maxy
        d = np.maximum(abslon2, abslat2)
        maxx_idx, maxy_idx = np.where(d == np.min(d))

        #Finding all the values that fall within the bounds of the indexes
        values = field[minx_idx[0]:maxx_idx[0],miny_idx[0]:maxy_idx[0]]

        #Averaging all the values
        var_val = np.mean(values)

        #Finding the time in UTC seconds from the file name
        file_ls = file.split('_')
        day = file_ls[2].split('-')
        timing = file_ls[3].split(':')

        date_string = datetime(int(day[0]), int(day[1]), int(day[2]), int(timing[0]), int(timing[1]), int(timing[2]))
        time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
        #Adding each timestep and tis corresponding value to an empty list
        ts_plot.append([time_stamp, float(var_val)])
        ts_plot.sort()

    #Returning the list with the timeseries values and the bounds so that they can be displayed on the graph.
    graph_json["values"] = ts_plot
    graph_json["bounds"] = [round(minx,2),round(miny,2),round(maxx,2),round(maxy,2)]
    graph_json = json.dumps(graph_json)
    return graph_json

#Function for getting the value of a variable at a given point.
def get_ts_plot(variable,pt_coords):

    # Initializing an empty json object. This object will have contain the results.
    graph_json = {}

    #Empty list to store the timeseries values
    ts_plot = []

    # Before you specify the file directory be sure to download and unzip all the wrf files onto the server machine. Change the name of the file directory as you see fit.
    file_dir = '/wrf/'
    #Defining the lat and lon from the coords string
    coords = pt_coords.split(',')
    stn_lat = float(coords[1])
    stn_lon = float(coords[0])

    #Looping through each timestep
    for file in os.listdir(file_dir):
        nc_fid = Dataset(file_dir + file, 'r') #Reading the netCDF file
        lats = nc_fid.variables['XLAT'][0,:,:]  #Defining the latitude array
        lons = nc_fid.variables['XLONG'][0,:,:] #Defining the longitude array
        field = nc_fid.variables[variable][0,:,:]   #Defning the variable array
        abslat = np.abs(lats - stn_lat) #Finding the absolute latitude
        abslon = np.abs(lons - stn_lon) #Finding the absolute longitude

        #Thanks to Brian Baylock. See http://kbkb-wx-python.blogspot.com/2016/08/find-nearest-latitude-and-longitude.html
        #Finding the index of the latitude and longitude
        c = np.maximum(abslon, abslat)
        x, y = np.where(c == np.min(c))


        #Getting the value based on the index
        var_val = field[x[0], y[0]]

        #Getting the value of the timestep and converting it into UTC seconds
        file_ls = file.split('_')
        day = file_ls[2].split('-')
        timing = file_ls[3].split(':')
        # file_dt = datetime.strptime(file_ls[2]+' '+file_ls[3], "%Y-%m-%d %H:%M:%S")
        date_string = datetime(int(day[0]),int(day[1]),int(day[2]),int(timing[0]),int(timing[1]),int(timing[2]))
        time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
        # ts_plot.append([datetime(int(day[0]),int(day[1]),int(day[2]),int(timing[0]),int(timing[1])),var_val])
        #Adding the timestep and its corresponding value to an empty list
        ts_plot.append([time_stamp,float(var_val)])
        ts_plot.sort()

    # Returning the list with the timeseries values and the point so that they can be displayed on the graph.
    graph_json["values"] = ts_plot
    graph_json["point"] = [round(stn_lat,2),round(stn_lon,2)]
    graph_json = json.dumps(graph_json)
    return graph_json

#Conver the shapefiles into a geojson object
def convert_shp(files):

    #Initizalizing an empty geojson string.
    geojson_string = ''

    try:
        #Storing the uploaded files in a temporary directory
        temp_dir = tempfile.mkdtemp()
        for f in files:
            f_name = f.name
            f_path = os.path.join(temp_dir,f_name)

            with open(f_path,'wb') as f_local:
                f_local.write(f.read())

        #Getting a list of files within the temporary directory
        for file in os.listdir(temp_dir):
            #Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(temp_dir,file)
                omit = ['SHAPE_AREA', 'SHAPE_LEN']

                #Reading the shapefile with fiona and reprojecting it
                with fiona.open(f_path) as source:
                    project = functools.partial(pyproj.transform,
                                                pyproj.Proj(**source.crs),
                                                pyproj.Proj(init='epsg:3857'))
                    features = []
                    for f in source:
                        shape = shapely.geometry.shape(f['geometry']) #Getting the shape of the shapefile
                        projected_shape = shapely.ops.transform(project, shape) #Transforming the shapefile

                        # Remove the properties we don't want
                        props = f['properties']  # props is a reference
                        for k in omit:
                            if k in props:
                                del props[k]

                        feature = geojson.Feature(id=f['id'],
                                                  geometry=projected_shape,
                                                  properties=props) #Creating a geojson feature by extracting properties through the fiona and shapely.geometry module
                        features.append(feature)
                    fc = geojson.FeatureCollection(features)

                    geojson_string = geojson.dumps(fc) #Creating the geojson string


    except:
        return 'error'
    finally:
        #Delete the temporary directory once the geojson string is created
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    return geojson_string



# Code for creating the plots
# def create_png():
#     random = ''
# #
# #     file_loc = '/home/tethys/wrf/wrfout_d02_2017-03-09_18:00:00'
#     variables = {'TACC_PRECIP':'Total Accumulated Precipitation(mm)','TACC_RAIN':'Total Rainfall Accumulation(mm)','TACC_SNICE':'Total Snow/Ice Accumulation(mm)','REFC_MAX':'Maximum Composite reflectivity(dbz)','S10_MAX':'Maximum 10 M wind speed(m s-1)','GCOLMAX':'Maximum Column Integrated Graupel(kg m-2)','UDHELI16_MAX':'1 to 6km Maximum Updraft Helicity(m2 s-2)','MAX_RRATE':'Period Maximum Rainfall Rate (mm s-1)','MAX_SFRATE':'Period Maximum Snow + Graupel Precipitation Rate(mm s-1)','T02_MEAN':'Mean Shelter Temperature(K)'}
#     file_dir = '/home/tethys/wrf/'
#     png_loc = '/home/tethys/wrf_plots/'
#     for var in variables:
#         for file in os.listdir(file_dir):
#             nc_fid = Dataset(file_dir+file, 'r')
#             lats = nc_fid.variables['XLAT']
#             lons = nc_fid.variables['XLONG']
#             field = nc_fid.variables[var]
#             map = Basemap(width=5000000, height=3500000, projection='lcc', resolution='l', lat_0=27.7, lon_0=85.3,
#                           llcrnrlon=78, llcrnrlat=19.2, urcrnrlon=96.76, urcrnrlat=34, )
#             x, y = map(lons[0], lats[0])
#             contour = map.contourf(x, y, field[0])
#             map.drawcoastlines()
#             map.drawstates()
#             map.drawcountries()
#             cbar = map.colorbar(contour, location='bottom', pad='10%')
#             dt = file.split('_')
#             day = dt[2]
#             time = dt[3]
#             title = variables[var]+' on '+day+' '+time
#             png_file = day+'_'+time+'_'+var+'.png'
#             plt.title(title)
#             plt.savefig(png_loc+png_file)
#             # plt.show()
#             plt.close()
#             print 'Saved '+png_file
#
#
#     return random

#Sample code for finding infromation about the netcdf file
# def ncdump(nc_fid, verb=True):
#     '''
#     ncdump outputs dimensions, variables and their attribute information.
#     The information is similar to that of NCAR's ncdump utility.
#     ncdump requires a valid instance of Dataset.
#
#     Parameters
#     ----------
#     nc_fid : netCDF4.Dataset
#         A netCDF4 dateset objecte
#     verb : Boolean
#         whether or not nc_attrs, nc_dims, and nc_vars are printed
#
#     Returns
#     -------
#     nc_attrs : list
#         A Python list of the NetCDF file global attributes
#     nc_dims : list
#         A Python list of the NetCDF file dimensions
#     nc_vars : list
#         A Python list of the NetCDF file variables
#     '''
#     def print_ncattr(key):
#         """
#         Prints the NetCDF file attributes for a given key
#
#         Parameters
#         ----------
#         key : unicode
#             a valid netCDF4.Dataset.variables key
#         """
#         try:
#             # print "\t\ttype:", repr(nc_fid.variables[key].dtype)
#             for ncattr in nc_fid.variables[key].ncattrs():
#                 # print '\t\t%s:' % ncattr,\
#                       repr(nc_fid.variables[key].getncattr(ncattr))
#         except KeyError:
#             # print "\t\tWARNING: %s does not contain variable attributes" % key
#             key
#     #
#     # NetCDF global attributes
#     nc_attrs = nc_fid.ncattrs()
#     if verb:
#         # print "NetCDF Global Attributes:"
#         for nc_attr in nc_attrs:
#             # print '\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr))
#             nc_attr, repr(nc_fid.getncattr(nc_attr))
#     nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
#     # Dimension shape information.
#     if verb:
#         # print "NetCDF dimension information:"
#         for dim in nc_dims:
#             # print "\tName:", dim
#             # print "\t\tsize:", len(nc_fid.dimensions[dim])
#             print_ncattr(dim)
#     # Variable information.
#     nc_vars = [var for var in nc_fid.variables]  # list of nc variables
#     if verb:
#         # print "NetCDF variable information:"
#         for var in nc_vars:
#             if var not in nc_dims:
#                 # print '\tName:', var
#                 # print "\t\tdimensions:", nc_fid.variables[var].dimensions
#                 # print "\t\tsize:", nc_fid.variables[var].size
#                 print_ncattr(var)
#     return nc_attrs, nc_dims, nc_vars

#Hard Coded to get the avaialable dates. This code will need to be changed to retrieve the dates more dynamically.
def get_times():
    start_date = '2017-03-09 18:00:00'

    dates = []
    dates.append((start_date,start_date))
    for i in range(1,73):
        the_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        the_time += timedelta(hours=i)
        dates.append((the_time.strftime("%Y-%m-%d %H:%M:%S"),the_time.strftime("%Y-%m-%d %H:%M:%S")))

    return dates



