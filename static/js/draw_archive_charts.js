let options = {
    fullWidth: true,
    showArea: true,
    showLabel: true,
    chartPadding: 0,
    axisY: {
        high: 100,
        low: 0,
        scaleMinSpace: 40,
    },
    axisX: {
        offset: 4
    }
};

function bytesToMegabytes(bytes) {
    return bytes / (1024 * 1024);
}

function megabytesToBytes(megabytes) {
    return megabytes * (1024 * 1024);
}

function draw_chart(chart_id, chart_data, chart_labels) {
    let chartOptions = { ...options };

    let data = {
        labels: chart_labels,
        series: [chart_data]
    };

    if (chart_id === 'metric-chart-4') {
        chartOptions.axisY.high = megabytesToBytes(500)
        chartOptions.axisY.labelInterpolationFnc = function (value) {
            return bytesToMegabytes(value).toFixed(0) + ' MB/s';
        };
    }

    let chart = new Chartist.Line('#' + chart_id, data, chartOptions);

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
                let labelValue = chart_labels[data.index];
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
        labelElement.textContent = value.split(' ')[1];

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

function group_by(arr, key) {
    return arr.reduce(function (rv, x) {
        (rv[x[key]] = rv[x[key]] || []).push(x);
        return rv;
    }, {});
}

function sort_by(arr, key) {
    return arr.sort(function (a, b) {
        return new Date(a[key]) - new Date(b[key]);
    });
}

function init() {
    let d = document.querySelector("#dataSelector");

    const metric_values = JSON.parse(d.dataset.metricvalues);
    const metric_names = JSON.parse(d.dataset.metricnames);

    let grouped_data = group_by(metric_values, 'metric_id');
    for (let metric of metric_names) {
        let metric_data = grouped_data[metric.id];
        if (!metric_data) {
            continue;
        }

        metric_data = sort_by(metric_data, 'timestamp');

        let chart_id = 'metric-chart-' + metric.id;
        let chart_data = metric_data.map(d => parseFloat(d.value));
        let chart_labels = metric_data.map(d => d.timestamp);

        console.log("Creating chart: ", metric.type);
        draw_chart(chart_id, chart_data, chart_labels);
    }
}

init();
