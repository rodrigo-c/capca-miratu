class QueryEditBase {
  constructor ({manager = null}) {
    this.manager = manager
    this.letters = "ABCDEFGHIJKLMNOPQRSTUXYZ"
    this.required_fields = ["name"]
    this.data = this._get_default_data()
    this.errors = {}
    this.buttons = {}

    this._click_more_attributes = this._click_more_attributes.bind(this)
    this._click_publish = this._click_publish.bind(this)

    this._dropdown_create_question = this._dropdown_create_question.bind(this)
    this._click_create_question = this._click_create_question.bind(this)
    this._move_question_ondragstart = this._move_question_ondragstart.bind(this)
    this._move_question_ondragend = this._move_question_ondragend.bind(this)
    this._move_question_ondrop = this._move_question_ondrop.bind(this)
    this._click_remove_question = this._click_remove_question.bind(this)

    this._click_question_add_option = this._click_question_add_option.bind(this)
    this._click_question_max_answers_menu = this._click_question_max_answers_menu.bind(this)
    this._click_question_max_answers_set = this._click_question_max_answers_set.bind(this)
    this._click_question_remove_option = this._click_question_remove_option.bind(this)

    this._set_initial()
    this._set_more_attrs()
    this._set_publish_button()
    this._set_create_question_button()
    this._set_query_inputs()
  }

  _get_default_data () {
    return {
        name: null,
        description: null,
        send_at: null,
        end_at: null,
        active: false,
        questions: [],
    }
  }
  _set_initial() {}

  _set_more_attrs() {
    let button = document.querySelector(`#query-${this.view_type}-more-attrs-button`)
    button.addEventListener("click", this._click_more_attributes, false)
  }

  _click_more_attributes (event) {
    let moreattrs = document.querySelector(`#query-${this.view_type}-more-attrs`)
    let button = document.querySelector(`#query-${this.view_type}-more-attrs-button`)
    if (moreattrs.classList.contains("hidden")) {
      moreattrs.classList.remove("hidden")
      button.classList.add("active")
    } else {
      moreattrs.classList.add("hidden")
      button.classList.remove("active")
    }
  }

  _set_publish_button () {
    let publish = document.querySelector(`#${this.view_type}-query-button`)
    publish.disabled = true
    publish.classList.add("disabled")
    publish.addEventListener("click", this._click_publish, false)
    this.buttons.publish = publish
  }

  _click_publish(event) {
    if (event.target.disabled == false) {
      this.manager.engine._set_loading()
      this.execute_service()
    }
  }

  execute_service () {}

  _clean_data() {
    this.data = this._get_default_data()
    this._build_question_from_data()
  }

  _set_query_inputs() {
    let name = document.querySelector(`#query-${this.view_type}-name`)
    let description = document.querySelector(`#query-${this.view_type}-description`)
    let start_at = document.querySelector(`.query-draft .start-at-input`)
    let end_at = document.querySelector(`.query-draft .end-at-input`)
    let active = document.querySelector(`#query-${this.view_type}-active`)
    let auth_email = document.querySelector(`#query-${this.view_type}-auth-email`)
    let auth_rut = document.querySelector(`#query-${this.view_type}-auth-rut`)
    this._change_input = this._change_input.bind(this)
    for (let input of [name, description, start_at, end_at, active, auth_email, auth_rut]) {
      input.field = input.getAttribute("field")
      input.addEventListener("input", this._change_input, false)
      if (this.data[input.field]) {
        input.value = this.data[input.field]
      }
    }
    this.error_containers = {}
    for (let field in this.data) {
      if (field != "questions") {
        let container = document.querySelector(`#query-${this.view_type}-${field}-error`)
        if (container) {
          this.error_containers[field] = container
        }
      }
    }
  }

  _set_errors_message() {
    for (let field in this.error_containers) {
      if (field != "questions") {
        this.error_containers[field].innerText = ""
      } else {
        for (let index in this.error_containers[field]) {
          for (let question_field in this.error_containers[field][index]) {
            this.error_containers[field][index][question_field].innerText = ""
          }
        }
      }
    }
    for (let field in this.errors) {
      if (field != "questions") {
        this.error_containers[field].innerText = this.errors[field]
      } else if (typeof this.errors[field] == "object") {
        for (let index in this.errors[field]) {
          for (let question_field in this.errors[field][index]) {
            this.error_containers[field][parseInt(index)][question_field].innerText = this.errors[field][index][question_field]
          }
        }
      }
    }
  }

  _change_input (event) {
    let field = event.target.field
    let value = event.target.value
    if (event.target.question) {
      if (field == "required") {
        value = event.target.checked? true: false
      }
      if (field == "question-option") {
        this.data.questions[event.target.index].options[event.target.option_index].name = value
      } else {
        this.data.questions[event.target.index][field] = value
      }
    } else {
      this.data[field] = value
    }
    this.validate_inputs()
    this._set_errors_message()
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
          if (question.kind == "SELECT") {
            this._val_question_options(question)
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
    if (this.required_fields.includes(field) && (!value || value.trim() == "")) {
      let message = "Este campo es requerido"
      this._set_field_error(field, message, question_index)
    } else {
      this._clean_field_error(field, question_index)
    }
  }

  _val_question_options(question) {
    let message = "Debe agregar al menos dos opciones y no pueden estar vacías"
    if (question.options.length < 2) {
      this._set_field_error("options", message, question.order)
    }
    let option_values = []
    for (let option of question.options) {
      if (!option.name || option.name.trim() == "") {
        this._set_field_error("options", message, question.order)
        break
      }
      if (option_values.includes(option.name)) {
        message = "Las opciones no pueden ser iguales"
        this._set_field_error("options", message, question.order)
        break
      }
      option_values.push(option.name)
    }
  }

  _set_field_error (field, message, question_index) {
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
  }

  _clean_field_error (field, question_index) {
    if (!isNaN(question_index) && this.errors.questions && this.errors.questions[question_index]) {
      delete this.errors.questions[question_index][field]
    }
    if (isNaN(question_index)) {
      delete this.errors[field]
    }
  }

  _set_create_question_button() {
    let button = document.querySelector(`#query-${this.view_type}-create-question-button`)
    button.addEventListener("click", this._dropdown_create_question, false)
    button.disabled = false
    this.buttons.new_question = button
    let kinds = Array.from(document.querySelectorAll(`#query-${this.view_type}-create-question-kinds .dropdown-item`))
    for (let kind of kinds) {
      kind.kind = kind.getAttribute("kind")
      kind.type = kind.getAttribute("type")
      kind.addEventListener("click", this._click_create_question, false)
    }
  }

  _dropdown_create_question(event) {
    let dropdown = document.querySelector(`#query-${this.view_type}-create-question-kinds`)
    if (!event.target.disabled) {
      if (dropdown.classList.contains("hidden")) {
        dropdown.classList.remove("hidden")
      } else {
        dropdown.classList.add("hidden")
      }
    }
  }

  _click_create_question (event) {
    let question = {
      kind: event.target.kind,
      name: null, description: null,
      required: false,
      order: this.data.questions.length,
    }
    if (event.target.kind === "TEXT") {
      if (event.target.type == "large") {
        question.text_max_length = 400
      } else {
        question.text_max_length = 150
      }
    } else if (event.target.kind == "SELECT") {
      question.options = []
    }
    this.data.questions.push(question)
    this._build_question_from_data()
    let dropdown = document.querySelector(`#query-${this.view_type}-create-question-kinds`)
    dropdown.classList.add("hidden")
  }

  _build_question_from_data() {
    let questions_container = document.querySelector(`#query-${this.view_type}-questions-tab`)
    questions_container.innerHTML = ""
    let index = 0
    for (let question_data of this.data.questions) {
      let question = this._create_question_element(question_data, index)
      questions_container.appendChild(question)
      let delete_button = question.querySelector(".action-delete")
      delete_button.addEventListener("click", this._click_remove_question, false)
      this._prepare_question_inputs(question, question_data, ["name", "description", "required"])
      this._set_question_draggable(question)
      this._set_question_error_containers(question)
      index += 1
    }
    this.validate_inputs()
  }

  _get_question_id(index) { return `query-${this.view_type}-question-item-${index}` }

  _create_question_element(question_data, index) {
    let question_id = this._get_question_id(index)
    var question = document.createElement("div")
    question.classList.add("question-item")
    question.index = index
    question.setAttribute("id", question_id)
    question.kind = question_data.kind
    question.innerHTML = `
      <div class="question-move-previous"></div>
      <div class="question-container">
        <div class="question-item-move">
          <i class="icon move"></i>
        </div>
        <div class="question-item-content">
          <input class="question-item-name"
                 id="query-${this.view_type}-${question_id}-name-input"
                 type="text"
                 field="name"
                 placeholder="Escribe tu pregunta aquí">
          </input>
          <div class="error-label" id="query-${this.view_type}-question-${index}-name-error"></div>
          <input class="question-item-description"
                 id="query-${this.view_type}-${question_id}-description-input"
                 type="text"
                 field="description"
                 placeholder="Agrega una descripción para esta pregunta (opcional)">
          </input>
          <div class="error-label" id="query-${this.view_type}-question-${index}-description-error"></div>
        </div>
        <div class="question-item-actions">
          <div class="action-delete"><i class="icon trash"></i></div>
          <div class="action-required">
            <label class="action-checkbox">
              <div class="action-label">Obligatorio</div>
              <input type="checkbox"
                     id="query-${this.view_type}-${question_id}-required-input"
                     field="required"
                     class="action-checkbox-input">
              </input>
              <span class="action-checkbox-checkmarker"></span>
            </label>
          </div>
        </div>
      </div>
      <div class="question-move-next"></div>
    `
    let question_content = question.querySelector(".question-item-content")
    if (question_data.kind === "TEXT") {
      let type = question_data.text_max_length > 150 ? "largo": "corto"
      question_content.innerHTML += `<div class="kind-text">Respuesta de texto ${type} (${question_data.text_max_length} caracteres)</div>`
    } else if (question_data.kind === "IMAGE") {
      question_content.innerHTML += `<div class="kind-image">Respuesta de imagen o foto</div>`
    } else if (question_data.kind === "POINT") {
      question_content.innerHTML += `<div class="kind-image">Ubicación</div>`
    } else if (question_data.kind === "SELECT") {
      this._set_question_options(question, question_data)
    }
    return question
  }

  _prepare_question_inputs(question, question_data, fields) {
    let question_id = this._get_question_id(question.index)
    for (let field of fields) {
      let element = question.querySelector(`#query-${this.view_type}-${question_id}-${field}-input`)
      element.field = field
      element.index = question.index
      element.question = true
      if (field === "required") {
        element.checked = question_data[field]
      } else {
        element.value = question_data[field]
      }
      element.addEventListener("input", this._change_input, false)
    }
  }

  _set_question_error_containers (question) {
    let base_id = "query-create"
    if (!this.error_containers.questions) {
      this.error_containers.questions = {}
    }
    if (!this.error_containers.questions[question.index]) {
      this.error_containers.questions[question.index] = {}
    }
    let fields = ["name", "description"]
    if (question.kind == "SELECT") {
      fields.push("options")
    }
    for (let field of fields) {
      this.error_containers.questions[question.index][field] = question.querySelector(
        `#query-${this.view_type}-question-${question.index}-${field}-error`
      )
    }
  }

  _click_remove_question(event) {
    let question = event.target.closest(".question-item")
    this.data.questions.splice(question.index, 1)
    this._build_question_from_data()
  }

  _set_question_options (question, question_data) {
    let question_content = question.querySelector(".question-item-content")
    let options_container = document.createElement("div")
    options_container.classList.add(".question-options-container")
    options_container.innerHTML = `
      <div class="question-option-list"></div>
      <div class="error-label" id="query-${this.view_type}-question-${question.index}-options-error"></div>
      <div class="question-option-add">+ Agregar opción</div>
    `
    let question_add_button = options_container.querySelector(".question-option-add")
    question_add_button.index = question.index
    question_add_button.addEventListener("click", this._click_question_add_option, false)
    question_content.appendChild(options_container)
    let option_list = options_container.querySelector(`.question-option-list`)
    let option_index = 0
    for (let option_data of this.data.questions[question.index].options) {
      let option = document.createElement("div")
      option.classList.add("question-option")
      let option_id = `query-${this.view_type}-question-option-${question.index}-${option_index}`
      option.innerHTML = `
        <div class="question-option-label">${this.letters[option_index]}.</div>
        <input id="${option_id}" type="text" class="question-option-input" placeholder="Opción ${option_index + 1}">
        <div class="question-option-delete">X</div>
      `
      let input = option.querySelector(".question-option-input")
      input.field = "question-option"
      input.index = question.index
      input.question = true
      input.option_index = option_index
      input.value = option_data.name
      input.addEventListener("input", this._change_input, false)
      let delete_button = option.querySelector(".question-option-delete")
      delete_button.index = question.index
      delete_button.option_index = option_index
      delete_button.addEventListener("click", this._click_question_remove_option, false)
      option_index += 1
      option_list.appendChild(option)
    }
    this._set_question_max_answers(question, question_data)
  }

  _click_question_remove_option(event) {
    let question = event.target.closest(".question-item")
    this.data.questions[question.index].options.splice(event.target.option_index, 1)
    this._build_question_from_data()
    this.validate_inputs()
    this._set_errors_message()
  }

  _set_question_max_answers (question, question_data) {
    let actions = question.querySelector(".question-item-actions")
    actions.innerHTML = `
      <div class="action-max-answers">
        <div class="action-max-answers-button">
          <span class="action-label">Cantidad de respuestas</span> <i class="icon bottom"></i>
        </div>
        <div class="action-max-answers-dropdown hidden"></div>
      </div>
    ` + actions.innerHTML
    let button = actions.querySelector(".action-max-answers-button")
    button.addEventListener("click", this._click_question_max_answers_menu, false)
    let dropdown = actions.querySelector(".action-max-answers-dropdown")
    for (let i = 0; i < 5; i++) {
      let option = document.createElement("div")
      option.classList.add("action-max-answers-option")
      option.value = i + 1
      let message = `${i + 1} respuesta`
      if (option.value == this.data.questions[question.index].max_answers) {
        actions.querySelector(".action-label").innerText = message
      }
      if (i > 0) { message += "s" }
      option.innerText = message
      option.addEventListener("click", this._click_question_max_answers_set, false)
      dropdown.appendChild(option)
    }
  }

  _click_question_add_option (event) {
    let question = event.target.closest(".question-item")
    let order = this.data.questions[question.index].options.length
    let empty_option = {
      name: null, order: order
    }
    this.data.questions[question.index].options.push(empty_option)
    this._build_question_from_data()
    this.validate_inputs()
    this._set_errors_message()
  }

  _click_question_max_answers_menu(event) {
    let question = event.target.closest(".question-item")
    let dropdown = question.querySelector(".action-max-answers-dropdown")
    if (dropdown.classList.contains("hidden")) {
      dropdown.classList.remove("hidden")
    } else {
      dropdown.classList.add("hidden")
    }
  }

  _click_question_max_answers_set (event) {
    let question = event.target.closest(".question-item")
    let button_label = question.querySelector(".action-max-answers .action-label")
    let dropdown = question.querySelector(".action-max-answers-dropdown")
    this.data.questions[question.index].max_answers = event.target.value
    button_label.innerText = event.target.innerText
    dropdown.classList.add("hidden")
  }

  _set_question_draggable (question) {
    let container = question.querySelector(".question-container")
    container.draggable = true
    container.ondragstart = this._move_question_ondragstart
    container.ondragend = this._move_question_ondragend
    let move_previous = question.querySelector(".question-move-previous")
    let move_next = question.querySelector(".question-move-next")
    move_previous.ondragenter = () => move_previous.classList.add("active")
    move_previous.ondragleave = () => move_previous.classList.remove("active")
    move_next.ondragenter = () => move_next.classList.add("active")
    move_next.ondragleave = () => move_next.classList.remove("active")
    move_previous.ondragover = (event) => event.preventDefault()
    move_previous.ondrop = this._move_question_ondrop
    move_previous.kind = "previous"
    move_next.ondragover = (event) => event.preventDefault()
    move_next.kind = "next"
    move_next.ondrop = this._move_question_ondrop
  }

  _move_question_ondragstart(event) {
    let question = event.target.closest(".question-item")
    let questions_container = document.querySelector(`#${this.view_type}-questions-tab`)
    this.current_pos = question.index
    setTimeout(()=> { question.style.display = "none"}, 0)
    questions_container.style.heigth = questions_container.clientHeigth - question.clientHeigth + "px"
  }

  _move_question_ondragend (event) {
    let questions_container = document.querySelector(`#${this.view_type}-questions-tab`)
    for (let question of questions_container.children) {
      question.style.display = "flex"
      question.querySelector(".question-move-previous").classList.remove("active")
      question.querySelector(".question-move-next").classList.remove("active")
    }
  }

  _move_question_ondrop(event) {
    event.preventDefault()
    let question = event.target.closest(".question-item")
    let kind = event.target.kind
    let total_questions = this.data.questions.length
    let to_index = null
    if (kind == "previous") {
      to_index = question.index - 1 < 0? 0 : question.index
    }

    else if (kind == "next") {
      to_index = question.index
    }
    if (this.current_pos === to_index) {
      return
    }
    let questions = [...this.data.questions]
    let moved_question = {...questions[this.current_pos]}
    questions = questions.filter(q => q.order != moved_question.order)
    questions.splice(to_index, 0, moved_question)
    this.data.questions = questions
    this._set_question_data_order()
    this._build_question_from_data()
  }

  _set_question_data_order () {
    let index = 0
    for (let question of this.data.questions) {
      question.order = index
      index += 1
    }
  }
}


class QueryCreateManager extends QueryEditBase {
  _set_initial() {
    this.view_type = "create"
  }

  execute_service() {
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
        response.json()
        .then((data)=> {
          this.errors = {...this.errors, ...data}
          this._set_errors_message()
          this.manager.engine._hide_all_views()
          this.manager.engine.views.query_create.classList.remove("hidden")
        })
      }
    })
  }

  show_view(on_history) {
    this.manager.engine._hide_all_views()
    this._clean_data()
    this.manager.engine.views.query_create.classList.remove("hidden")
    if (on_history) {
      this.manager.engine._set_url_params("query-create", null)
    }
  }

}

export {QueryCreateManager}
