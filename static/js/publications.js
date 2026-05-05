const urlParams = new URLSearchParams(window.location.search);
const table = $('#documents-table').DataTable({
    bAutoWidth: false,
    bLengthChange: false,
    order: [[0, 'desc']],
    sScrollX: '100%',
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
    scrollX: true,
  });

function init() {
    getPublications();
    $('#documents-table tbody').on('click', 'tr', function () {
      if ($(this).hasClass('selected')) {
        $(this).removeClass('selected');
      } else {
        $('#documents-table tbody tr').removeClass('selected');
        $(this).addClass('selected');
      }
    });
    
}


function redirectToNew(empty) {
  let selectedData = table.row('.selected').data();
  location.assign(`/new-publication?session=${urlParams.get("session")}&id=${empty ?  null : selectedData.id}`);
}

function redirectBack() {
    location.assign(`/publications?session=${urlParams.get("session")}`);
}

function redirectToTrain() {
    location.assign(`/admin?session=${urlParams.get("session")}`);
}



function addFormEventListener(id) {
    let form = document.getElementById("publication-form")
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      fetch(`/api/v1/research/publication?session=${urlParams.get("session")}&id=${id}`, {
        method: id == "null" ? "POST" : "PUT",
        body: new FormData(form)
      }).then(response => {
        if (response.ok) 
          return response.json();
        return Promise.reject(response); 
      })
      .then(json => {
        alert("Publication submission completed.")
        redirectBack();
      })
      .catch(error => {
        console.error(error);
        error.json().then(error => {
            alert(error.message)
        });
      });  
    });
  }

function fillFields() {
    addFormEventListener(urlParams.get("id"));
    if (urlParams.get("id") == "null")
        return;
    fetch(`api/v1/research/publication?session=${urlParams.get("session")}&id=${urlParams.get("id")}`, {
        method: 'GET',
    }).then(response => {
        if (response.ok) 
            return response.json();
        return Promise.reject(response); 
    })
    .then(json => {
        document.getElementById("title").value = json.data.title;
        document.getElementById("abstract").value = json.data.abstract;
        document.getElementById("url").value = json.data.url;
        document.getElementById("authors").value = json.data.authors;
        const dateObj = new Date(json.data.submission_date)
        const formatted = dateObj.toISOString().slice(0, 16) // "2025-03-06T00:00"
        document.getElementById("submission-date").value = formatted
        document.getElementById("category").value = json.data.category;
        document.getElementById("metadata").value = json.data.metadata;
    })
    .catch(error => {
        console.error(error);
        error.json().then(error => {
            alert(error.message)
        });
    });  
}

function getPublications(){
    fetch(`api/v1/research/publication/all?session=${urlParams.get("session")}`, {
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
        error.json().then(error => {
            if (isAuthTokenInvalid(error)) 
              location.assign("/login");
            else 
                alert(error.message)
        });
    });  
}

function deletePublication() {
  let row = table.row('.selected');
  let selectedData = row.data();

  fetch(`/api/v1/research/publication?session=${urlParams.get("session")}&id=${selectedData.id}`, {
    method: 'DELETE',
  }).then(response => {
    if (response.ok) 
      return response.json();
    return Promise.reject(response); 
  })
  .then(json => {
    row.remove().draw();
  })
  .catch(error => {
    console.error(error);
    error.json().then(error => alert(error.message));
  });  
}


function createPublication(){
    fetch(`api/v1/research/publication?session=${urlParams.get("session")}`, {
        method: 'GET',
    }).then(response => {
        if (response.ok) 
            return response.json();
        return Promise.reject(response); 
    })
    .then(json => {
        json.data.publications.forEach(function (data, index, arr) {
            document.getElementById("documents-table").innerHTML += `
                <div class="table-row">
                    <div class="row-item document-title">${data.title}</div>
                   <div class="row-item date-submitted">${data.submission_date}</div>
                    <div class="row-item actions">
                        <a href="${data.url}" class="action-link view">View</a>
                        <a href="#" class="action-link delete">Delete</a>
                    </div>
                </div>
            `;
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