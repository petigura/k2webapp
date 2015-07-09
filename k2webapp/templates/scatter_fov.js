Highcharts.setOptions({
   plotOptions: {
      series: {
         animation: false
      }
   }
})

var field_star_coords = {{ scatter_fov['field_star_coords'] }};
var target_star_coords = {{ scatter_fov['target_star_coords'] }};
var starname = "{{ starname }} ";
var xlabel = "RA (deg)"; 
var ylabel = "Dec (Deg)";

$(function () {
    $('#scatter_fov').highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: 'Location of {{starname}} on FOV'
        },
        xAxis: {
            title: {
                enabled: true,
                text: xlabel
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: ylabel
            }
        },

        plotOptions: {
            scatter: {
                marker: {
                    radius: 2,
                    states: {
                        hover: {
                            enabled: true,
                            lineColor: 'rgb(100,100,100)'
                        }
                    }
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: '{point.x}, {point.y}'
                }
            }
        },
        series: [
	    {
		name: 'K2 Target Stars',
		data: field_star_coords
	    },
	    {
		name: starname,
		marker: {radius: 10,},
		data: target_star_coords
	    }
	]
    });
 });





