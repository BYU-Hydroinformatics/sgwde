/*****************************************************************************
 * FILE:    SGWDE MAIN.JS
 * DATE:    14 APRIL 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var SGWDE_PACKAGE = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/


    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var get_plot,$get_plot,init_jquery_var;


    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    init_jquery_var=function(){
        $get_plot = $('#get-plot');
    };

    get_plot = function(){
        var datastring = $get_plot.serialize();
        $.ajax({
            type:"POST",
            url:'/apps/sgwde/get-plot/',
            dataType:'HTML',
            data:datastring,
            success:function(result){
                var json_response = JSON.parse(result);
                if(json_response.status === 'success'){
                    $(".plot").html('');
                    var png_file = json_response.png_file;
                    var img = document.createElement("IMG");
                    img.src = '/static/sgwde/wrf_plots/'+png_file;
                    img.height = "500";
                    img.width = "800";
                    document.getElementById('plot').appendChild(img);


                }
            }
        });
    };

    $("#btn-get-plot").on('click',get_plot);


    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/


    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    $(function() {
        init_jquery_var();

    });



}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.