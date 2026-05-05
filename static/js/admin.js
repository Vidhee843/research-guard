const urlParams = new URLSearchParams(window.location.search);

function redirectBack() {
    location.assign(`/publications?session=${urlParams.get("session")}`);
}

function init() {
    getAvailableModels();
    getContributors();
    uploadDataset();
}

function uploadDataset() {
    document.getElementById('upload-dataset').addEventListener('change', async function(event) {
        const loadingText = document.getElementById('loadingText');
        const loadingProgress = document.getElementById('loadingProgress');
        loadingProgress.style.width = 0 + '%';
        loadingText.textContent = 'Uploading: 0%';
        document.getElementById("metric-accuracy").innerHTML = "---";
        document.getElementById("metric-precision-recall").innerHTML = "--- / ---";
        document.getElementById("metric-f1").innerHTML = "---";
        document.getElementById("metric-model").innerHTML = "---";
          document.getElementById("confusion-matrix").innerHTML = `---`
        document.getElementById("confusion-matrix").href = `#`
        const file = event.target.files[0]
        if (!file) return
        const formData = new FormData()
        formData.append('dataset', file)
        fetch(`/api/v1/research/publication/import?session=${urlParams.get("session")}`, {
            method: "POST",
            body: formData,
          }).then(response => {
            if (response.ok) 
              return response.json();
            return Promise.reject(response); 
          })
          .then(json => {
            loadingProgress.style.width = 100 + '%';
            loadingText.textContent = 'Uploading: 100%';
          })
          .catch(error => {
            console.error(error);
            error.json().then(error => {
                alert(error.message)
            });
        });  
    })
}


function getContributors() {
  document.getElementById("contributors-table-body").innerHTML = "";
  fetch(`/api/v1/research/session/contributors?id=${urlParams.get("session")}`, {
    method: "GET",
  }).then(response => {
    if (response.ok) 
      return response.json();
    return Promise.reject(response); 
  })
  .then(json => {
    document.getElementById("owner").innerHTML = `Owner: ${json.data.owner}`;
    json.data.contributors.forEach(function(contributor) {
      document.getElementById("contributors-table-body").innerHTML += `
      <tr>
        <td>${contributor.username}</td>
        <td><button style="background-color: #f85149;" onclick="deleteContributor('${contributor.id}')" class="table-btn">Remove</button></td>
      </tr>
      `
    })
  })
  .catch(error => {
    console.error(error);
    error.json().then(error => {
      alert(error.message)      
    });
  });
}


function deleteContributor(account) {
  fetch(`/api/v1/research/session/contributors?id=${urlParams.get("session")}&account=${account}`, {
    method: "DELETE",
  }).then(response => {
    if (response.ok) 
      return response.json();
    return Promise.reject(response); 
  })
  .then(json => {
    getContributors();
  })
  .catch(error => {
    console.error(error);
    error.json().then(error => {
      alert(error.message)      
    });
  });
}


function logout() {
  fetch(`/api/v1/security/logout`, {
    method: "PUT",
  }).then(response => {
    if (response.ok) 
      return response.json();
    return Promise.reject(response); 
  })
  .then(json => {
    location.assign("/login");
  })
  .catch(error => {
    console.error(error);
    error.json().then(error => {
      alert(error.message)      
    });
  });
}



function getAvailableModels() {
  fetch(`/api/v1/ai/model/all?session=${urlParams.get("session")}`, {
    method: "GET",
  }).then(response => {
    if (response.ok) 
      return response.json();
    return Promise.reject(response); 
  })
  .then(json => {
    let nbActive = document.getElementById("nb-active");
    let rfActive = document.getElementById("rf-active");
    let lsvmActive = document.getElementById("lsvm-active");
    let lrActive = document.getElementById("lr-active");
    const availableModels = json.data || [];
    function updateModelStatus(element, modelName) {
      if (availableModels.includes(modelName)) {
        element.innerHTML = `<span class="status-active">Active</span>`;
      } else {
        element.innerHTML = `<span class="status-active" style="color: #da3633;" >Inactive</span>`;
      }
    }
    updateModelStatus(nbActive, "naive-bayes-model");
    updateModelStatus(rfActive, "random-forest-model");
    updateModelStatus(lsvmActive, "linear-svm-model");
    updateModelStatus(lrActive, "logistic-regression-model");

  })
  .catch(error => {
    console.error(error);
    error.json().then(error => {
      if (isAuthTokenInvalid(error)) 
        location.assign("/login");
      else 
        alert(error.message);
    });
  });
}

function downloadDataset(type) {
  const session = urlParams.get("session");
  window.location.href = `/api/v1/ai/model?session=${session}&type=${type}`;
}


function deleteModel(model) {
  fetch(`/api/v1/ai/model?session=${urlParams.get("session")}&type=${model}`, {
    method: "DELETE",
  }).then(response => {
    if (response.ok) 
      return response.json();
    return Promise.reject(response); 
  })
  .then(json => {
    // Map model name to element id
    const modelIdMap = {
      "naive-bayes-model": "nb-active",
      "random-forest-model": "rf-active",
      "linear-svm-model": "lsvm-active",
      "logistic-regression-model": "lr-active"
    };

    const elementId = modelIdMap[model];
    const element = document.getElementById(elementId);

    if (element) {
      element.innerHTML =`<span class="status-active" style="color: #da3633;" >Inactive</span>`;
    }
  })
  .catch(error => {
    console.error(error);
    error.json().then(error => {
      alert(error.message);     
    });
  });
}

function classifyDataset() {
  const loadingText = document.getElementById('loadingText');
  const loadingProgress = document.getElementById('loadingProgress');
  document.getElementById("confusion-matrix").innerHTML = `---`
  document.getElementById("confusion-matrix").href = `#`
  const model = document.getElementById("classificaton-model").value
  loadingProgress.style.width = '0%';
  loadingText.textContent = 'Classifying: 0%';
  document.getElementById("metric-accuracy").innerHTML = "---";
  document.getElementById("metric-precision-recall").innerHTML = "--- / ---";
  document.getElementById("metric-f1").innerHTML = "---";
  document.getElementById("metric-model").innerHTML = model;
  fetch(`/api/v1/ai/classify?session=${urlParams.get("session")}&type=${model}&override=${document.getElementById("override-checkbox").checked}`, {
    method: "PUT",
  })
  .then(response => {
    if (!response.ok) {
      return Promise.reject(response);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    reader.read().then(function pump({ done, value }) {
      if (done) {
        loadingProgress.style.width = '100%';
        loadingText.textContent = 'Classifying: 100%';
        return;
      }
      const percentage = decoder.decode(value).trim();
      loadingProgress.style.width = percentage;
      loadingText.textContent = `Classifying: ${percentage}`;
      return reader.read().then(pump);
    });
  })
  .catch(error => {
    console.error(error);
    error.json().then(error => {
      alert(error.message);
    }).catch(() => {
      alert("An error occurred during classification.");
    });
  });
}

function train(model) {
  const loadingText = document.getElementById('loadingText');
  const loadingProgress = document.getElementById('loadingProgress');
  loadingProgress.style.width = 0 + '%';
  loadingText.textContent = 'Training: 0%';
  document.getElementById("confusion-matrix").innerHTML = `---`
  document.getElementById("confusion-matrix").href = `#`
  document.getElementById("metric-model").innerHTML = model;
  document.getElementById("metric-accuracy").innerHTML = "---";
  document.getElementById("metric-precision-recall").innerHTML = "--- / ---";
  document.getElementById("metric-f1").innerHTML = "---";
  fetch(`/api/v1/ai/model?session=${urlParams.get("session")}&type=${model}`, {
    method: "POST",
  }).then(response => {
    if (response.ok) 
      return response.json();
    return Promise.reject(response); 
  })
  .then(json => {
    loadingProgress.style.width = 100 + '%';
    loadingText.textContent = 'Training: 100%';
    const modelIdMap = {
      "naive-bayes-model": "nb-active",
      "random-forest-model": "rf-active",
      "linear-svm-model": "lsvm-active",
      "logistic-regression-model": "lr-active"
    };

    const elementId = modelIdMap[model];
    const element = document.getElementById(elementId);
    if (element) {
      element.innerHTML = `<span class="status-active">Active</span>`;
    }
    document.getElementById("metric-f1").innerHTML = (json.data.f1 * 100).toFixed(2) + "%";
    document.getElementById("metric-accuracy").innerHTML = (json.data.accuracy * 100).toFixed(2) + "%";
    document.getElementById("metric-precision-recall").innerHTML = `${(json.data.precision * 100).toFixed(2) + "%"} / ${(json.data.recall * 100).toFixed(2) + "%"}`;
    document.getElementById("confusion-matrix").innerHTML = `Download`
    document.getElementById("confusion-matrix").href = `/api/v1/ai/model?session=${urlParams.get("session")}&type=${model}&extension=.png`
  })
  .catch(error => {
    console.error(error);
    error.json().then(error => {
        alert(error.message)
    });
  });  
}

/*

// Add this to your admin.js file
function startTraining() {
  const loadingContainer = document.getElementById('loadingContainer');
  const loadingProgress = document.getElementById('loadingProgress');
  const loadingText = document.getElementById('loadingText');
  const trainBtn = document.getElementById('trainBtn');
  
  // Show loading bar and disable button
  loadingContainer.style.display = 'block';
  trainBtn.disabled = true;
  
  // Simulate training progress
  let progress = 0;
  const interval = setInterval(() => {
      progress += Math.random() * 10;
      if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          
          // Update UI when complete
          loadingText.textContent = 'Training complete!';
          trainBtn.disabled = false;
          
          // Optional: Hide loading bar after delay
          setTimeout(() => {
              loadingContainer.style.display = 'none';
              loadingProgress.style.width = '0%';
              loadingText.textContent = 'Training model: 0%';
          }, 2000);
      } else {
          loadingProgress.style.width = progress + '%';
          loadingText.textContent = 'Training model: ' + Math.floor(progress) + '%';
      }
  }, 300);
}


// Make sure to call this function when the Train Model button is clicked
document.getElementById('trainBtn').addEventListener('click', startTraining);

*/