const urlParams = new URLSearchParams(window.location.search);

function addRegisterFormEventListener() {
  document.getElementById("username").value = urlParams.get("username")
  document.getElementById("email").value = urlParams.get("email")
  document.getElementById('form').addEventListener('submit', function(event) {
    event.preventDefault();
    fetch(`api/v1/security/register?invite=${urlParams.get("invite")}`, {
      method: "POST",
      body: new FormData(this)
    }).then(response => {
      if (response.ok)
        return response.json();
      return Promise.reject(response);
    })
    .then(json => {
      location.assign(`/`);
    })
    .catch(error => {
      error.json().then(error => {
        document.getElementById("response-msg").innerHTML = error.message;
      });
    });
  });
}

function addLoginFormEventListener() {
  document.getElementById('form').addEventListener('submit', function(event){
    event.preventDefault();
    fetch('api/v1/security/login', {
      method: 'POST',
      headers: new Headers({
        'Authorization': 'Basic '+ btoa(this.email.value + ':' + this.password.value),
        'Content-Type': 'application/x-www-form-urlencoded'
      })
    })
    .then(response => {
      if (response.ok)
        return response.json();
      return Promise.reject(response);
    })
    .then(json => {
      if (urlParams.get("invite") == null)
        location.assign(`/`);
      else
        location.assign(`api/v1/research/session/invite?id=${urlParams.get("invite")}`);
    })
    .catch(error => {
      error.json().then(error => {
        document.getElementById("response-msg").innerHTML = error.message;
      });
    });
  });
}