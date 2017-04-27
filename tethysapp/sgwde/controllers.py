from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

#All the commented out modules were used to make the png plots. Just leaving them here so that they can used if you need to replicate this process in the future.
# import subprocess
# import gdal
# import numpy as np
# from netCDF4 import Dataset
# import urllib2, json, mimetypes,os,urlparse
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# from matplotlib.colors import LogNorm, SymLogNorm
# import scipy.ndimage
# from mpl_toolkits.basemap import Basemap
# import numpy
from utilities import *
from tethys_sdk.gizmos \
    import SelectInput, \
    TimeSeries #Inbuilt Tethys gizmos to minimize JavaScript
# from datetime import datetime, timedelta
import json, \
    shapely.geometry #Need this module for getting the bounds of the shapefile and the polygon

@login_required()
def home(request):
    """
    Controller for the app home page.

    """

    #List of tuples containing the variable and its key word
    variable_options = [('Total Accumulated Precipitation(mm)','TACC_PRECIP'),('Total Rainfall Accumulation(mm)','TACC_RAIN'),('Total Snow/Ice Accumulation(mm)','TACC_SNICE'),('Maximum Composite reflectivity(dbz)','REFC_MAX'),('Maximum 10 M wind speed(m s-1)','S10_MAX'),('Maximum Column Integrated Graupel(kg m-2)','GCOLMAX'),('1 to 6km Maximum Updraft Helicity(m2 s-2)','UDHELI16_MAX'),('Period Maximum Rainfall Rate (mm s-1)','MAX_RRATE'),('Period Maximum Snow + Graupel Precipitation Rate(mm s-1)','MAX_SFRATE'),('Mean Shelter Temperature(K)','T02_MEAN')]

    #Select Variable Dropdown
    select_variable = SelectInput(display_text='Select WRF Variable',
                                  name='select_variable',
                                  multiple=False,
                                  options=variable_options,
                                  initial=['Total Accumulated Precipitation(mm)'])

    #Get the date options. This is somewhat static. This needs to be changed so that it is dynamic in the future. See utilities.py for get_times function.
    date_options = get_times()

    #Select Data Dropdown
    select_date = SelectInput(display_text='Select WRF Forecast Date',
                                  name='select_date',
                                  multiple=False,
                                  options=date_options,
                                  initial=['2017-03-09 18:00:00']) #Needs to be changed to be more dynamic

    context = {"select_variable":select_variable,"select_date":select_date}


    return render(request, 'sgwde/home.html', context)

def get_plot(request):
    return_obj = {}

    #Recreating the variable options, the text from this list will be used for titles and other metadata in the final plot.
    variable_options = [('Total Accumulated Precipitation(mm)', 'TACC_PRECIP'),
                        ('Total Rainfall Accumulation(mm)', 'TACC_RAIN'),
                        ('Total Snow/Ice Accumulation(mm)', 'TACC_SNICE'),
                        ('Maximum Composite reflectivity(dbz)', 'REFC_MAX'),
                        ('Maximum 10 M wind speed(m s-1)', 'S10_MAX'),
                        ('Maximum Column Integrated Graupel(kg m-2)', 'GCOLMAX'),
                        ('1 to 6km Maximum Updraft Helicity(m2 s-2)', 'UDHELI16_MAX'),
                        ('Period Maximum Rainfall Rate (mm s-1)', 'MAX_RRATE'),
                        ('Period Maximum Snow + Graupel Precipitation Rate(mm s-1)', 'MAX_SFRATE'),
                        ('Mean Shelter Temperature(K)', 'T02_MEAN')]

    #Check if tis an ajax post request
    if request.is_ajax() and request.method == 'POST':

        #Get the point/polygon/shapefile coordinates along with the selected variable
        pt_coords = request.POST['point-lat-lon']
        poly_coords  = request.POST['poly-lat-lon']
        shp_bounds = request.POST['shp-lat-lon']
        variable = request.POST['select_variable']

        #Find the variable name and unit from the variable_options dictionary using the variable key
        var_dict = dict((val,key) for (key,val) in variable_options)
        var_item = str(var_dict.get(variable))
        var_item = var_item.replace('(','~').replace(')','').split('~')
        var_unit = var_item[1]
        var_name = var_item[0]


        #Get the data and replace the string to mimic the name of the actual file structure
        date = request.POST['select_date']

        date = date.replace(' ','_')

        #Get the relevant timeseries based on point/polygon/shapefile. See utilities.py for the get_ts_plot,get_mean functions
        if pt_coords:
            graph = get_ts_plot(variable,pt_coords)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["point"]


        if poly_coords:
            poly_geojson = json.loads(poly_coords)

            #Get the bounds of the shape using shapely.geometry
            shape_obj = shapely.geometry.asShape(poly_geojson)
            poly_bounds = shape_obj.bounds
            graph = get_mean(poly_bounds,variable)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["bounds"]

        if shp_bounds:
            shp_bounds = tuple(shp_bounds.split(','))
            graph = get_mean(shp_bounds,variable)
            graph = json.loads(graph)
            return_obj["values"] = graph["values"]
            return_obj["location"] = graph["bounds"]


        png_file = date+'_'+variable+'.png'

        #Returning the png file, variable, variable name, variable unit as json objects.
        return_obj["png_file"] = png_file
        return_obj["variable"] = variable
        return_obj["var_name"] = var_name
        return_obj["var_unit"] = var_unit

        return_obj["status"] = "success"

    return JsonResponse(return_obj)



