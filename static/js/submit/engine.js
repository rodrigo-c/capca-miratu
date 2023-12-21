import {
  get_components
} from "./components.js"

import {
  set_point_input_event, set_response_geolocation
} from "./geo.js"

import {
  validator
} from "./validations.js"


class QuerySubmitEngine {
  constructor (
    {
      focus = "entry",
    }
  ) {
    this.hidden_class_name = "hidden";
    this.comp = get_components()
    this._set_focus (focus)
    this._set_event_buttons()
    this._set_identifier_inputs()
    this._set_question_inputs()
    set_response_geolocation(this, this.comp.containers, this.comp.input_map)
  }
  _set_focus (focus) {
    this.focus = !isNaN(focus) ? parseInt(focus): focus
    this.show_view(this.focus)
  }

  _set_event_buttons() {
    this.click_start_button = this.click_start_button.bind(this)
    this.comp.buttons.start.addEventListener("click", this.click_start_button, false)

    this.click_next_button = this.click_next_button.bind(this)
    this.comp.buttons.submit.addEventListener("click", this.click_next_button, false)

    this.show_back_form = this.show_back_form.bind(this)
    this.comp.buttons.back.addEventListener("click", this.show_back_form, false)
  }

  _set_identifier_inputs () {
    this.change_identifier_input = this.change_identifier_input.bind(this)
    for (let input of this.comp.input_map.identifier) {
      input.addEventListener("input", this.change_identifier_input, false)
    }
  }

  _set_question_inputs() {
    this.change_question_input = this.change_question_input.bind(this)
    this.click_image_clear = this.click_image_clear.bind(this)
    for (let inputs of this.comp.input_map.question_list) {
      for (let input of inputs) {
        input.addEventListener("input", this.change_question_input, false)
        if (input.type == "checkbox") {
          validator.validate_options_question(input, this.comp.containers, false)
        }
        if (input.classList.contains("vSerializedField")) {
          set_point_input_event(input)
          validator.validate_point_question(input, this.comp.containers, false)
        }
        if (input.type == "file") {
          let input_container = input.parentElement
          let input_close_icon = input_container.querySelector(".closed-icon")
          input_close_icon.addEventListener("click", this.click_image_clear, false)
        }
      }
    }
  }

  click_start_button (event) {
    this.show_view("identifier")
  }

  click_next_button (event) {
    let total_questions = this.comp.containers.question_list.length
    let valid = event.currentTarget.getAttribute("disabled") != "true"
    if (valid) {
      if (this.focus != total_questions - 1) {
        event.preventDefault()
      } else {
        this.hide_all()
        document.querySelector(".load.content-container").classList.remove("hidden")
      }
      if (this.focus == "identifier") {
        this.show_view("detail")
      } else if (this.focus == "detail") {
        this.show_view(0)
      }
      else if (Number.isInteger(this.focus)) {
        if (this.focus < total_questions - 1) {
          this.show_view(this.focus + 1)
        }
      }
    }
  }

  change_identifier_input (event) {
    let input = event.currentTarget
    let button = this.comp.buttons.submit
    let errors = input.parentElement.parentElement.querySelector(".errors")
    let valid = true
    for (let input of this.comp.input_map.identifier) {
      if (input.getAttribute("name") == "rut") {
        validator.validate_rut(input)
      }
      valid &&= input.validity.valid
    }
    if (valid) {
      errors.textContent = ""
      button.removeAttribute("disabled")
    } else {
      errors.textContent = "*Error de autenticación"
      button.setAttribute("disabled", true)
    }
  }

  change_question_input (event) {
    let input = event.currentTarget
    if (input.type == "file") {
      validator.validate_image_question(input)
    }
    if (input.type == "checkbox") {
      validator.validate_options_question(input, this.comp.containers, true)
    }
    if (input.classList.contains("vSerializedField")) {
      validator.validate_point_question(input, this.comp.containers, true)
    }
    this.set_next_button_status(input.question_index, true)
  }

  click_image_clear(event) {
    let input_container = event.currentTarget.parentElement
    let input = input_container.querySelector("input")
    input.value = ""
    validator.validate_image_question(input)
    this.set_next_button_status(input.question_index, true)
  }

  hide_all () {
    this.comp.navbars.main.classList.add(this.hidden_class_name)
    this.comp.navbars.brand.classList.add(this.hidden_class_name)
    this.comp.containers.entry.classList.add(this.hidden_class_name)
    this.comp.containers.identifier.classList.add(this.hidden_class_name)
    this.comp.containers.detail.classList.add(this.hidden_class_name)
    for (let question of this.comp.containers.question_list) {
        question.classList.add(this.hidden_class_name)
    }
    this.comp.buttons.submit.classList.add(this.hidden_class_name)
    this.comp.buttons.back.classList.add(this.hidden_class_name)

  }

  show_view(focus) {
    this.hide_all()
    if (focus != "entry") {
      this.comp.buttons.back.classList.remove(this.hidden_class_name)
      this.comp.buttons.submit.classList.remove(this.hidden_class_name)
      this.comp.navbars.main.classList.remove(this.hidden_class_name)
    } else {
      this.comp.navbars.brand.classList.remove(this.hidden_class_name)
    }
    if (Number.isInteger(focus)) {
      this.set_next_button_status(focus)
      this.comp.containers.question_list[focus].classList.remove(this.hidden_class_name)
    } else {
      this.comp.containers[focus].classList.remove(this.hidden_class_name)
      this.comp.buttons.submit.removeAttribute("disabled")
    }
    this.focus = focus
  }

  show_back_form () {
    if (this.focus == "identifier") {
        this.show_view("entry")
    }
    else if (this.focus == "detail") {
      this.show_view("identifier")
    }
    else if (!isNaN(this.focus)) {
        if (this.focus == 0) {this.show_view("detail")}
        else {this.show_view(this.focus - 1)}
    }
  }

  set_next_button_status(question_index, report) {
    let next_button = this.comp.buttons.submit
    let valid = true
    for (let input of this.comp.input_map.question_list[question_index]) {
      valid &&= input.validity.valid
      if (!valid && report) {input.reportValidity()}
    }
    if (valid) {
      next_button.removeAttribute("disabled")
    } else {
      next_button.setAttribute("disabled", true)
    }
  }
}

export {QuerySubmitEngine}
