const focus_names = {
  entry: "entry",
  identifier: "identifier",
  detail: "detail",
  question: "question"
}

const suffixes = {
  cont: "-container"
}

const button_names = {
  start: "start-button",
  back: "back-button",
  submit: "form-submit",
}

function _get_question_input_list(containers) {
  let question_list = []
  for (let i = 0; i < containers.question_list.length; i++) {
    let question = containers.question_list[i]
    let question_inputs = question.querySelectorAll("input,textarea")
    for (let input of question_inputs) {
      input.question_index = i
    }
    question_list.push(Array.from(question_inputs))
  }
  return question_list
}

function get_components() {
  let containers = {
    entry: document.getElementById(focus_names.entry + suffixes.cont),
    identifier: document.getElementById(focus_names.identifier + suffixes.cont),
    detail: document.getElementById(focus_names.detail + suffixes.cont),
    question_list: Array.from(document.getElementsByClassName(focus_names.question)),
  }
  return {
    navbars: {
      main: document.getElementById("navbar"),
    },
    has_nodescription: document.querySelector("#detail-container").hasAttribute("nodescription"),
    containers: containers,
    buttons: {
      start: document.getElementById(button_names.start),
      back: document.getElementById(button_names.back),
      submit: document.getElementById(button_names.submit),
    },
    input_map: {
      identifier: Array.from(containers.identifier.querySelectorAll("input,textarea")),
      question_list: _get_question_input_list(containers),
    },
  }
}


export {get_components}
