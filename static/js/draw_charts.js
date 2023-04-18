var socket = io.connect('http://' + document.domain + ':' + location.port + '/metrics');

var data = {
    labels: [],
    series: [[]]
}

var options = {
    fullWidth: true,
    showArea: true,
    chartPadding: {
        right: 40
    },
    axisY: {
        high: 100,
        low: 0,
        scaleMinSpace: 40,
        labelInterpolationFnc: function(value) {
            return value + '%';
        }
    }
}

function init() {
    let charts = document.getElementsByClassName("ct-chart");

    for (let c of charts) {
        let chart = new Chartist.Line('#' + c.id, data, options);

        socket.on(c.id, function (data) {
            var labels = data.labels;
            var new_data_point = data.data;
        
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
init()


// var cpu_chart = new Chartist.Line('#cpu-usage-chart', data, options);
// var ram_chart = new Chartist.Line('#ram-usage-chart', data, options);

// socket.on('cpu_usage', function (data) {
//     var labels = data.labels;
//     var new_data_point = data.data;

//     chart.update({
//         labels: labels,
//         series: [chart.data.series[0].concat(new_data_point)]
//     });

//     if (chart.data.series[0].length > 30) {
//         chart.data.labels.splice(0, 1);
//         chart.data.series[0].splice(0, 1);
//     }
// });

// socket.on('ram_usage', function (data) {
//     var labels = data.labels;
//     var new_data_point = data.data;

//     chart.update({
//         labels: labels,
//         series: [chart.data.series[0].concat(new_data_point)]
//     });

//     if (chart.data.series[0].length > 30) {
//         chart.data.labels.splice(0, 1);
//         chart.data.series[0].splice(0, 1);
//     }
// });
