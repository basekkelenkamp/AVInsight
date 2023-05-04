document.getElementById('save-config').addEventListener('click', function() {
    const form = document.getElementById('config-form');
    const formData = new FormData(form);
    const updatedConfig = {
      "metrics": [],
      "archive": []
    };
  
    for (const [key, value] of formData.entries()) {
      const [section, configKey] = key.split('-', 2);
      const input = document.getElementById(key);
      let processedValue;
  
      if (input.type === 'checkbox') {
        processedValue = input.checked;
      } else {
        processedValue = isNaN(value) ? value : Number(value);
      }
  
      const configItem = {};
      configItem[configKey] = processedValue;
      updatedConfig[section].push(configItem);
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
      } else {
        console.log('Error updating config');
      }
    });
  });
  