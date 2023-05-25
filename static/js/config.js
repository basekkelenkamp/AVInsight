document.getElementById('save-config').addEventListener('click', saveConfig);

document.getElementById('config-form').addEventListener('change', function () {
  document.getElementById('save-config').disabled = false;
  document.getElementById('save-config').innerHTML = 'Save';
});

document.getElementById('config-form').addEventListener('keydown', function (event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // Prevent form submission
    saveConfig();
  }
});

document.querySelectorAll('input[type=number]').forEach(function(input) {
  input.addEventListener('input', function(event) {
    let dataType = event.target.dataset.type; // Access the data-type attribute
    let step = 1;
    let value = parseFloat(event.target.value);
    if (dataType === "float") {
      step = 0.1;
      if (event.target.value.slice(-1) === '.') {
        return; // If the last character is a dot, do not change the value
      }
      value = Math.round(value * 10) / 10; // Round to 1 decimal place
    }
    // Ensure value is within the range 0-99
    value = Math.min(Math.max(value, 0), 99);
    event.target.value = isNaN(value) ? '' : value;
  });
  input.addEventListener('wheel', function(event) {
    event.preventDefault();
    let dataType = event.target.dataset.type; // Access the data-type attribute
    let step = dataType === "float" ? 0.1 : 1;
    let value = parseFloat(event.target.value) + (event.deltaY < 0 ? step : -step);
    if (dataType === "float") {
      value = Math.round(value * 10) / 10; // Round to 1 decimal place
    }
    // Ensure value is within the range 0-99
    value = Math.min(Math.max(value, 0), 99);
    event.target.value = isNaN(value) ? '' : value;
  });
});

function saveConfig() {
  const form = document.getElementById('config-form');
  const formData = new FormData(form);
  const updatedConfig = {
    "metrics": [],
    "archive": [],
    "thresholds": []
  };

  let tempSetting = { "name": undefined, "value": undefined, "description": undefined, "category": undefined, "datatype": undefined }

  for (const [key, value] of formData.entries()) {
    console.log(`key: ${key}. value: ${value}`)
    
    const [section, settingName] = key.split('-', 2)

    if (key.includes("-description")) {
      tempSetting.description = value
    } else if (key.includes("-category")) {
      tempSetting.category = value
    } else if (key.includes("-datatype")) {
      tempSetting.datatype = value
    } else {
      tempSetting.name = settingName
      tempSetting.value = typeof value === 'boolean' ? String(value) : value
      tempSetting.value = value === 'on' ? "true" : value
    }

    if (!Object.values(tempSetting).every(value => value !== undefined)) {
      continue
    }

    let settingObject = tempSetting
    tempSetting = tempSetting = { "name": undefined, "value": undefined, "description": undefined, "category": undefined, "datatype": undefined }
    updatedConfig[section].push(settingObject)
  }

  // Send updatedConfig to Flask backend
  fetch('/save-config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updatedConfig)
  })
  .then(response => {
    if (response.ok) {
      console.log('Config updated successfully');
      document.getElementById('save-config').disabled = true;
      document.getElementById('save-config').innerHTML = 'Saved';
    } else {
      console.log('Error updating config');
    }
  });
}
