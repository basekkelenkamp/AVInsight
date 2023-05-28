var socket = io.connect('http://' + document.domain + ':' + location.port + '/metrics');

let data = {
    labels: [],
    series: [[]]
};

let options = {
    fullWidth: true,
    showArea: true,
    showLabel: false,
    chartPadding: 0,
    axisY: {
        high: 100,
        low: 0,
        scaleMinSpace: 40,
    },
    axisX: {
        showLabel: false,
        offset: 4
    }
};

function bytesToMegabytes(bytes) {
    return bytes / (1024 * 1024);
}

function megabytesToBytes(megabytes) {
    return megabytes * (1024 * 1024);
}


function init() {
    let charts = document.getElementsByClassName("ct-chart");

    let d = document.querySelector("#dataSelector");
    let interval = d.dataset.interval;

    let thresholds = {
        'gpu': d.dataset.thresholdgpu,
        'cpu': d.dataset.thresholdcpu,
        'ram': d.dataset.thresholdram
    };

    for (let c of charts) {

        let metricType = c.id.slice(0, 3);
        let thresholdValue = thresholds[metricType];

        let chartOptions = {...options};
        if (c.id === 'disk-read-speed-chart') {
            chartOptions.axisY.high = megabytesToBytes(500)
            chartOptions.axisY.labelInterpolationFnc = function (value) {
                return bytesToMegabytes(value).toFixed(0) + ' MB/s';
            };
        } else {
            chartOptions.axisY.labelInterpolationFnc = function (value) {
                return value + '%';
            };
        }
        
        let chart = new Chartist.Line('#' + c.id, data, chartOptions);

        // Add a threshold line at 75% for all charts except 'disk-read-speed-chart'
        if (c.id !== 'disk-read-speed-chart') {

            chart.on('created', function(context) {
                var threshold = {
                    value: thresholdValue,
                    class: 'threshold',
                    axisX: context.axisX,
                    axisY: context.axisY
                };
                var targetLineY = context.chartRect.y1 - (context.chartRect.height() * (threshold.value / 100));
                context.svg.elem('line', {
                    x1: context.chartRect.x1,
                    x2: context.chartRect.x2,
                    y1: targetLineY,
                    y2: targetLineY
                }, threshold.class);
            });
        }
        
        socket.on(c.id, function (receivedData) {
            let new_data_point = receivedData.data;

            chart.update({
                labels: new_data_point,
                series: [chart.data.series[0].concat(new_data_point)]
            });

            if (chart.data.series[0].length > 30) {  
                chart.data.labels.splice(0, 1);
                chart.data.series[0].splice(0, 1);
            }
        });
    }
}
init();
