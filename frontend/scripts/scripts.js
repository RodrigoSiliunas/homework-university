const buttonCreate = document.querySelector('#buttonCreate');
const buttonLogin = document.querySelector('#buttonLogin');


buttonCreate.addEventListener('click', () => {
  window.location.href = "http://127.0.0.1:5500/frontend/create-account.html";
});

buttonLogin.addEventListener('click', () => {
  window.location.href = "http://127.0.0.1:5500/frontend/login.html";
});
