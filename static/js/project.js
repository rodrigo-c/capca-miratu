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
      varset = []
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
      varset,
    }
    this.hidden_class_name = hidden_class_name;
    this._set_focus(focus)
    this._set_containers()
    this._set_buttons()
    this.input_map = {}
    this._set_response_inputs()
    this._set_question_inputs()
    this._set_response_geolocation()
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

  _set_response_inputs () {
    this.change_response_input = this.change_response_input.bind(this)
    let inputs = this.containers.response.querySelectorAll("input,textarea")
    for (let input of inputs) {
      input.addEventListener("input", this.change_response_input, false)
    }
    this.input_map.response = Array.from(inputs)
  }

  _set_question_inputs() {
    this.change_question_input = this.change_question_input.bind(this)
    for (let i = this.containers.question_list.length - 1; i >= 0; i--) {
      let question = this.containers.question_list[i]
      let question_inputs = question.querySelectorAll("input,textarea")

      for (let input of question_inputs) {
        input.question_index = i
        input.addEventListener("input", this.change_question_input, false)
        if (input.type == "checkbox") {
          this.validate_options_question(input, false)
        }
        if (input.classList.contains("vSerializedField")) {
          this._set_point_input_event(input)
          this.validate_point_question(input, false)
        }
      }
      this.input_map[i] = Array.from(question_inputs)
      this.set_next_button_status(i, false)
    }
  }

  _set_point_input_event(input) {
    for (var i = this.kwargs.varset.length - 1; i >= 0; i--) {
      if (i == input.question_index) {
        let var_name = this.kwargs.varset[i]
        try {
          let mapwidget = eval(var_name)
          let _serializeFeatures = mapwidget.serializeFeatures
          let _clearFeatures = mapwidget.clearFeatures
          _serializeFeatures = _serializeFeatures.bind(mapwidget)
          _clearFeatures = _clearFeatures.bind(mapwidget)
          mapwidget.serializeFeatures = () => {
            _serializeFeatures()
            input.dispatchEvent(new Event("input"))
          }
          mapwidget.clearFeatures = () => {
            _clearFeatures()
            input.dispatchEvent(new Event("input"))
          }
          mapwidget.map.getView().setCenter(
            ol.proj.transform([-70.668423, -33.447869], 'EPSG:4326', 'EPSG:3857')
          )
        } catch (e){
          console.log(e)
        }
      }
    }
  }

  _set_response_geolocation () {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition((position) => {
        this.user_location = {
          lon: position.coords.longitude,
          lat: position.coords.latitude,
        }
        let geolocation_input = this.containers.response.querySelector("input[name='location']")
        geolocation_input.value = `POINT(${this.user_location.lon} ${this.user_location.lat})`;
        for (let var_name of this.kwargs.varset) {
          try {
            eval(var_name).map.getView().setCenter(
              ol.proj.transform([this.user_location.lon, this.user_location.lat], 'EPSG:4326', 'EPSG:3857')
            )
          } catch (e){
            console.log(e)
          }
        }
      })
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

  change_response_input (event) {
    let input = event.currentTarget
    let button = this.buttons.start_questions
    let valid = true
    for (let input of this.input_map.response) {
      if (input.getAttribute("name") == "rut") {
        this.validate_rut(input)
      }
      valid &&= input.validity.valid
      input.reportValidity()
    }
    if (valid) {
      button.removeAttribute("disabled")
    } else {
      button.setAttribute("disabled", true)
    }
  }

  change_question_input (event) {
    let input = event.currentTarget
    if (input.type == "file") {
      this.validate_image_question(input)
    }
    if (input.type == "checkbox") {
      this.validate_options_question(input, true)
    }
    if (input.classList.contains("vSerializedField")) {
      this.validate_point_question(input, true)
    }
    this.set_next_button_status(input.question_index, true)
  }

  validate_rut(input) {
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

  validate_image_question(input) {
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
    }
    this.set_image_preview(input)
  }

  validate_options_question(input, report) {
    let field_container =  this.containers.question_list[input.question_index].querySelector("[field='options']")
    let maxlength = parseInt(field_container.getAttribute("maxlength"))
    let required = field_container.hasAttribute("required")
    let checked_inputs = Array.from(field_container.querySelectorAll("input")).filter(input=>input.checked).length
    let errorlist = this.get_error_list(input.question_index)

    if (errorlist) {errorlist.remove()}
    input.setCustomValidity("")
    if (checked_inputs > maxlength && input.checked) {
      let message = `Seleccione máximo ${maxlength} respuesta${maxlength > 1? 's': ''}`
      this.create_error_list(input, message)
      input.checked = false
    }
    else if (required && checked_inputs == 0 && !input.checked) {
      let message = `Debe seleccionar al menos una opción`
      if (report) {this.create_error_list(input, message)}
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

  validate_point_question (input, report) {
    let field_container =  this.containers.question_list[input.question_index].querySelector("[field='point']")
    let required = field_container.hasAttribute("required")
    let errorlist = this.get_error_list(input.question_index)
    if (errorlist) {errorlist.remove()}
    input.setCustomValidity("")

    if (required && !input.value) {
      let message = "Debe seleccionar un punto en el mapa"
      if (report) {this.create_error_list(input, message)}
      input.setCustomValidity(message)
    }
  }

  get_error_list(question_index) {
    return this.containers.question_list[question_index].querySelector(".errorlist")
  }

  create_error_list(input, message) {
    let errorlist = document.createElement("div")
    let container = this.containers.question_list[input.question_index]
    errorlist.className = "errorlist"
    errorlist.textContent = message
    container.insertBefore(
      errorlist, container.querySelector(".form-field")
    )
  }

  set_next_button_status(question_index, report) {
    let next_question_button = this.buttons.next_question_list[question_index]
    let next_button = next_question_button ? next_question_button : this.buttons.submit
    let valid = true
    for (let input of this.input_map[question_index]) {
      valid &&= input.validity.valid
      if (!valid && report) {input.reportValidity()}
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
    } else {
      input_container.style.backgroundImage = null
    }

    if (files.length > 1) {
      input_label.innerText = `+${files.length - 1}`
      input_label.style.opacity = 1
    } else {
      input_label.style.opacity = 0
    }

    if (files.length > 0) {
      input_container.firstElementChild.style.opacity = .5
    } else {
      input_container.firstElementChild.style.opacity = 1
    }
  }
}

// need https://leafletjs.com/
function set_answer_result_map (id, dataset) {
  let latlng = L.latLng(-33.447869, -70.668423)
  let map = L.map(id).setView(latlng, 9)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
  }).addTo(map);
  map.attributionControl.setPrefix("")

  for (answer of dataset) {
    if (answer.point) {
      let marker = L.marker(answer.point).addTo(map)
      let message = `<b>Enviado en: </b> ${new Date(answer.send_at)}`
      marker.bindPopup(message)
    }
  }
  return map
}
