/* Public query submit view */

class QuerySubmitManager {
  constructor (
    {
      focus = "detail",
      detail_id = "detail-container",
      response_id = "response-container",
      back_button_id = "back-button",
      start_button_id = "start-button",
      question_class_name = "question",
      hidden_class_name = "hidden",
      image_input_class_name = "image-input",
      start_questions_button_id = "next-response-button",
      next_question_button_prefix = "next-question-button",
      submit_id = "form-submit",
    } = {}
  ) {
    this.kwargs = {
      detail_id,
      response_id,
      back_button_id,
      start_button_id,
      question_class_name,
      hidden_class_name,
      image_input_class_name,
      start_questions_button_id,
      next_question_button_prefix,
      submit_id,
    }
    this.hidden_class_name = hidden_class_name;
    this._set_focus(focus)
    this._set_containers()
    this._set_buttons()
    this._set_inputs()
  }

  _set_focus (focus) {this.focus = !isNaN(focus) ? parseInt(focus): focus}

  _set_containers() {
    let detail = document.getElementById(this.kwargs.detail_id);
    let response = document.getElementById(this.kwargs.response_id);
    let question_list = document.getElementsByClassName(this.kwargs.question_class_name);
    this.containers = {detail, response: response, question_list: question_list}
  }

  _set_buttons() {
    let start = document.getElementById(this.kwargs.start_button_id)
    this.click_start_button = this.click_start_button.bind(this)
    start.addEventListener("click", this.click_start_button, false)

    let back = document.getElementById(this.kwargs.back_button_id)
    this.show_back_form = this.show_back_form.bind(this)
    back.addEventListener("click", this.show_back_form, false)

    let start_questions =  document.getElementById(this.kwargs.start_questions_button_id)
    this.click_next_question = this.click_next_question.bind(this)
    start_questions.addEventListener("click", this.click_next_question, false)
    start_questions.next_question = 0

    let next_question_list = {}
    for (let i = this.containers.question_list.length - 1; i >= 0; i--) {
      let prefix = this.kwargs.next_question_button_prefix
      let next_question_button = document.getElementById(`${prefix}-${i}`)
      if (next_question_button) {
        next_question_button.next_question = i + 1
        next_question_button.addEventListener("click", this.click_next_question, false)
        next_question_list[i] = next_question_button
      }
    }
    let submit = document.getElementById(this.kwargs.submit_id)
    this.buttons = {start, back, start_questions, next_question_list, submit}
  }

  _set_inputs() {
    this.change_image_input = this.change_image_input.bind(this)
    this.change_question_input = this.change_question_input.bind(this)

    this.input_map = {}
    for (let i = this.containers.question_list.length - 1; i >= 0; i--) {
      let question = this.containers.question_list[i]
      let question_inputs = question.querySelectorAll("input,textarea")

      for (let input of question_inputs) {
        input.question_index = i
        if (input.parentElement.classList.contains(this.kwargs.image_input_class_name)) {
          input.addEventListener("change", this.change_image_input, false)
        }
        input.addEventListener("input", this.change_question_input, false)
      }
      this.input_map[i] = question_inputs
      this.set_next_button_status(i, false)
    }
  }

  click_start_button (event) {
    this.show_response_form()
  }

  click_next_question(event) {
    if (event.currentTarget.getAttribute("disabled") != "true") {
      let question_index = event.currentTarget.next_question
      this.show_question_form(question_index)
    }
  }

  change_question_input (event) {
    let input = event.currentTarget
    if (input.type == "file") {
      let maxlength = parseInt(input.getAttribute("maxlength"))
      let errorlist = this.containers.question_list[input.question_index].querySelector(".errorlist")
      if (maxlength >= input.files.length) {
        if (errorlist) {errorlist.remove()}
        input.setCustomValidity("")
      } else {
        let message = `Selecciona máximo ${maxlength} archivo${maxlength > 1? 's': ''}`
        if (!errorlist) {
          let errorlist = document.createElement("div")
          errorlist.className = "errorlist"
          errorlist.textContent = message
          this.containers.question_list[input.question_index].insertBefore(
            errorlist, input.parentElement.parentElement
          )
        } else {errorlist.textContent = message}
        input.value = ""
        input.setCustomValidity(message)
        this.set_image_preview(input)
      }
    }
    this.set_next_button_status(input.question_index, true)
  }

  change_image_input (event) {
    this.set_image_preview(event.currentTarget)
  }

  set_next_button_status(question_index, report) {
    let next_question_button = this.buttons.next_question_list[question_index]
    let next_button = next_question_button ? next_question_button : this.buttons.submit
    let valid = true
    for (let input of this.input_map[question_index]) {
      valid &&= input.validity.valid
      if (report) {input.reportValidity()}
    }
    if (valid) {
      next_button.removeAttribute("disabled")
    } else {
      next_button.setAttribute("disabled", true)
    }
  }

  hide_all () {
    this.containers.detail.classList.add(this.hidden_class_name)
    this.containers.response.classList.add(this.hidden_class_name)
    for (let question of this.containers.question_list) {
        question.classList.add(this.hidden_class_name)
    }
  }

  show_detail_form () {
    this.hide_all()
    this.buttons.back.classList.add(this.hidden_class_name)
    this.containers.detail.classList.remove(this.hidden_class_name)
    this.focus = "detail"
  }

  show_response_form () {
    this.hide_all()
    this.buttons.back.classList.remove(this.hidden_class_name)
    this.containers.response.classList.remove(this.hidden_class_name)
    this.focus = "response"
  }

  show_question_form(question_index) {
    this.hide_all()
    this.buttons.back.classList.remove("hidden")
    this.containers.question_list[question_index].classList.remove(this.hidden_class_name)
    this.focus = question_index
  }

  show_back_form () {
    if (this.focus == "response") {
        this.show_detail_form()
    }
    else if (!isNaN(this.focus)) {
        if (this.focus == 0) {this.show_response_form()}
        else {this.show_question_form(this.focus - 1)}
    }
  }

  set_image_preview (input) {
    let files = input.files
    let input_container = input.parentElement
    let input_label = input.previousElementSibling
    let payload = ""
    for (var i = files.length - 1; i >= 0; i--) {
      let url = URL.createObjectURL(files[i])
      payload+=`url(${url})`
      if (i > 0) {payload+=", "}
    }
    if (payload != "") {
      input_container.style.backgroundImage = payload
    }

    if (files.length > 1) {
      input_label.innerText = `+${files.length - 1}`
      input_label.style.opacity = 1
    }

    if (files.length > 0) {
      input_container.firstElementChild.style.opacity = .5
    } else {
      input_container.firstElementChild.style.opacity = 1
    }
  }
}
