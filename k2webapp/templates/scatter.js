var data = {{ scatter['data'] }}
var xlabel = "BJD - 2454833"
var ylabel = "{{ scatter['ylabel'] }}"
var title = "{{ scatter['title'] }}"
var subtitle = "Click to zoom"

$(function () {
    $('#scatter').highcharts({
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
        series: [{
            name: 'Phot',
            color: 'rgba(223, 83, 83, .5)',
            data: data
          }]
    });
});



