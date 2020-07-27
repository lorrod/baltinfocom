
function show_modal() {
  var modal = document.getElementById("auth");
  modal.style = "display: block;"
}
function hide_modal() {
  var modal = document.getElementById("auth");
  modal.style = "display: none;"
}

// function for dynamicly appending new input with button

function add_input() {
  input_container = document.getElementById("inputs_div");

  let div_new_input = document.createElement("div");
  div_new_input.className = "div_new_input"

  let new_input = document.createElement("input")
  new_input.setAttribute("type", "text");
  new_input.className = "url_input"
  new_input.style = "margin-right: 2.5px"

  let delete_but = document.createElement("button")
  delete_but.onclick = function() { delete_input(this);};
  delete_but.innerText = "Удалить"
  delete_but.style = "margin-left: 2.5px"
  delete_but.className = "wide_but"

  input_container.appendChild(div_new_input);
  div_new_input.appendChild(new_input);
  div_new_input.appendChild(delete_but);
}

// function for deleting new input
function delete_input(button) {
   button.parentNode.parentNode.removeChild(button.parentNode);
}


// function for asking telegram code for auth with telethon
async function request_code() {
  url = 'https://' + document.domain +'/auth';
  let request_for_booking = await fetch(url,{
    method: 'POST',
    headers: {
              'Content-Type': 'application/json;charset=utf-8'
            }
  })
    .then((response) => {
      console.log(response.status);
      if (response.status == 203) {
        show_modal()
      } else if (response.status == 200) {
        var alert = document.getElementById("alert");
        alert.innerText = "Вы уже авторизованы"
        return
      } else {
        console.log(response);
        var alert = document.getElementById("alert");
        alert.innerText = "Что-то пошло не так.."
        return
      }

});
}

// function for sending password
async function send_pass() {
  var password = document.getElementById("password").value;
  var error = document.getElementById("warning")

  //checking the format of input
  if (password.length == 0) {
    var error = document.getElementById("warning")
    error.innerText = "Необходимо ввести пароль!"
    error.style = "color: red;";
    return
  } else if (password.length > 5 || !password.match(/^-{0,1}\d+$/)) {
    error.innerText = "Это не пароль:)"
    error.style = "color: red;";
    return
  }

    data = {}
    data["code"] = password;
    url = 'https://' + document.domain + '/auth';

    let request_for_booking = await fetch(url,{
      method: 'POST',
      headers: {
                'Content-Type': 'application/json;charset=utf-8'
              },
      body: JSON.stringify(data)
    })
      .then((response) => {
        if (response.status == 201) {
          error.innerText = "Успешная авторизация!";
          error.style = "color: green;";
        } else if (response.status == 203) {
          error.innerText = "Неверный пароль..";
          error.style = "color: orange;";
        } else if (response.status == 200) {
          error.innerText = "Вы были уже авторизированы!";
          error.style = "color: green;";
        } else {
          error.innerText = "Что-то пошло не так..!";
          error.style = "color: red;";
        }

  });
}

//sending data from inputs
async function send_data() {
    var alert = document.getElementById("alert");
    alert.innerText = "Подождите, запрос обрабатывается..."

    var urls = document.getElementsByClassName('url_input');
    if (urls[0].value.length == 0 || urls[1].value.length == 0) {

      alert.innerText = "Первые два инпута должны быть заполнены"
      return
    }

    // forming dictionary with urls
    var data = {}
    for (var i = 0; i < urls.length; i++) {
      if (urls[i].value.length != 0) {
        data[i] = urls[i].value;
      }
    }

    url = 'https://' + document.domain +'/analyze';
    let request_for_booking = await fetch(url,{
      method: 'POST',
      headers: {
                'Content-Type': 'application/json;charset=utf-8'
              },
      redirect: 'follow',
      body: JSON.stringify(data)
    })
      .then((response) => {
        if (response.redirected) {
            window.location.href = response.url
        }
});
}
