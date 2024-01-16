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
      auth_url = "",
      csrf_token = "",
    }
  ) {
    this.auth_url = auth_url
    this.csrf_token = csrf_token
    this.closed_sk = new URLSearchParams(window.location.search).get("k")
    this.closed_email = new URLSearchParams(window.location.search).get("e")
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
      if (this.closed_email && input.getAttribute("name") == "email") {
        input.value = this.closed_email
        input.setAttribute("disabled", true)
      }
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
        if (input.parentElement.getAttribute("field") == "text") {
          validator.validate_text_question(input, this.comp.containers, false)
        }
      }
    }
  }

  click_start_button (event) {
    this.show_view("identifier")
  }

  set_loading () {
    this.hide_all()
    this.comp.navbars.main.classList.remove("hidden")
    document.querySelector(".load.content-container").classList.remove("hidden")
  }

  identify() {
    let identifier_data = {}
    for (let input of this.comp.input_map.identifier) {
      let field = input.getAttribute("name")
      if (field == "rut") {
        identifier_data.rut = input.value
      } else if (field == "email") {
        identifier_data.email = input.value
      }
    }
    if (this.closed_sk) {
      identifier_data.sk = this.closed_sk
    }
    fetch(this.auth_url, {
      method: "POST",
      body: JSON.stringify(identifier_data),
      headers: {"Content-Type": "application/json",  "X-CSRFToken": this.csrf_token},
    })
    .then((response) => {
      if (response.status == 200) {
        this.show_view("detail")
      } else {
        response.json().then((data)=> {
          let errors = this.comp.containers.identifier.querySelector(".errors")
          if (data.email) {errors.textContent = data.email}
          if (data.rut) {errors.textContent = data.rut}
          this.show_view("identifier")
        })
      }
    })
  }

  click_next_button (event) {
    let total_questions = this.comp.containers.question_list.length
    let valid = event.currentTarget.getAttribute("disabled") != "true"
    if (valid) {
      if (this.focus != total_questions - 1) {
        event.preventDefault()
      } else {
        for (let input of this.comp.input_map.identifier) {
          if (this.closed_email && input.getAttribute("name") == "email") {
            input.removeAttribute("disabled")
          }
        }
        this.set_loading()
      }
      if (this.focus == "identifier") {
        this.set_loading()
        this.identify()
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
    } else {
      errors.textContent = "*Error de autenticación"
    }
    this.set_next_button_status("identifier", true)
  }

  change_question_input (event) {
    let input = event.currentTarget
    this.validate_input(input, true)
    this.set_next_button_status(input.question_index, true)
  }

  validate_input (input, report) {
    if (input.type == "file") {
      validator.validate_image_question(input, report)
    }
    if (input.type == "checkbox") {
      validator.validate_options_question(input, this.comp.containers, report)
    }
    if (input.classList.contains("vSerializedField")) {
      validator.validate_point_question(input, this.comp.containers, report)
    }
    if (input.parentElement.getAttribute("field") == "text") {
      validator.validate_text_question(input, this.comp.containers, report)
    }
  }

  click_image_clear(event) {
    let input_container = event.currentTarget.parentElement
    let input = input_container.querySelector("input")
    input.value = ""
    validator.validate_image_question(input, true)
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
    document.querySelector(".load.content-container").classList.add(this.hidden_class_name)
  }

  show_view(focus) {
    this.hide_all()
    this.focus = focus
    if (focus != "entry") {
      this.comp.buttons.back.classList.remove(this.hidden_class_name)
      this.comp.buttons.submit.classList.remove(this.hidden_class_name)
      this.comp.navbars.main.classList.remove(this.hidden_class_name)
    } else {
      this.comp.navbars.brand.classList.remove(this.hidden_class_name)
    }
    if (Number.isInteger(focus)) {
      for (let input of this.comp.input_map.question_list[focus]) {
        this.validate_input(input, false)
      }
      this.set_next_button_status(focus)
      this.comp.containers.question_list[focus].classList.remove(this.hidden_class_name)
    } else {
      this.comp.containers[focus].classList.remove(this.hidden_class_name)
      this.comp.buttons.submit.removeAttribute("disabled")
    }
    if (focus == "identifier") {
      this.set_next_button_status(focus)
    }
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

  set_next_button_status(focus, report) {
    let next_button = this.comp.buttons.submit
    let valid = true
    let input_list = !isNaN(this.focus)? this.comp.input_map.question_list[focus]: this.comp.input_map.identifier
    for (let input of input_list) {
      valid &&= input.validity.valid
    }
    if (valid) {
      next_button.removeAttribute("disabled")
    } else {
      next_button.setAttribute("disabled", true)
    }
  }
}

export {QuerySubmitEngine}
