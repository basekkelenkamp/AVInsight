var socket = io.connect('http://' + document.domain + ':' + location.port + '/metrics');

function calculateAverage(arr) {
    let sum = arr.reduce((a, b) => a + b, 0);
    return sum / arr.length;
}

function bytesToMegabytes(bytes) {
    return bytes / (1024 * 1024);
}


function init() {
    let charts = document.getElementsByClassName("ct-chart");

    let d = document.querySelector("#dataSelector");
    let interval = d.dataset.interval;

    let incomingData = {
        "gpu": [],
        "cpu": [],
        "ram": [],
        "disk": []
    }

    document.getElementById("interval").textContent = `Data interval: ${interval}s`;

    for (let chart of charts) {
        let key = chart.id.split("-")[0];
        socket.on(chart.id, function (receivedData) {
            let new_data_point = receivedData.data;
            incomingData[key].push(new_data_point[0]);

            // Limit the data points to the last 30
            if (incomingData[key].length > 30) {
                incomingData[key].splice(0, 1);
            }

            // Update the info container
            let container = document.getElementById(`info-${key}`);
            if (key == "disk") {
                container.textContent = `Read speed ${key.toUpperCase()}: ${bytesToMegabytes(incomingData[key].slice(-1)).toFixed(2)} MB/s`;

            } else {
                let average = calculateAverage(incomingData[key]);
                container.textContent = `Average ${key.toUpperCase()}: ${average.toFixed(2)}%`;
            }
        });
    }
}

init();
