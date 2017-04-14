from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
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
from tethys_sdk.gizmos import SelectInput
# from datetime import datetime, timedelta

@login_required()
def home(request):
    """
    Controller for the app home page.

    """

    variable_options = [('Total Accumulated Precipitation(mm)','TACC_PRECIP'),('Total Rainfall Accumulation(mm)','TACC_RAIN'),('Total Snow/Ice Accumulation(mm)','TACC_SNICE'),('Maximum Composite reflectivity(dbz)','REFC_MAX'),('Maximum 10 M wind speed(m s-1)','S10_MAX'),('Maximum Column Integrated Graupel(kg m-2)','GCOLMAX'),('1 to 6km Maximum Updraft Helicity(m2 s-2)','UDHELI16_MAX'),('Period Maximum Rainfall Rate (mm s-1)','MAX_RRATE'),('Period Maximum Snow + Graupel Precipitation Rate(mm s-1)','MAX_SFRATE'),('Mean Shelter Temperature(K)','T02_MEAN')]
    select_variable = SelectInput(display_text='Select WRF Variable',
                                  name='select_variable',
                                  multiple=False,
                                  options=variable_options,
                                  initial=['Total Accumulated Precipitation(mm)'])

    date_options = get_times()

    select_date = SelectInput(display_text='Select WRF Forecast Date',
                                  name='select_date',
                                  multiple=False,
                                  options=date_options,
                                  initial=['2017-03-09 18:00:00'])

    context = {"select_variable":select_variable,"select_date":select_date}


    return render(request, 'sgwde/home.html', context)

def get_plot(request):
    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        variable = request.POST['select_variable']
        date = request.POST['select_date']
        date = date.replace(' ','_')
        png_file = date+'_'+variable+'.png'
        return_obj["png_file"] = png_file
        return_obj["status"] = "success"

    return JsonResponse(return_obj)



