class QueryCreateManager {
  constructor ({manager = null}) {
    this.manager = manager
    this.data = {
        name: null,
        description: null,
        send_at: null,
        end_at: null,
        active: false,
        questions: [],
    }
    this.letters = "ABCDEFGHIJKLMNOPQRSTUXYZ"
    this.required_fields = ["name"]
    this.errors = {}
    this.can_publish = false
    this.buttons = {}
    this.query_inputs = {}
    this._set_more_attrs()
    this._set_publish_button()
    this._set_create_question_button()
    this._set_query_inputs()

    this._click_question_option_delete = this._click_question_option_delete.bind(this)
  }

  _set_more_attrs() {
    this._click_more_attributes = this._click_more_attributes.bind(this)
    let button = document.querySelector("#query-create-more-attrs-button")
    button.addEventListener("click", this._click_more_attributes, false)
  }

  _click_more_attributes (event) {
    let moreattrs = document.querySelector("#query-create-more-attrs")
    let button = document.querySelector("#query-create-more-attrs-button")
    if (moreattrs.classList.contains("hidden")) {
      moreattrs.classList.remove("hidden")
      button.classList.add("active")
    } else {
      moreattrs.classList.add("hidden")
      button.classList.remove("active")
    }
  }

  _set_publish_button () {
    let publish = document.querySelector("#create-query-button")
    let new_question = document.querySelector("#create-question-button")
    publish.disabled = true
    publish.classList.add("disabled")
    this._click_publish = this._click_publish.bind(this)
    publish.addEventListener("click", this._click_publish, false)
    this.buttons.publish = publish
  }

  _click_publish(event) {
    if (event.target.disabled == false) {
      this.manager.engine._set_loading()
      fetch(this.manager.url_base, {
        method: "POST",
        body: JSON.stringify(this.data),
        headers: {"Content-Type": "application/json", "X-CSRFToken": this.manager.engine.csrf_token},
        credentials: "same-origin"
      })
      .then((response) => {
        if (response.ok) {
          response.json()
          .then((data)=> {
            if (data.uuid) {
              this.manager.engine.cursor.key = data.uuid
              this.manager.engine.show_view("query-detail", true)
              this._clean_data()
            } else {
              console.log(data)
            }
          })
        } else {
          console.log(response)
        }
      })
    }
  }

  _clean_data() {
    this.data = {
      name: null,
      description: null,
      send_at: null,
      end_at: null,
      active: false,
      questions: [],
    }
    for (let field in this.query_inputs) {
      this.query_inputs[field].value = ""
    }
    document.querySelector("#create-questions-tab").innerText = ""
  }

  _set_create_question_button() {
    this._dropdown_create_question = this._dropdown_create_question.bind(this)
    this._click_create_question = this._click_create_question.bind(this)
    let button = document.querySelector("#create-question-button")
    button.addEventListener("click", this._dropdown_create_question, false)
    button.disabled = false
    this.buttons.new_question = button
    let kinds = Array.from(document.querySelectorAll("#create-question-options .dropdown-item"))
    for (let kind of kinds) {
      kind.kind = kind.getAttribute("kind")
      kind.addEventListener("click", this._click_create_question, false)
    }
  }

  _dropdown_create_question(event) {
    let dropdown = document.querySelector("#create-question-options")
    if (!event.target.disabled) {
      if (dropdown.classList.contains("hidden")) {
        dropdown.classList.remove("hidden")
      } else {
        dropdown.classList.add("hidden")
      }
    }
  }

  _click_create_question (event) {
    let questions_container = document.querySelector("#create-questions-tab")
    let index = questions_container.childElementCount
    let question = this._create_empty_question(event.target.kind, event.target.getAttribute("type"), index)
    this.data.questions.push(this._get_question_data(question))
    questions_container.appendChild(question)
    this.validate_inputs()
    event.target.parentElement.classList.add("hidden")
  }

  _create_empty_question (kind, type, index) {
    let container = document.createElement("div")
    container.index = index
    container.classList.add("question-item")
    let question_id = `question-item-${index}`
    container.setAttribute("id", question_id)
    container.kind = kind
    container.innerHTML = `
      <div class="question-item-move">
        <i class="icon move"></i>
      </div>
      <div class="question-item-content">
        <input class="question-item-name"
               id="${question_id}-name-input"
               field="name"
               type="text"
               question="true"
               placeholder="Escribe tu pregunta aquí">
        </input>
        <input class="question-item-description"
               id="${question_id}-description-input"
               field="description"
               type="text"
               question="true"
               placeholder="Agrega una descripción para esta pregunta (opcional)">
        </input>
      </div>
      <div class="question-item-actions">
        <div class="action-delete"><i class="icon trash"></i></div>
        <div class="action-required">
          <label class="action-checkbox">
            <div class="action-label">Obligatorio</div>
            <input type="checkbox"
                   id="${question_id}-required-input"
                   class="action-checkbox-input"
                   field="required"
                   question="true">
            </input>
            <span class="action-checkbox-checkmarker"></span>
          </label>
        </div>
      </div>
    `
    this._set_change_question_input(container,)
    this._click_delete_question = this._click_delete_question.bind(this)
    let delete_button = container.querySelector(".action-delete")
    delete_button.querySelector(".icon.trash").index = index
    delete_button.index = index
    delete_button.addEventListener("click", this._click_delete_question, false)
    if (kind === "TEXT") {
      this._set_text_question(container, type)
    } else if (kind == "SELECT") {
      this._set_select_question(container)
    } else if (kind == "IMAGE") {
      this._set_image_question(container)
    } else if (kind == "POINT") {
      this._set_point_question(container)
    }

    return container
  }

  _set_text_question(question, type) {
    let question_content = question.querySelector(".question-item-content")
    let text_input = document.createElement("input")
    text_input.classList.add("kind-text")
    text_input.setAttribute("type", "text")
    text_input.setAttribute("disabled", "true")
    if (type === "large") {
      text_input.setAttribute("placeholder", "Respuesta de texto largo (400 caracteres)")
      question.maxlength = 400
    } else {
      text_input.setAttribute("placeholder", "Respuesta de texto corto (150 caracteres)")
      question.maxlength = 150
    }
    question_content.appendChild(text_input)
  }

  _set_image_question (question) {
    let question_content = question.querySelector(".question-item-content")
    let text_input = document.createElement("input")
    text_input.classList.add("kind-text")
    text_input.setAttribute("type", "text")
    text_input.setAttribute("disabled", "true")
    text_input.setAttribute("placeholder", "Imagen o foto")
    question_content.appendChild(text_input)
  }

  _set_point_question (question) {
    let question_content = question.querySelector(".question-item-content")
    let text_input = document.createElement("input")
    text_input.classList.add("kind-text")
    text_input.setAttribute("type", "text")
    text_input.setAttribute("disabled", "true")
    text_input.setAttribute("placeholder", "Ubicación")
    question_content.appendChild(text_input)
  }

  _set_select_question(question) {
    let question_content = question.querySelector(".question-item-content")
    let options_container = document.createElement("div")
    options_container.classList.add(".question-options-container")
    options_container.innerHTML = `
      <div class="question-option-list"></div>
      <div class="question-option-add">+ Agregar opción</div>
    `
    this._click_question_option_add = this._click_question_option_add.bind(this)
    let question_add_button = options_container.querySelector(".question-option-add")
    question_add_button.index = question.index
    question_add_button.addEventListener("click", this._click_question_option_add, false)
    question_content.appendChild(options_container)
  }

  _click_question_option_add(event) {
    let question_index = event.target.index
    let question_id = `question-item-${question_index}`
    let option_list = document.querySelector(`#${question_id} .question-option-list`)
    let index = option_list.childElementCount
    let option = document.createElement("div")
    let option_id = `question-option-${question_index}-${index}`
    option.classList.add("question-option")
    option.setAttribute("id", option_id)
    option.innerHTML = `
      <div class="question-option-label">${this.letters[index]}.</div>
      <input type="text" class="question-option-input" placeholder="Opción ${index + 1}" question="true">
      <div class="question-option-delete">X</div>
    `
    let input = option.querySelector(".question-option-input")
    input.field = "question-option"
    input.index = question_index
    input.option_index = index
    input.addEventListener("input", this._change_input, false)
    let delete_button = option.querySelector(".question-option-delete")
    delete_button.index = question_index
    delete_button.option_index = index
    delete_button.addEventListener("click", this._click_question_option_delete, false)
    let option_data = {
      name: null, order: index,
    }
    if (!this.data.questions[question_index].options) {
      this.data.questions[question_index].options = []
    }
    this.data.questions[question_index].options.push(option_data)
    //max answers

    option_list.appendChild(option)
  }

  _click_question_option_delete (event) {
    let question_index = event.target.index
    let option_index = event.target.option_index
    let option_id = `question-option-${question_index}-${option_index}`
    let option = document.querySelector(`#${option_id}`)
    this.data.questions[question_index].options.splice(option_index, 1)
    let option_list = option.parentElement
    option.remove()
    let index = 0
    for (let option of option_list.children) {
      let option_id = `question-option-${question_index}-${index}`
      option.setAttribute("id", option_id)
      let input = option.querySelector(".question-option-input")
      input.index = question_index
      input.option_index = index
      input.setAttribute("placeholder", `Opción ${index+1}`)
      this.data.questions[question_index].options[index].order = index
      let delete_button = option.querySelector(".question-option-delete")
      delete_button.index = question_index
      delete_button.option_index = index
      option.querySelector(".question-option-label").innerText = `${this.letters[index]}.`
      index += 1
    }
  }

  _set_change_question_input (question) {
    let name = question.querySelector(".question-item-name")
    let description = question.querySelector(".question-item-description")
    let required = question.querySelector(".action-checkbox-input[field='required']")
    for (let input of [name, description, required]) {
      input.field = input.getAttribute("field")
      input.index = question.index
      input.addEventListener("input", this._change_input, false)
    }
  }

  _click_delete_question (event) {
    let index = event.target.index
    let question_id = `question-item-${index}`
    let question = document.querySelector(`#${question_id}`)
    this.data.questions.splice(index, 1)
    question.remove()
    this._set_questions_order()
    this.validate_inputs()
  }

  _set_questions_order() {
    let questions_container = document.querySelector("#create-questions-tab")
    let counter = 0
    for (let question of questions_container.children) {
      this.data.questions[counter].order = counter
      question.index = counter
      let question_id = `question-item-${counter}`
      question.setAttribute("id", question_id)
      let name = question.querySelector(".question-item-name")
      let description = question.querySelector(".question-item-description")
      let required = question.querySelector(".action-checkbox-input[field='required']")
      let delete_button = question.querySelector(".action-delete")
      delete_button.index = counter
      for (let input of [name, description, required]) {
        input.index = counter
      }
      let inputs = Array.from(question.querySelectorAll(".question-option-input"))
      for (let input of inputs) {
        input.index = counter
      }
      counter += 1
    }
  }

  _get_question_data(question) {
    let name_input = question.querySelector("input[field='name']")
    let description_input = question.querySelector("input[field='description']")
    let question_data = {
      kind: question.kind,
      name: name_input.value,
      description: description_input.value,
      order: question.index,
      required: false,
    }
    if (question.kind == "TEXT") {
      question_data.text_max_length = question.maxlength
    }
    return question_data
  }

  _set_query_inputs() {
    let name = document.querySelector("#query-create-name")
    let description = document.querySelector("#query-create-description")
    let start_at = document.querySelector(".query-draft .start-at-input")
    let end_at = document.querySelector(".query-draft .end-at-input")
    let active = document.querySelector("#query-create-active")
    let auth_email = document.querySelector("#query-create-auth-email")
    let auth_rut = document.querySelector("#query-create-auth-rut")
    this._change_input = this._change_input.bind(this)
    for (let input of [name, description, start_at, end_at, active, auth_email, auth_rut]) {
      input.field = input.getAttribute("field")
      input.addEventListener("input", this._change_input, false)
      this.query_inputs[input.field] = input
    }
  }

  _change_input (event) {
    let field = event.target.field
    let value = event.target.value
    if (event.target.hasAttribute("question")) {
      if (field == "required") {
        value = event.target.checked? true: false
      }
      if (field == "question-option") {
        this.data.questions[event.target.index].options[event.target.option_index].name = value
      }
      this.data.questions[event.target.index][field] = value
    } else {
      this.data[field] = value
    }
    this.validate_inputs()
  }

  validate_inputs() {
    this.errors = {}
    let no_question_message = "Debe crear al menos una pregunta"
    if (this.data.questions.length == 0) {
      this.errors.questions = no_question_message
    } else {
      delete this.errors.questions
    }
    for (let field in this.data) {
      if (field == "questions") {
        for (let question of this.data.questions) {
          for (let field in question) {
            let value = question[field]
            this._val_field_value_is_required(field, value, question.order)
          }
        }
      } else {
        let value = this.data[field]
        this._val_field_value_is_required(field, value)
      }
    }
    if (this.errors.questions && this.errors.questions.length == 0) {
      delete this.errors.questions
    }
    if (this.errors.questions && this.errors.questions != no_question_message) {
      this.buttons.new_question.disabled = true
      this.buttons.new_question.classList.add("disabled")
    } else {
      this.buttons.new_question.disabled = false
      this.buttons.new_question.classList.remove("disabled")
    }
    if (
      Object.keys(this.errors).length === 0
      && this.errors.constructor === Object
    ) {
      this.buttons.publish.classList.remove("disabled")
      this.buttons.publish.disabled = false
    } else {
      this.buttons.publish.classList.add("disabled")
      this.buttons.publish.disabled = true
    }
  }

  _val_field_value_is_required(field, value, question_index) {
    if (this.required_fields.includes(field) && (!value || value == "")) {
      let message = "Este campo es requerido"
      if (!isNaN(question_index)) {
        if (!this.errors.questions) {
          this.errors.questions = {}
        }
        if (!this.errors.questions[question_index]) {
          this.errors.questions[question_index] = {}
        }
        this.errors.questions[question_index][field] = message
      } else {
        this.errors[field] = message
      }
    } else {
      if (!isNaN(question_index) && this.errors.questions && this.errors.questions[question_index]) {
        delete this.errors.questions[question_index][field]
      }
      if (isNaN(question_index)) {
        delete this.errors[field]
      }
    }
  }

  show_view(on_history) {
    this._set_in_view()
    if (on_history) {
      this.manager.engine._set_url_params("query-create", null)
    }
  }

  _set_in_view() {
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_create.classList.remove("hidden")

  }

}

export {QueryCreateManager}
