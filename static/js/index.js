const table = $('#documents-table').DataTable({
  order: [[0, 'desc']],
  bAutoWidth: false,
  scrollX: true,
  columns: [
    {data: 'date_created'},
    {data: 'submission_date'},
    {data: 'title'},
    {data: 'authors'},
    {data: 'category'},
  ],
  columnDefs: [
    {
      targets: [0],
      render: function (data, type, row, meta) {
        return parseDateTime(data)
      }
    },
    {
      targets: [1],
      render: function (data, type, row, meta) {
        return parseDate(data)
      }
    }
  ],

});
const memosTable = $('#memos-table').DataTable({
  bAutoWidth: false,
  order: [[0, 'desc']],
  columns: [
    {data: 'date_created'},
    {data: 'title'},
    {data: 'account'},
    {data: 'publication'},
  ],
  columnDefs: [
    {
      targets: [0],
      render: function (data, type, row, meta) {
        return parseDateTime(data)
      }
    },
  ],
  scrollX: true,
});


function init() {
  fillResearchSessions();
  $('#documents-table tbody').on('click', 'tr', function () {
    if ($(this).hasClass('selected')) {
      $(this).removeClass('selected');
    } else {
      $('#documents-table tbody tr').removeClass('selected');
      $(this).addClass('selected');
    }
  });
  $('#memos-table tbody').on('click', 'tr', function () {
    if ($(this).hasClass('selected')) {
      $(this).removeClass('selected');
    } else {
      $('memos-table tbody tr').removeClass('selected');
      $(this).addClass('selected');
    }
  });
  setupRowHighlighting(document.getElementById("research-sessions-body"));
  addFormEventListener();
}

function fillResearchSessions() {
    document.getElementById("research-sessions-body").innerHTML = '';
    fetch(`/api/v1/research/session`, {
        method: 'GET',
      }).then(response => {
        if (response.ok) 
          return response.json();
        return Promise.reject(response); 
      })
      .then(json => {
        json.data.forEach(function (data, index, arr) {
            document.getElementById("research-sessions-body").innerHTML += `
            <tr value="${data.id}" class="session-row">
                <td>${data.title}</td>
                <td>${data.date_created.split(" ")[0]}</td>
            </tr>
            `
        });
      })
      .catch(error => {
        console.error(error);
        error.json().then(error => {
            if (isAuthTokenInvalid(error)) 
              location.assign("/login");
            else 
                alert(error.message)
        });
      });  
}

function redirectToPublications() {
  let selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
  if (selectedRow == null) {
      alert("No research session selected.")
      return
  }
  location.assign(`/publications?session=${selectedRow}`);
}

function viewPublication() {
  let selectedData = table.row('.selected').data();
  if (selectedData == null)
    return 
  window.open(selectedData.url, '_blank');
}

function toggleView(viewType) {
  const abstractBox = document.getElementById('abstract-box');
  const summaryBox = document.getElementById('summary-box');
  abstractBox.classList.remove('hidden', 'full-width');
  summaryBox.classList.remove('hidden', 'full-width');
  switch(viewType) {
    case 'abstract':
      summaryBox.classList.add('hidden');
      abstractBox.classList.add('full-width');
      break;
    case 'summary':
      abstractBox.classList.add('hidden');
      summaryBox.classList.add('full-width');
      break;
    case 'both':
      break;
  }
}

function searchPublications() {
  table.clear();
  document.getElementById("publications").style.display = 'block'
  document.getElementById("summary").style.display = 'none'
  document.getElementById("memos").style.display = 'none'
  let selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
  if (selectedRow == null)
      return
  fetch(`/api/v1/research/publication/search?session=${selectedRow}&query=${document.getElementById("search-box").value}`, {
      method: 'GET',
    }).then(response => {
      if (response.ok) 
        return response.json();
      return Promise.reject(response); 
    })
    .then(json => {
      table.rows.add(json.data).draw();
    })
    .catch(error => {
      console.error(error);
      error.json().then(error => alert(error.message));
    });  
}

function deleteResearchSession() {
  let selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
  if (selectedRow == null)
      return
  fetch(`/api/v1/research/session?id=${selectedRow}`, {
      method: 'DELETE',
    }).then(response => {
      if (response.ok) 
        return response.json();
      return Promise.reject(response); 
    })
    .then(json => {
      fillResearchSessions();
    })
    .catch(error => {
      console.error(error);
      error.json().then(error => alert(error.message));
    });  
}


function createNewResearchSession() {
  const userInput = prompt("Enter title:");
  if (userInput !== null) {
    let form = new FormData();
    form.append("title" ,userInput)
    fetch(`/api/v1/research/session`, {
      method: 'POST',
      body: form,
    }).then(response => {
      if (response.ok) 
        return response.json();
      return Promise.reject(response); 
    })
    .then(json => {
      fillResearchSessions();
    })
    .catch(error => {
      console.error(error);
      error.json().then(error => alert(error.message));
    });  
  }
}

function setupRowHighlighting(tableBody) {
  if (!tableBody) return;
  tableBody.addEventListener('click', function(e) {
      const clickedRow = e.target.closest('tr');
      if (clickedRow && tableBody.contains(clickedRow)) {
          [...tableBody.querySelectorAll('tr')].forEach(row => {
              row.classList.remove('active');
          });
          clickedRow.classList.add('active');
      }
  });
}

function getSelectedValue(tableBody) {
  if (!tableBody) return null;
  const activeRow = tableBody.querySelector('tr.active');
  if (activeRow) {
      return activeRow.getAttribute('value');
  } else {
      alert("No research session selected.");
      return null;
  }
}

function share() {
  let selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
  if (selectedRow == null)
    return;
  navigator.clipboard.writeText(`http://127.0.0.1:8000/api/v1/research/session/invite?id=${selectedRow}`)
  .then(() => {
    alert(`Copied to your clipboard, only give to someone you trust.`)
  })
  .catch(err => {
    console.error("Failed to copy text: ", err);
  });

}

function summarizePublication() {
  let selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
  let selectedData = table.row('.selected').data();
  if (selectedData == null)
      return
  let button = document.getElementById("summarize-button");
  let summary = document.getElementById("full-summary-content");
  button.classList.add("disabled")
  summary.innerHTML = "";
  button.innerHTML = "Processing..."
  document.getElementById("abstract-content").innerHTML = selectedData.abstract;
  document.getElementById("publications").style.display = 'none'
  document.getElementById("summary").style.display = 'block'
  
  fetch(`/api/v1/ai/summarize?session=${selectedRow}&publication=${selectedData.id}`, {
      method: 'GET',
    }).then(response => {
      if (response.ok) 
        return response.body;
      return Promise.reject(response); 
    })
    .then(body => {
      const reader = body.getReader();
      const decoder = new TextDecoder();
      let markdownContent = ''; // Variable to accumulate markdown content
      reader.read().then(function pump({ done, value }) {
        if (done) {
          button.classList.remove("disabled")
          button.innerHTML = "Summarize"
          return;
        }
        markdownContent += decoder.decode(value, { stream: true });
        summary.innerHTML = marked.parse(markdownContent);
        return reader.read().then(pump);
      });     
    })
    .catch(error => {
      console.error(error);
      error.json().then(error => alert(error.message));
      button.classList.remove("disabled")
      button.innerHTML = "Summarize"
    });  
}

function citate() {
  let selectedData = table.row('.selected').data();
  if (selectedData == null)
    return 
  window.open(`https://www.citethisforme.com/cite/website/autocite?q=${selectedData.url}`, '_blank');
}

function back() {
  document.getElementById("publications").style.display = 'block'
  document.getElementById("summary").style.display = 'none'
  document.getElementById("memos").style.display = 'none'
  document.getElementById("memo-form-container").style.display = 'none'
}

function viewMemo() {
  let selectedData = memosTable.row('.selected').data();
  if (selectedData == null) 
    return;
  document.getElementById("memo-form-container").style.display = 'block'
  document.getElementById("publications").style.display = 'none'
  document.getElementById("memos").style.display = 'none'
  document.getElementById("memo-title").value = selectedData.title;
  document.getElementById("memo-content").value = selectedData.content;
}

function viewMemos() {
  memosTable.clear().draw();
  let selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
  if (selectedRow == null)
      return
  document.getElementById("summary").style.display = 'none'
  document.getElementById("publications").style.display = 'none'
  let selectedData = table.row('.selected').data();
  if (selectedData == null) {
    document.getElementById("memos").style.display = 'block'
    fetch(`/api/v1/research/memo?session=${selectedRow}`, {
      method: 'GET',
    }).then(response => {
      if (response.ok) 
        return response.json();
      return Promise.reject(response); 
    })
    .then(json => {
      memosTable.rows.add(json.data).draw();
    })
    .catch(error => {
      console.error(error);
      error.json().then(error => {
        alert(error.message)      
      });
    });  
  }
  else {
    document.getElementById("memo-form-container").style.display = 'block'
    document.getElementById("publications").style.display = 'none'
    document.getElementById("memo-title").value = '';
    document.getElementById("memo-content").value = '';
  }
}

function deleteMemo() {
  const selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
  if (selectedRow == null) return;

  const row = memosTable.row('.selected');
  const selectedData = row.data();
  if (!selectedData) return;

  fetch(`/api/v1/research/memo?session=${selectedRow}&id=${selectedData.id}`, {
    method: 'DELETE',
  })
  .then(response => {
    if (response.ok) return response.json();
    return Promise.reject(response);
  })
  .then(json => {
    row.remove().draw(false);
  })
  .catch(error => {
    console.error(error);
    error.json?.().then(err => alert(err.message));
  });
}


function addFormEventListener() {
  let form = document.getElementById("memo-form");
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    let selectedRow = getSelectedValue(document.getElementById("research-sessions-body"));
    if (selectedRow == null)
      return;
    
    let selectedData = memosTable.row('.selected').data();
    let selectedPublication = table.row('.selected').data();

    fetch(`/api/v1/research/memo?session=${selectedRow}&${selectedPublication == null ? `id=${selectedData.id}` : `publication=${selectedPublication.id}`}`, {
      method: selectedData == null ? "POST" : "PUT",
      body: new FormData(form)
    })
    .then(response => {
      if (response.ok)
        return response.json();
      return Promise.reject(response);
    })
    .then(json => {
      const selectedRowNode = memosTable.row('.selected');
      document.getElementById("memo-form-container").style.display = 'none'
      if (selectedRowNode.node()) {
        selectedRowNode.data(json.data).draw(false); // update row
        document.getElementById("memos").style.display = 'block';
      } else {
        memosTable.rows.add([json.data]).draw(); // fallback to adding new row
        document.getElementById("publications").style.display = 'block'       
      }
    })
    .catch(error => {
      console.error(error);
    });
  });
}