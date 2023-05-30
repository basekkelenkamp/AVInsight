let minuteChart = document.getElementById("minute-metrics-chart");
let thresholds = JSON.parse(document.querySelector("#dataThresholds").dataset.thresholds)
let minuteData = JSON.parse(document.querySelector("#dataMinute").dataset.minute_data)
let dailyData = JSON.parse(document.querySelector("#dataDaily").dataset.daily_data)

console.log(dailyData)
let options = {
    fullWidth: true,
    showArea: true,
    showLabel: false,
    chartPadding: {
        top: 30,
        right: 0,
        bottom: 0,
        left: 5,
    },
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
            timestamps.push(minData[0].split(' ')[1])
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

    let chartTitle = document.getElementById("main-chart-title")
    chartTitle.textContent = metric

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
        chartOptions.axisY.high = 100
        chartOptions.axisY.labelInterpolationFnc = function (value) {
            return value + '%';
        };
    }

    let chartData = {
        labels: [timestamps],
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

    let tooltipTimeout;
    let labelElement;

    chart.on('draw', function (data) {
        if (data.type === 'point') {
            // Increase the hover area around the point
            let hoverArea = document.createElementNS(
                'http://www.w3.org/2000/svg',
                'rect'
            );
            hoverArea.setAttribute('x', data.x - 5);
            hoverArea.setAttribute('y', data.y - 5);
            hoverArea.setAttribute('width', 10);
            hoverArea.setAttribute('height', 10);
            hoverArea.setAttribute('style', 'opacity: 0;');

            data.group._node.appendChild(hoverArea);

            hoverArea.addEventListener('mouseenter', function (event) {
                let labelValue = timestamps[data.index];
                showLabel(event.clientX, event.clientY, labelValue);
            });
            hoverArea.addEventListener('mouseleave', function (event) {
                hideLabel();
            });
        }
    });

    function showLabel(x, y, value) {
        if (labelElement) {
            labelElement.parentNode.removeChild(labelElement);
        }

        labelElement = document.createElement('div');
        labelElement.className = 'chart-label';
        labelElement.textContent = value;

        labelElement.style.position = 'fixed';
        labelElement.style.top = y - 30 + 'px';
        labelElement.style.left = x + 'px';

        document.body.appendChild(labelElement);

        clearTimeout(tooltipTimeout);
    }

    function hideLabel() {
        tooltipTimeout = setTimeout(function () {
            if (labelElement) {
                labelElement.parentNode.removeChild(labelElement);
                labelElement = null;
            }
        }, 500);
    }
}


function draw_gauge_chart(metric, data_type) {
    let gaugeElement = document.getElementById(`gauge-chart-${metric}`);
    gaugeElement.style.transform = "scale(1.75)";
    gaugeElement.style.transformOrigin = "top";
    gaugeElement.style.transform = "translateX(-100px)";


    // remove the old chart if it exists
    while (gaugeElement.firstChild) {
        gaugeElement.firstChild.remove();
    }

    let gaugeData = dailyData.find((data) => data[metric] !== undefined)[metric][data_type];

    let gaugeChart = new Chartist.Pie(`#gauge-chart-${metric}`, {
        series: [gaugeData, 100 - gaugeData]
    }, {
        donut: true,
        donutWidth: 40,
        startAngle: 270,
        total: 200, // halfway donut
        labelInterpolationFnc: function (value) {
            return value + '%';
        },
    });

    let labelCount = 0;

    gaugeChart.on('draw', function (data) {
        if (!gaugeElement.style.transform) {
            gaugeElement.style.transform = "scale(1.75)";
        }
        gaugeElement.style.transform = "scale(1.75)";
        gaugeElement.style.transformOrigin = "top";
        if (data.type === 'label') {
            if (labelCount === 1) {
                data.element.attr({
                    style: 'display: none'
                });
            } else {
                // Adjust the font size and color as needed
                data.element.attr({
                    style: 'font-size: 50%; fill: #F2F2F3;' // fill color is the text color
                });
            }
            labelCount++;
        }
    });
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
    const cycleButton = document.getElementById('cycleButton')
    cycleButton.innerHTML = `Cycle<br>(current: daily_max)`
}


document.addEventListener('DOMContentLoaded', function () {
    init()

    let dateInput = document.getElementById('custom-date')
    dateInput.addEventListener('change', function () {
        let newDate = this.value;
        window.location.href = `/data_report/${newDate}`
    });

    const cycleKeys = ['daily_max', 'daily_avg']
    let currentKeyIndex = 0
    const cycleButton = document.getElementById('cycleButton')
    cycleButton.addEventListener('click', function () {
        currentKeyIndex = (currentKeyIndex + 1) % cycleKeys.length

        for (let metric of Object.keys(minuteData)) {
            if (metric !== 'DISK') {
                cycleButton.innerHTML = `Cycle<br>(current: ${cycleKeys[currentKeyIndex]})`
                draw_gauge_chart(metric, cycleKeys[currentKeyIndex])
            }
        }
    });

    let gaugeInfoElement = document.getElementById('gaugeInfo')

    for (let metric of Object.keys(minuteData)) {
        if (metric !== 'DISK') {
            let title = document.getElementById('gauge-title-' + metric)
            title.textContent = metric + " (" + dailyData.find((data) => data[metric] !== undefined)[metric]['daily_counts'] + ")"
            draw_gauge_chart(metric, cycleKeys[currentKeyIndex])
        }
    }
});
