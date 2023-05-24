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

function saveConfig() {
  const form = document.getElementById('config-form');
  const formData = new FormData(form);
  const updatedConfig = {
    "metrics": [],
    "archive": []
  };

  let tempSetting = { "name": undefined, "value": undefined, "description": undefined }

  for (const [key, value] of formData.entries()) {
    console.log(`key: ${key}. value: ${value}`)

    const [section, settingName] = key.split('-', 2)

    if (key.includes("-description")) {
      tempSetting.description = value
    } else {
      tempSetting.name = settingName
      tempSetting.value = typeof value === 'boolean' ? String(value) : value
      tempSetting.value = value === 'on' ? "true" : value
    }

    if (!Object.values(tempSetting).every(value => value !== undefined)) {
      continue
    }

    let settingObject = tempSetting
    tempSetting = { "name": undefined, "value": undefined, "description": undefined }
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
