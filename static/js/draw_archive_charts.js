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
        showLabel: true,
        offset: 4
    }
};

function draw_chart(chart_id, chart_data, chart_labels) {
    let chartOptions = { ...options };

    let data = {
        labels: chart_labels,
        series: [chart_data]
    };

    let chart = new Chartist.Line('#' + chart_id, data, chartOptions);
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
    let d = document.querySelector("#dataSelector")

    const metric_values = JSON.parse(d.dataset.metricvalues)
    const metric_names = JSON.parse(d.dataset.metricnames)

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

        console.log("Creating chart: ", metric.type)
        draw_chart(chart_id, chart_data, chart_labels);
    }
}
init();
