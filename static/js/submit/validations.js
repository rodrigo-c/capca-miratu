import {set_image_preview} from "./images.js"


function validate_rut(input) {
  let validator = {
    val: function (rut) {
      if (!/^[0-9]+[-|‐]{1}[0-9kK]{1}$/.test(rut)) {
        return false
      }
      let tmp   = rut.split('-')
      let digv  = tmp[1]
      let _rut   = tmp[0]
      if (digv == 'K') {digv = 'k'}
      return (validator.dv(_rut) == digv );
    },
    dv: function(T){
      let M=0, S=1;
      for(;T;T=Math.floor(T/10))
        S=(S+T%10*(9-M++%6))%11;
      return S?S-1:'k';
    }
  }
  if (!input.value || (input.value && validator.val(input.value))) {
    input.setCustomValidity("")
  } else {
    let message = "Rut inválido"
    input.setCustomValidity(message)
  }
}

function _get_question_errors(question_index, containers) {
  let errors = containers.question_list[question_index].querySelector(".errors")
  errors.textContent = ""
  return errors
}


function validate_image_question(input) {
  let required = input.hasAttribute("required")
  let question_container = input.parentElement.parentElement.parentElement
  let errors = question_container.querySelector(".errors")
  let image_input_container = input.parentElement
  errors.textContent = ""
  image_input_container.classList.remove("error")

  input.setCustomValidity("")
  if (required && input.files.length == 0) {
    let message = "*Este campo es obligatorio"
    errors.textContent = message
    image_input_container.classList.add("error")
    input.value = ""
    input.setCustomValidity(message)
  }
  set_image_preview(input)
}


function validate_options_question(input, containers, report) {
  let field_container =  containers.question_list[input.question_index].querySelector("[field='options']")
  let maxlength = parseInt(field_container.getAttribute("maxlength"))
  let required = field_container.hasAttribute("required")
  let checked_inputs = Array.from(field_container.querySelectorAll("input")).filter(input=>input.checked).length
  let errors = _get_question_errors(input.question_index, containers)

  input.setCustomValidity("")
  if (checked_inputs > maxlength && input.checked) {
    let message = `Seleccione máximo ${maxlength} respuesta${maxlength > 1? 's': ''}`
    errors.textContent = message
    input.checked = false
  }
  else if (required && checked_inputs == 0 && !input.checked) {
    let message = `Debe seleccionar al menos una opción`
    if (report) {errors.textContent = message}
    input.setCustomValidity(message)
  }
  else {
    for (let i of field_container.querySelectorAll("input")) {
      i.setCustomValidity("")
    }
  }
  if (input.checked) {
    input.parentElement.classList.add("checked")
  } else {
    input.parentElement.classList.remove("checked")
  }
}

function validate_point_question (input, containers, report) {
  let field_container =  containers.question_list[input.question_index].querySelector("[field='point']")
  let required = field_container.hasAttribute("required")
  let errors = _get_question_errors(input.question_index, containers)
  let clear_features = input.parentElement.querySelector(".clear-features")

  field_container.classList.remove("error")
  input.setCustomValidity("")
  if (input.value) {
    clear_features.classList.remove("hidden")
  } else {
    clear_features.classList.add("hidden")
  }

  if (required && !input.value) {
    let message = "*Este campo es requerido"
    if (report) {
      field_container.classList.add("error")
      errors.textContent = message
    }
    input.setCustomValidity(message)
  }
}

function validate_text_question (input, containers, report) {
  let field_container =  input.parentElement
  let required = field_container.hasAttribute("required")
  let maxlength = input.getAttribute("maxlength")
  let minlength = input.getAttribute("minlength")
  maxlength = Number.isInteger(maxlength) ? maxlength : 255
  minlength = Number.isInteger(minlength) ? minlength : 1
  let errors = _get_question_errors(input.question_index, containers)

  field_container.classList.remove("error")
  input.setCustomValidity("")
  let valid = true
  let message = null
  if (required && !input.value) {
    message = "*Este campo es requerido"
    valid = false
  }
  else if (input.value && input.value.length > maxlength) {
    message = `*Este campo debe tener como máximo ${maxlength} caracteres`
    valid = false
  }
  else if (input.value && input.value.length < minlength) {
    message = `*Este campo debe tener como mínimo ${minlength} caracteres`
    valid = false
  }

  if (!valid) {
    if (report) {
      field_container.classList.add("error")
      errors.textContent = message
    }
    input.setCustomValidity(message)
  }
}


const validator = {
  validate_rut,
  validate_image_question,
  validate_options_question,
  validate_point_question,
  validate_text_question,
}

export {validator}
