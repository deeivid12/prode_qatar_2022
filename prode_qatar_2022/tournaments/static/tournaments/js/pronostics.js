function check_tie(element){
  let parent = element.closest('.card-body');
  let home_goals = parent.querySelector('[name="home_goals"]').value
  let away_goals = parent.querySelector('[name="away_goals"]').value
  let radio_buttons = parent.querySelectorAll('input[type="radio"]');
  if (radio_buttons.length === 0) {
      return;
  }
  if (home_goals != away_goals){
    radio_buttons.forEach(function(radio) {
      radio.disabled = true;
      radio.checked = false;
    });
  }
  else {
    radio_buttons.forEach(function(radio) {
      radio.removeAttribute("disabled");
    });
  }
}

function check_elements(){
  let elements = document.querySelectorAll("form .card");
  elements.forEach(function(card_element){
    let card_body = card_element.querySelector(".card-body");
    let played = card_body.querySelector('[name="played"]').getAttribute("played");
    let home_goals = card_body.querySelector('[name="home_goals"]');
    let away_goals = card_body.querySelector('[name="away_goals"]');
    let radio_buttons = card_body.querySelectorAll('input[type="radio"]');

    if (played == "True"){
      card_body.classList.add("bg-secondary");
      home_goals.disabled = true;
      away_goals.disabled = true;
      home_goals.setAttribute("style", "background-color: #b5babe;");
      away_goals.setAttribute("style", "background-color: #b5babe;");
      home_goals.setAttribute("class", "form-control text-center");
      away_goals.setAttribute("class", "form-control text-center");
      if (radio_buttons.length != 0) {
        radio_buttons.forEach(function(radio) {
          radio.disabled = true;
        });
      }
    } else {
        home_goals.addEventListener('input', () => check_tie(home_goals));
        away_goals.addEventListener('input', () => check_tie(away_goals));
        check_tie(home_goals);
    }
  })
}

window.onload = check_elements; 