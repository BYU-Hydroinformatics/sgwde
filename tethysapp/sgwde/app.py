from tethys_sdk.base import TethysAppBase, url_map_maker


class ServirGriddedWaterObservationsExplorer(TethysAppBase):
    """
    Tethys app class for Servir Gridded Water Observations Explorer.
    """

    name = 'Servir Gridded Water Observations Explorer'
    index = 'sgwde:home'
    icon = 'sgwde/images/logo.png'
    package = 'sgwde'
    root_url = 'sgwde'
    color = '#004de6'
    description = ''
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
                           controller='sgwde.controllers.home'),
                    UrlMap(name='get-plot',
                           url='sgwde/get-plot',
                           controller='sgwde.controllers.get_plot'),
        )

        return url_maps