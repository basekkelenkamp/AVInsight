// Init
let minuteChart = document.getElementById("minute-metrics-chart");
let thresholds = JSON.parse(document.querySelector("#dataThresholds").dataset.thresholds)
let minuteData = JSON.parse(document.querySelector("#dataMinute").dataset.minute_data)

console.log(thresholds)
console.log(minuteData)

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

function extract_data_points_no_minutes(metric) {
    let timestamps
    let data

    // extract data


    return [timestamps, data]
}

function extract_data_points_with_minutes(metric, lineType) {
    let timestamps
    let data
    
    // extract data


    return [timestamps, data]
}


function draw_minute_graph(metric, lineType) {
    console.log("Metric: ", metric);
    console.log("Line: ", lineType);

    let thresholdValue = thresholds[metric];
    let is_disk = metric === 'DISK'

    let data = undefined
    let timestamps = undefined
    if (lineType === 'all') {
        [timestamps, data] = extract_data_points_no_minutes(metric)
    } else {
        [timestamps, data] = extract_data_points_with_minutes(metric, lineType)

    }

    let chartOptions = {...options};
    if (is_disk) {
        chartOptions.axisY.high = megabytesToBytes(500)
        chartOptions.axisY.labelInterpolationFnc = function (value) {
            return bytesToMegabytes(value).toFixed(0) + ' MB/s';
        };
    } else {
        chartOptions.axisY.labelInterpolationFnc = function (value) {
            return value + '%';
        };
    }
    
    let chart = new Chartist.Line('#minute-metrics-chart', data, chartOptions);

    if (!is_disk) {
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
}
  

let selectMetricGraph = document.getElementById('select-graph-metric');
let selectLine = document.getElementById('select-graph-line');

selectMetricGraph.addEventListener('change', function() {
    draw_minute_graph(this.value, selectLine.value); 
});
  
selectLine.addEventListener('change', function() {
    draw_minute_graph(selectMetricGraph.value, this.value); 
});


function init() {
    draw_minute_graph(selectMetricGraph.value, selectLine.value)
}
init();
