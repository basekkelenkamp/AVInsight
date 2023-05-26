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
    let minuteChart = document.getElementById("minute-metrics-chart");


    let dThres = document.querySelector("#dataThresholds").dataset.thresholds;
    let dMinute = document.querySelector("#dataMinute").dataset.minute_data;

    let thresholds = JSON.parse(dThres)
    let minuteData = JSON.parse(dMinute)

    console.log(thresholds)
    console.log(minuteData)
    console.log(minuteChart)

    // let metricType = c.id.slice(0, 3);
    // let thresholdValue = thresholds[metricType];

    // let chartOptions = {...options};
    // if (c.id === 'disk-read-speed-chart') {
    //     chartOptions.axisY.high = megabytesToBytes(500)
    //     chartOptions.axisY.labelInterpolationFnc = function (value) {
    //         return bytesToMegabytes(value).toFixed(0) + ' MB/s';
    //     };
    // } else {
    //     chartOptions.axisY.labelInterpolationFnc = function (value) {
    //         return value + '%';
    //     };
    // }
    
    // let chart = new Chartist.Line('#' + c.id, data, chartOptions);

    // // Add a threshold line at 75% for all charts except 'disk-read-speed-chart'
    // if (c.id !== 'disk-read-speed-chart') {

    //     chart.on('created', function(context) {
    //         var threshold = {
    //             value: thresholdValue,
    //             class: 'threshold',
    //             axisX: context.axisX,
    //             axisY: context.axisY
    //         };
    //         var targetLineY = context.chartRect.y1 - (context.chartRect.height() * (threshold.value / 100));
    //         context.svg.elem('line', {
    //             x1: context.chartRect.x1,
    //             x2: context.chartRect.x2,
    //             y1: targetLineY,
    //             y2: targetLineY
    //         }, threshold.class);
    //     });
    // }
}
init();
