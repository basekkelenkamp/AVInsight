// Init
let minuteChart = document.getElementById("minute-metrics-chart");
let thresholds = JSON.parse(document.querySelector("#dataThresholds").dataset.thresholds)
let minuteData = JSON.parse(document.querySelector("#dataMinute").dataset.minute_data)

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
}

// function create_main_chart_element() {
//     let existingElement = document.getElementById("minute-metrics-chart");
//     if(existingElement) {
//         existingElement.remove();
//     }

//     let newElement = document.createElement("div");
//     newElement.id = "minute-metrics-chart";
//     newElement.classList.add("ct-chart", "ct-double-octave");

//     let parentContainer = document.getElementById("main-chart");

//     parentContainer.appendChild(newElement);
// }


function bytesToMegabytes(bytes) {
    return bytes / (1024 * 1024);
}

function megabytesToBytes(megabytes) {
    return megabytes * (1024 * 1024);
}

function extract_data_points_no_minutes(metric) {
    let timestamps = []
    let values = []
    let data = minuteData[metric]

    Object.keys(data).forEach(function (minute) {
        for (let minData of data[minute]['values']) {
            timestamps.push(minData[0])
            values.push(minData[1])
        }
    });

    return [timestamps, values]
}

function extract_data_points_with_minutes(metric, lineType) {
    let timestamps = []
    let values = []
    let data = minuteData[metric]
    let key

    if (lineType === 'average') {
        key = 'avg'
    } else if (lineType === 'min' || lineType === 'max') {
        key = 'minmax'
    }

    Object.keys(data).forEach(function (minute) {
        timestamps.push(minute)
        if (key === 'minmax') {
            if (lineType === 'min') {
                values.push(data[minute][key][0]);
            } else if (lineType === 'max') {
                values.push(data[minute][key][1]);
            }
        } else {
            values.push(data[minute][key]);
        }
    });

    return [timestamps, values]
}



function draw_minute_graph(metric, lineType) {
    let thresholdValue = thresholds[metric];
    let is_disk = metric === 'DISK'

    let data = []
    let timestamps = []

    if (lineType === 'all') {
        [timestamps, data] = extract_data_points_no_minutes(metric)
    } else {
        [timestamps, data] = extract_data_points_with_minutes(metric, lineType)
    }

    console.log(`linetype: ${lineType}, metric: ${metric}`)
    console.log(timestamps)
    console.log(data)

    let chartOptions = { ...options };
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

    let chartData = {
        labels: [],
        series: [data]
    };

    let chart = new Chartist.Line('#minute-metrics-chart', chartData, chartOptions);

    if (!is_disk) {
        chart.on('created', function (context) {
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

selectMetricGraph.addEventListener('change', function () {
    draw_minute_graph(this.value, selectLine.value);
});

selectLine.addEventListener('change', function () {
    draw_minute_graph(selectMetricGraph.value, this.value);
});


function init() {
    draw_minute_graph(selectMetricGraph.value, selectLine.value)
}

document.addEventListener('DOMContentLoaded', function () {
    init();
});

