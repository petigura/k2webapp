var data_phot = {{ scatter_phasefold['data_phot'] }};
var data_even = {{ scatter_phasefold['data_even'] }};
var data_odd = {{ scatter_phasefold['data_odd'] }};
var data_fit = {{ scatter_phasefold['data_fit'] }};
var title = "Phase-folded photometry";
var subtitle = "Click to zoom";

$(function () {
    $('#scatter_phasefold').highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy'
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
                text: 'Time Since Mid-transit (days)'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Normalized Flux - 1'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'bottom',
            verticalAlign: 'right',
//            x: 100,
//            y: 70,
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
            name: 'Fit',
            data: data_fit,
	    lineWidth: 3
	},
	{
            name: 'Even',
            data: data_even,
	},
	{
            name: 'Odd',
            data: data_odd,
	}
	]
    });
});
