from django.http import JsonResponse, Http404, HttpResponse
from utilities import *
import json
import shapely.geometry


def upload_shp(request):

    return_obj = {
        'success':False
    }

    if request.is_ajax() and request.method == 'POST':


        file_list = request.FILES.getlist('files')
        shp_json = convert_shp(file_list)
        gjson_obj = json.loads(shp_json)
        geometry = gjson_obj["features"][0]["geometry"]
        shape_obj = shapely.geometry.asShape(geometry)
        poly_bounds = shape_obj.bounds
        return_obj["bounds"] = poly_bounds
        return_obj["geo_json"] = gjson_obj
        return_obj["success"] = True

    return JsonResponse(return_obj)
