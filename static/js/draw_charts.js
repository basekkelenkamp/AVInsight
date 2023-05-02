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
        top: 40
    },
    axisY: {
        high: 100,
        low: 0,
        scaleMinSpace: 40
    }
};

let maxDiskReadSpeed = 0;

function init() {
    let charts = document.getElementsByClassName("ct-chart");

    for (let c of charts) {
        let chartOptions = {...options};
        if (c.id === 'disk-read-speed-chart') {
            chartOptions.axisY.labelInterpolationFnc = function (value) {
                return (value / 1024 / 1024).toFixed(2) + ' MB/s';
            };
            chartOptions.axisY.high = 1024 * 100;
        } else {
            chartOptions.axisY.labelInterpolationFnc = function (value) {
                return value + '%';
            };
        }

        let chart = new Chartist.Line('#' + c.id, data, chartOptions);

        socket.on(c.id, function (receivedData) {
            var new_data_point = receivedData.data;
            var labels = receivedData.labels;

            if (c.id === 'disk-read-speed-chart') {
                let diskReadSpeeds = Object.values(new_data_point);
                maxDiskReadSpeed = Math.max(maxDiskReadSpeed, ...diskReadSpeeds);
                chart.options.axisY.high = maxDiskReadSpeed * 1.1;
                new_data_point = [diskReadSpeeds.reduce((a, b) => a + b, 0)]; // Sum all disk read speeds
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
