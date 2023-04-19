var socket = io.connect('http://' + document.domain + ':' + location.port + '/metrics');

var data = {
    labels: [],
    series: [[]]
};

var options = {
    fullWidth: true,
    showArea: true,
    chartPadding: {
        right: 40,
        top: 40 // Add padding to the top of the chart area
    },
    axisY: {
        high: 100,
        low: 0,
        scaleMinSpace: 40,
        labelInterpolationFnc: function (value) {
            return value + '%';
        }
    }
};

let maxDiskReadSpeed = 0;

function init() {
    let charts = document.getElementsByClassName("ct-chart");

    for (let c of charts) {
        let chartOptions = { ...options };
        if (c.id === 'disk-read-speed-chart') {
            chartOptions.axisY.labelInterpolationFnc = function (value) {
                return (value / 1024 / 1024).toFixed(2) + ' MB/s';
            };
            chartOptions.axisY.high = 1024 * 100; // Set a maximum value based on your expected disk read speed
        }

        let chart = new Chartist.Line('#' + c.id, data, chartOptions);

        socket.on(c.id, function (data) {
            var labels = data.labels;
            var new_data_point = data.data;

            if (c.id === 'disk-read-speed-chart') {
                maxDiskReadSpeed = Math.max(maxDiskReadSpeed, ...new_data_point);
                chart.options.axisY.high = maxDiskReadSpeed * 1.1; // Add 10% buffer to the maximum value
            }

            chart.update({
                labels: labels,
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
