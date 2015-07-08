var data = [[1,1],[3,2],[4,1]]
var xlabel = 'BJD - XXX'
var ylabel = 'Flux' 
$(function () {
    $('#container').highcharts({
        chart: {
            type: 'scatter',
            zoomType: 'xy',

        },
        title: {
            text: 'Photometry'
        },
        subtitle: {
            text: 'Click Region to Zoom'
        },
        xAxis: {
            title: {
                enabled: true,
                text: xlabel
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true,

        },
        yAxis: {
            lineWidth: 0,
            minorGridLineWidth: 0,
            title: {
                text: ylabel
            }
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 3,
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
            },
            series: {
             animation: false
        }
        },
        series: [{
            color: 'rgba(223, 83, 83, .5)',
            data: data
        }]
    });
});


