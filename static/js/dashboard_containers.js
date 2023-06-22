var socket = io.connect('http://' + document.domain + ':' + location.port + '/metrics');

function calculateAverage(arr) {
    let sum = arr.reduce((a, b) => a + b, 0);
    return sum / arr.length;
}

function bytesToMegabytes(bytes) {
    return bytes / (1024 * 1024);
}

function getColorForPercentage(pct) {
    let percent = Math.max(Math.min(pct, 100), 0) / 100;
    let color1 = [25, 198, 34];
    let color2 = [230, 57, 70];
    let color = [0, 0, 0];
    for (let i = 0; i < 3; i++) {
        color[i] = Math.round(color1[i] + percent * (color2[i] - color1[i]));
    }
    return `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
}
    
function init() {
    let charts = document.getElementsByClassName("ct-chart");

    let incomingData = {
        "gpu": [],
        "cpu": [],
        "ram": [],
        "disk": []
    }

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
                container.innerHTML = `Read speed ${key.toUpperCase()}: <span style="color: rgb(25, 198, 34)"><b>${bytesToMegabytes(incomingData[key].slice(-1)).toFixed(2)} MB/s</b></span>`;

            } else {
                let average = calculateAverage(incomingData[key]);
                let color = getColorForPercentage(average); // get color for average
                container.innerHTML = `Average ${key.toUpperCase()}: <span style="color: ${color}"><b>${average.toFixed(2)}%</b></span>`;
            }
        });
    }
}

init();

let container = document.getElementById('warning-container-content');
container.scrollTop = container.scrollHeight;
