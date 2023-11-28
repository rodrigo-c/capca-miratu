/* Public query submit view */

class QuerySubmitManager {
  constructor (
    {
      detail_id = "detail-container",
      response_id = "response-container",
      question_class_name = "question",
      hidden_class_name = "hidden",
      focus = "detail",
      back_button_id = "back-button"
    } = {}
  ) {
    this.detail = document.getElementById(detail_id);
    this.response = document.getElementById(response_id);
    this.question_list = document.getElementsByClassName(question_class_name);
    this.hidden_class_name = hidden_class_name;
    this.back_button = document.getElementById(back_button_id)
    this.image_fields = document.getElementsByClassName("image-input");
    this._add_listener_events();
    if (!isNaN(focus)) {
        focus = parseInt(focus)
    }
    this.focus = focus;
  }

  _add_listener_events() {
    var start_button = document.getElementById("start-button")
    var next_response_button = document.getElementById("next-response-button")
    this.callback_show_response_form = this.callback_show_response_form.bind(this)
    this.callback_show_question_form = this.callback_show_question_form.bind(this)
    this.show_back_form = this.show_back_form.bind(this)
    this.set_image_preview = this.set_image_preview.bind(this)
    start_button.addEventListener("click", this.callback_show_response_form, false)
    next_response_button.addEventListener("click", this.callback_show_question_form, false)
    next_response_button.question_index = 0
    for (var i = this.question_list.length - 1; i >= 0; i--) {
        var next_question_button = document.getElementById(`next-question-button-${i}`)
        if (next_question_button) {
            next_question_button.addEventListener("click", this.callback_show_question_form, false)
            next_question_button.question_index = i + 1
        }
    }
    this.back_button.addEventListener("click", this.show_back_form, false)
    for (let image_field of this.image_fields) {
      image_field.lastElementChild.addEventListener("change", this.set_image_preview, false)
    }
  }

  hide_all () {
    this.detail.classList.add(this.hidden_class_name)
    this.response.classList.add(this.hidden_class_name)
    for (let question of this.question_list) {
        question.classList.add(this.hidden_class_name)
    }
  }

  show_detail_form () {
    this.hide_all()
    this.back_button.classList.add(this.hidden_class_name)
    this.detail.classList.remove(this.hidden_class_name)
    this.focus = "detail"
  }

  show_response_form () {
    this.hide_all()
    this.back_button.classList.remove(this.hidden_class_name)
    this.response.classList.remove(this.hidden_class_name)
    this.focus = "response"
  }

  callback_show_response_form (event) {
    this.show_response_form()
  }

  show_question_form(question_index) {
    this.hide_all()
    this.back_button.classList.remove("hidden")
    this.question_list[question_index].classList.remove(this.hidden_class_name)
    this.focus = question_index
  }

  callback_show_question_form(event) {
    var question_index = event.currentTarget.question_index
    this.show_question_form(question_index)
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

  set_image_preview (event) {
    let files = event.currentTarget.files
    let input_container = event.currentTarget.parentElement
    let input_label = event.currentTarget.previousElementSibling
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
