# import subprocess
# from PIL import Image
# import gdal
import numpy as np
from netCDF4 import Dataset
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
import fiona
import geojson
import pyproj
import shapely.geometry
import shapely.ops
import os, tempfile, shutil, sys

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


def get_mean(bounds,variable):
    graph_json= {}
    file_dir = '/wrf/'
    miny = float(bounds[1])
    minx = float(bounds[0])
    maxx = float(bounds[2])
    maxy = float(bounds[3])

    ts_plot = []

    for file in os.listdir(file_dir):
        nc_fid = Dataset(file_dir + file, 'r')
        lats = nc_fid.variables['XLAT'][0, :, :]
        lons = nc_fid.variables['XLONG'][0, :, :]
        field = nc_fid.variables[variable][0, :, :]
        abslat = np.abs(lats - miny)
        abslon = np.abs(lons - minx)
        abslat2 = np.abs(lats - maxy)
        abslon2= np.abs(lons - maxx)

        c = np.maximum(abslon, abslat)
        minx_idx, miny_idx = np.where(c == np.min(c))

        d = np.maximum(abslon2, abslat2)
        maxx_idx, maxy_idx = np.where(d == np.min(d))

        values = field[minx_idx[0]:maxx_idx[0],miny_idx[0]:maxy_idx[0]]


        var_val = np.mean(values)

        file_ls = file.split('_')
        day = file_ls[2].split('-')
        timing = file_ls[3].split(':')

        date_string = datetime(int(day[0]), int(day[1]), int(day[2]), int(timing[0]), int(timing[1]), int(timing[2]))
        time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
        ts_plot.append([time_stamp, float(var_val)])
        ts_plot.sort()


    graph_json["values"] = ts_plot
    graph_json["bounds"] = [round(minx,2),round(miny,2),round(maxx,2),round(maxy,2)]
    graph_json = json.dumps(graph_json)
    return graph_json

def get_ts_plot(variable,pt_coords):
    graph_json = {}
    ts_plot = []

    file_dir = '/wrf/'
    coords = pt_coords.split(',')
    stn_lat = float(coords[1])
    stn_lon = float(coords[0])
    for file in os.listdir(file_dir):
        nc_fid = Dataset(file_dir + file, 'r')
        lats = nc_fid.variables['XLAT'][0,:,:]
        lons = nc_fid.variables['XLONG'][0,:,:]
        field = nc_fid.variables[variable][0,:,:]
        abslat = np.abs(lats - stn_lat)
        abslon = np.abs(lons - stn_lon)
        c = np.maximum(abslon, abslat)
        x, y = np.where(c == np.min(c))
        var_val = field[x[0], y[0]]

        file_ls = file.split('_')
        day = file_ls[2].split('-')
        timing = file_ls[3].split(':')
        # file_dt = datetime.strptime(file_ls[2]+' '+file_ls[3], "%Y-%m-%d %H:%M:%S")
        date_string = datetime(int(day[0]),int(day[1]),int(day[2]),int(timing[0]),int(timing[1]),int(timing[2]))
        time_stamp = calendar.timegm(date_string.utctimetuple()) * 1000
        # ts_plot.append([datetime(int(day[0]),int(day[1]),int(day[2]),int(timing[0]),int(timing[1])),var_val])
        ts_plot.append([time_stamp,float(var_val)])
        ts_plot.sort()
    graph_json["values"] = ts_plot
    graph_json["point"] = [round(stn_lat,2),round(stn_lon,2)]
    graph_json = json.dumps(graph_json)
    return graph_json

def convert_shp(files):
    geojson_string = ''
    try:
        temp_dir = tempfile.mkdtemp()
        for f in files:
            f_name = f.name
            f_path = os.path.join(temp_dir,f_name)

            with open(f_path,'wb') as f_local:
                f_local.write(f.read())


        for file in os.listdir(temp_dir):
            if file.endswith(".shp"):
                f_path = os.path.join(temp_dir,file)
                omit = ['SHAPE_AREA', 'SHAPE_LEN']

                with fiona.open(f_path) as source:
                    project = functools.partial(pyproj.transform,
                                                pyproj.Proj(**source.crs),
                                                pyproj.Proj(init='epsg:3857'))
                    features = []
                    for f in source:
                        shape = shapely.geometry.shape(f['geometry'])
                        projected_shape = shapely.ops.transform(project, shape)

                        # Remove the properties we don't want
                        props = f['properties']  # props is a reference
                        for k in omit:
                            if k in props:
                                del props[k]

                        feature = geojson.Feature(id=f['id'],
                                                  geometry=projected_shape,
                                                  properties=props)
                        features.append(feature)
                    fc = geojson.FeatureCollection(features)

                    geojson_string = geojson.dumps(fc)


    except:
        return 'error'
    finally:
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                # for file in files:
                #     if str(file).endswith('.shp'):
                #         reader = shapefile.Reader(file)
                #         fields = reader.fields[1:]
                #         field_names = [field[0] for field in fields]
                #         buffer = []
                #         for sr in reader.shapeRecords():
                #             atr = dict(zip(field_names, sr.record))
                #             geom = sr.shape.__geo_interface__
                #             buffer.append(dict(type="Feature", geometry=geom, properties=atr))

                # print buffer

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

def get_times():
    start_date = '2017-03-09 18:00:00'

    dates = []
    dates.append((start_date,start_date))
    for i in range(1,73):
        the_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        the_time += timedelta(hours=i)
        dates.append((the_time.strftime("%Y-%m-%d %H:%M:%S"),the_time.strftime("%Y-%m-%d %H:%M:%S")))

    return dates



