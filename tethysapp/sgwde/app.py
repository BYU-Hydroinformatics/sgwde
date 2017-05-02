from tethys_sdk.base import TethysAppBase, url_map_maker


class ServirGriddedWaterObservationsExplorer(TethysAppBase):
    """
    Tethys app class for Servir Gridded Water Observations Explorer.
    """

    #Note: All of these parameters can be changed through the Site Admin Portal --> Tethys Apps --> Installed Apps
    name = 'Servir Gridded Water Observations Explorer'
    index = 'sgwde:home'
    icon = 'sgwde/images/logo.png'
    package = 'sgwde'
    root_url = 'sgwde'
    color = '#004de6'   #Change this to change the primary color of the website
    description = ''    #Change this to change the description of the app
    tags = ''
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='sgwde',
                           controller='sgwde.controllers.home'), #Home Page controller (See controllers.py). Responsible for creating variable and date dropdowns.
                    UrlMap(name='get-plot',
                           url='sgwde/get-plot',
                           controller='sgwde.controllers.get_plot'), #Get Plot controller (See controllers.py). Gets triggered when you click submit button on the homepage.
                    UrlMap(name='upload-shp',
                           url='sgwde/upload-shp',
                           controller='sgwde.controllers_ajax.upload_shp'),#Upload Shapefile Controller (See controllers_ajax.py). Gets triggered when you click upload shapefile.
                    UrlMap(name='api_get_var_list',
                           url='sgwde/api/GetVariableList',
                           controller='sgwde.api.api_get_var_list'), #Get Variables API call. See api.py.
                    UrlMap(name='api_get_available_dates',
                           url='sgwde/api/GetAvailableDates',
                           controller='sgwde.api.api_get_available_dates'), #Get Available Dates API call. See api.py
                    UrlMap(name='api_get_point_values',
                           url='sgwde/api/GetPointValues',
                           controller='sgwde.api.api_get_point_values'), # Get values for a point API call. See api.py
                    UrlMap(name='api_get_polygon_values',
                           url='sgwde/api/GetPolygonValues',
                           controller='sgwde.api.api_get_polygon_values'), #Get values for polyon bounds API call. See api.py
        )

        return url_maps