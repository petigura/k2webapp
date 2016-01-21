var data_out = {{ scatter_trans['data_out'] }}; // Out of transit points
var label_out = "Out of transit";
var data_in = {{ scatter_trans['data_in'] }}; // In transit points
var label_in = "In transit";
var title = ""

// the name in $('').highcharts gives the chart a name so we can refer to it using the <div in the template>
// #scatter_phot+trans didn't work! due to plus sign
$(function () {
    $('#scatter_phottrans').highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy'
        },
	tooltip: {
	    enabled: false
        },
        title: {
            text: title
        },
        subtitle: {
            text: subtitle,
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'BJD - 2454833'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Normalized Flux'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: 100,
            y: 70,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
            borderWidth: 1
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 2,
                    states: {
                        hover: {
                            enabled: false,
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
            }
        },
        series: [
	{
           name: label_out,
           data: data_out
        },
	{
           name: label_in,
           data: data_in
        }
	]
    });
});



