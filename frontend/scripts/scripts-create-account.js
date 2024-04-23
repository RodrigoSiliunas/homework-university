const form = document.querySelector("#userForm");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const name = formData.get("idName");
  const username = formData.get("idUsername");
  const email = formData.get("idEmail");
  const password = formData.get("idPassword");
  const statusOk = document.getElementById("statusOk");
  const statusError = document.getElementById("statusError");

  // Create a JavaScript object to hold the form data
  const data = {
    name: name,
    username: username,
    email: email,
    password: password,
  };

  // Convert the JavaScript object to JSON string
  const dataJSON = JSON.stringify(data);

  try {
    const response = await fetch("http://127.0.0.1:8000/v1/users", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: dataJSON,
    });

    if (response.ok) {
      const responseData = await response.json();
      console.log("Resposta do servidor:", responseData);
      window.location.href = "http://127.0.0.1:5500/frontend/login.html";
    } else {
      console.error("Erro na requisição:", response.statusText);
      statusError.style.display = "block";
    }
  } catch (error) {
    console.error("Erro na requisição:", error);
  }
});
