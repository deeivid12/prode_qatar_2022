function parseGoalValue(val) {
  if (val === null || val === undefined || val === "") {
    return null;
  }
  const n = parseInt(val, 10);
  return Number.isNaN(n) ? null : n;
}

function getGoalInputs(cardBody) {
  let inputs = cardBody.querySelectorAll("input[type='number']");
  let home = null;
  let away = null;
  inputs.forEach(function (input) {
    if (input.name.startsWith("home_goals_")) {
      home = input;
    } else if (input.name.startsWith("away_goals_")) {
      away = input;
    }
  });
  return { home: home, away: away };
}

function check_tie(element) {
  let parent = element.closest(".card-body");
  let goals = getGoalInputs(parent);
  if (!goals.home || !goals.away) {
    return;
  }
  let radio_buttons = parent.querySelectorAll("input[type='radio']");
  if (radio_buttons.length === 0) {
    return;
  }
  let h = parseGoalValue(goals.home.value);
  let a = parseGoalValue(goals.away.value);
  if (h === null || a === null) {
    radio_buttons.forEach(function (radio) {
      radio.disabled = true;
      radio.checked = false;
    });
    return;
  }
  if (h !== a) {
    radio_buttons.forEach(function (radio) {
      radio.disabled = true;
      radio.checked = false;
    });
  } else {
    radio_buttons.forEach(function (radio) {
      radio.removeAttribute("disabled");
    });
  }
}

function validatePronosticForm(e, form) {
  if (!form || form.tagName !== "FORM") {
    return;
  }
  let ok = true;
  let cards = form.querySelectorAll(".card");
  cards.forEach(function (card) {
    let played = card.getAttribute("data-played");
    if (played === "True") {
      return;
    }
    let card_body = card.querySelector(".card-body");
    if (!card_body) {
      return;
    }
    let goals = getGoalInputs(card_body);
    if (!goals.home || !goals.away) {
      return;
    }
    let hr = goals.home.value.trim();
    let ar = goals.away.value.trim();
    if ((hr !== "" && ar === "") || (hr === "" && ar !== "")) {
      ok = false;
      goals.home.classList.add("is-invalid");
      goals.away.classList.add("is-invalid");
    } else {
      goals.home.classList.remove("is-invalid");
      goals.away.classList.remove("is-invalid");
    }
    let radio_buttons = card_body.querySelectorAll("input[type='radio']");
    if (radio_buttons.length !== 0) {
      let h = parseGoalValue(hr);
      let a = parseGoalValue(ar);
      if (h !== null && a !== null && h === a) {
        let any_checked = false;
        radio_buttons.forEach(function (radio) {
          if (radio.checked) {
            any_checked = true;
          }
        });
        if (!any_checked) {
          ok = false;
          radio_buttons.forEach(function (radio) {
            radio.classList.add("is-invalid");
          });
        } else {
          radio_buttons.forEach(function (radio) {
            radio.classList.remove("is-invalid");
          });
        }
      } else {
        radio_buttons.forEach(function (radio) {
          radio.classList.remove("is-invalid");
        });
      }
    }
  });
  if (!ok) {
    e.preventDefault();
    alert(
      "Revisá los pronósticos: completá ambos goles o dejá ambos vacíos; en llaves, si hay empate elegí ganador por penales."
    );
  }
}

function check_elements() {
  let form = document.querySelector("form[method='post']");
  if (form) {
    form.addEventListener("submit", function (e) {
      validatePronosticForm(e, form);
    });
  }
  let elements = document.querySelectorAll("form .card");
  elements.forEach(function (card_element) {
    let played = card_element.getAttribute("data-played");
    let card_body = card_element.querySelector(".card-body");
    let goals = getGoalInputs(card_body);
    if (!goals.home || !goals.away) {
      return;
    }
    let radio_buttons = card_body.querySelectorAll("input[type='radio']");

    if (played == "True") {
      card_body.classList.add("bg-secondary");
      goals.home.disabled = true;
      goals.away.disabled = true;
      goals.home.setAttribute("style", "background-color: #b5babe;");
      goals.away.setAttribute("style", "background-color: #b5babe;");
      goals.home.setAttribute("class", "form-control text-center");
      goals.away.setAttribute("class", "form-control text-center");
      if (radio_buttons.length != 0) {
        radio_buttons.forEach(function (radio) {
          radio.disabled = true;
        });
      }
    } else {
      goals.home.addEventListener("input", () => check_tie(goals.home));
      goals.away.addEventListener("input", () => check_tie(goals.away));
      check_tie(goals.home);
    }
  });
}

window.onload = check_elements;
