import subprocess
from PIL import Image
import gdal
import numpy as np
from netCDF4 import Dataset
import urllib2, json, mimetypes,os,urlparse
import ftplib
from StringIO import StringIO
from zipfile import ZipFile
import gzip
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import LogNorm, SymLogNorm
import scipy.ndimage
from mpl_toolkits.basemap import Basemap
import numpy
import os,os.path
from datetime import datetime, timedelta

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

def ncdump(nc_fid, verb=True):
    '''
    ncdump outputs dimensions, variables and their attribute information.
    The information is similar to that of NCAR's ncdump utility.
    ncdump requires a valid instance of Dataset.

    Parameters
    ----------
    nc_fid : netCDF4.Dataset
        A netCDF4 dateset object
    verb : Boolean
        whether or not nc_attrs, nc_dims, and nc_vars are printed

    Returns
    -------
    nc_attrs : list
        A Python list of the NetCDF file global attributes
    nc_dims : list
        A Python list of the NetCDF file dimensions
    nc_vars : list
        A Python list of the NetCDF file variables
    '''
    def print_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        try:
            # print "\t\ttype:", repr(nc_fid.variables[key].dtype)
            for ncattr in nc_fid.variables[key].ncattrs():
                # print '\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr))
        except KeyError:
            # print "\t\tWARNING: %s does not contain variable attributes" % key
            key
    #
    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        # print "NetCDF Global Attributes:"
        for nc_attr in nc_attrs:
            # print '\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr))
            nc_attr, repr(nc_fid.getncattr(nc_attr))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        # print "NetCDF dimension information:"
        for dim in nc_dims:
            # print "\tName:", dim
            # print "\t\tsize:", len(nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        # print "NetCDF variable information:"
        for var in nc_vars:
            if var not in nc_dims:
                # print '\tName:', var
                # print "\t\tdimensions:", nc_fid.variables[var].dimensions
                # print "\t\tsize:", nc_fid.variables[var].size
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

def get_times():
    start_date = '2017-03-09 18:00:00'

    dates = []
    dates.append((start_date,start_date))
    for i in range(1,73):
        the_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        the_time += timedelta(hours=i)
        dates.append((the_time.strftime("%Y-%m-%d %H:%M:%S"),the_time.strftime("%Y-%m-%d %H:%M:%S")))

    return dates



