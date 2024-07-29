import {
  get_chart
} from "../charts.js"

class QueryResultManager {
  constructor ({manager = null, kind = null}) {
    this.manager = manager
    this.data = {}
    this.kind = kind
    this.charts = {summary: null, questions: []}
    this.map = null
    this.data_table = null
    this.marker_focus = null
    this.map_markers = {}
    this._click_download_link = this._click_download_link.bind(this)
    this._click_download_dropdown = this._click_download_dropdown.bind(this)
    this._click_map_shapes_button = this._click_map_shapes_button.bind(this)
    this._click_map_shape_action = this._click_map_shape_action.bind(this)
    this._click_response_visibility = this._click_response_visibility.bind(this)
    this._set_row_callback = this._set_row_callback.bind(this)
    this._set_pre_in_view()
  }

  _set_pre_in_view () {
    let tab_links = document.querySelector(`.view.query-${this.kind} .result.tab-links`)
    let click_got_to = this.manager._click_go_to_view.bind(this.manager)
    for (let tab_link of tab_links.children) {
      tab_link.addEventListener("click", click_got_to, false)
    }
    this._set_download_links()
  }

  _set_download_links () {
    let dropdown_button = document.querySelector(`#query-${this.kind}-download-button`)
    dropdown_button.addEventListener("click", this._click_download_dropdown, false)
    let excel_link = document.querySelector(`#query-${this.kind}-download-excel`)
    excel_link.kind = "excel"
    let geojson_link = document.querySelector(`#query-${this.kind}-download-geojson`)
    geojson_link.kind = "geojson"
    let images_link = document.querySelector(`#query-${this.kind}-download-images`)
    images_link.kind = "images-zip"
    for (let element of [excel_link, geojson_link, images_link]) {
      element.addEventListener("click", this._click_download_link, false)
    }
  }

  _click_download_dropdown (event) {
    let dropdown_content = document.querySelector(`#query-${this.kind}-dropdown`)
    if (dropdown_content.classList.contains("hidden")) {
      dropdown_content.classList.remove("hidden")
    } else {
      dropdown_content.classList.add("hidden")
    }
  }

  _click_download_link (event) {
    let kind = event.target.kind
    if (["geojson", "excel"].includes(kind)) {
      let link = `${this.manager.url_base}${this.manager.engine.cursor.key}/${event.target.kind}/`
      window.open(link)
    }
    if (kind === "images-zip") {
      this._donwload_images()
    }
    document.querySelector(`#query-${this.kind}-dropdown`).classList.add("hidden")
  }

  _donwload_images () {
    const _get_image_fields = (data) => {
      let images_fields = []
      for (let question of data.query.questions) {
        if (question.kind === "IMAGE") {
          let field = `pregunta_${question.index + 1}`
          images_fields.push(field)
        }
      }
      return images_fields.length === 0 ? null : images_fields
    }

    const _get_image_data_list = (data, fields) => {
      let image_data_list = []
      for (let response of data.dataset) {
        if (response.visible === "True") {
          let base_data = {
            "response": {send_at: response.send_at, uuid: response.uuid}
          }
          for (let field of fields) {
            let original = response[field] === "" ? null : response[field].original
            if (original) {
              let url = response[field].thumb_medium
              let extension = url.slice(url.length - 3)
              let image_data = {...base_data, url, extension, field}
              image_data_list.push(image_data)
            }
          }
        }
      }
      return image_data_list.length > 0 ? image_data_list : null
    }

    const _create_async_download = (image_data) => {
      return new Promise((resolve, reject) => {
        let image_blob = fetch(image_data.url).then(response => response.blob());
        resolve({...image_data, blob: image_blob})
      })
    }

    const _download_image_callback = (results, query_url_code) => {
      let zip = new JSZip()
      let folder = zip.folder("images")
      for (let image_data of results) {
        let response = image_data.response
        let filename = `${response.send_at}-${image_data.field}-${response.uuid}.${image_data.extension}`
        folder.file(filename, image_data.blob)
      }
      folder.generateAsync({type: "blob"}).then(content => saveAs(content, `consulta-imagenes-${query_url_code}-${new Date().toLocaleDateString()}`))
    }

    fetch (`${this.manager.url_base}${this.manager.engine.cursor.key}/data/`, {
      method: "GET",
      headers: {"Content-Type": "application/json"},
      credentials: "same-origin"
    })
    .then(response=> {
      if (response.ok) {
        response.json()
        .then((data)=> {
          let images_fields = _get_image_fields(data)
          let image_data_list = _get_image_data_list(data, images_fields)
          let tasks = []
          for (let image_data of image_data_list) {
            let task = _create_async_download(image_data)
            tasks.push(task)
          }
          let results = []
          let task_completed = 0
          tasks.forEach((task) => {
            task.then((value)=> {
              results.push(value)
            })
            .catch((error)=> console.log(error))
            .finally(() => {
              task_completed++
              if (task_completed >= tasks.length) {
                _download_image_callback(results, data.query.url_code)
              }
            })
          })
        })
      } else {
        console.log(response)
      }
    })
  }

  show_view(on_history) {
    let suffix = `${["result", "questions"].includes(this.kind)? '' : this.kind}`
    fetch (`${this.manager.url_base}${this.manager.engine.cursor.key}/${suffix}`, {
      method: "GET",
      headers: {"Content-Type": "application/json"},
      credentials: "same-origin"
    })
    .then(response=> {
      if (response.ok) {
        response.json()
        .then((data)=> {
          this.data = data
          this._set_in_view()
          if (on_history) {
            this.manager.engine._set_url_params(`query-${this.kind}`, data.query.url_code)
          }
        })
      } else {
        console.log(response)
        this.manager.engine.show_view("query-list", false)
      }
    })
  }

  _set_in_view() {
    this.manager._build_sidebar()
    if (this.kind == "result") {
      this._set_summary()
    } else if (this.kind == "questions") {
      this._set_questions()
    } else if (this.kind == "map") {
      this._set_map()
    } else if (this.kind == "data") {
      this._set_datatables()
    }
    this.manager.engine._hide_all_views()
    this.manager.engine.views[`query_${this.kind}`].classList.remove("hidden")
  }

  _set_summary () {
    if (this.charts.summary) {
      this.charts.summary.destroy()
    }
    document.querySelector("#query-result-summary .content").innerHTML = ""
    document.querySelector("#result-summary-chart-labels").innerHTML = ""
    document.querySelector("#result-summary-chart").classList.add("hidden")
    document.querySelector(
      "#query-result .responses-total .total-value"
    ).textContent = this.data.total_responses
    let summary_answer = this._get_first_select_result()
    if (summary_answer) {
      let answer_labels = summary_answer.options.map((x)=> x.option_name)
      let answer_values = summary_answer.options.map((x)=> x.total)
      let options = {indexAxis: "x"}
      let chart = get_chart({
        id: "result-summary-chart",
        type: "bar",
        labels: answer_labels,
        values: answer_values,
        options
      })
      document.querySelector("#result-summary-chart").classList.remove("hidden")
      this.charts.summary = chart
    }
  }

  _get_first_select_result () {
    let result = null
    for (let answer_result of this.data.answer_results) {
      if (["SELECT", "SELECT_IMAGE"].includes(answer_result.question.kind)) {
        result = answer_result
        break
      }
    }
    return result
  }

  _set_questions() {
    document.querySelector("#query-result-questions .content").innerHTML = ""
    let questions_container = document.querySelector("#query-result-questions")
    let content = questions_container.querySelector(".content")
    for (let chart of this.charts.questions) {
      chart.destroy()
    }
    this.charts.questions = []
    for (let answer_result of this.data.answer_results) {
      let template = questions_container.querySelector("#result-question-template").cloneNode(true)
      template.removeAttribute("id")
      let index = answer_result.question.index
      template.querySelector(".question-number .value").textContent = index + 1
      template.querySelector(".question-name").textContent = answer_result.question.name
      template.querySelector(".responses-total .total-value").textContent = answer_result.total
      content.appendChild(template)
      if (["SELECT", "SELECT_IMAGE"].includes(answer_result.question.kind)) {
        let id = `result-question-chart-${index}`
        let canvas = template.querySelector(".question-chart")
        canvas.setAttribute("id", id)
        let labels = template.querySelector(".chart-labels")
        labels.setAttribute("id", `${id}-labels`)
        let answer_labels = answer_result.options.map((x)=> x.option_name)
        let answer_values = answer_result.options.map((x)=> x.total)
        let chart = get_chart({
          id,
          type: "bar",
          labels: answer_labels,
          values: answer_values,
          options: {indexAxis: "y"},
        })
        this.charts.questions.push(chart)
        canvas.classList.remove("hidden")
        labels.classList.remove("hidden")
      }
      template.classList.remove("hidden")
    }

  }

  _set_map () {
    let map = this._get_map()
    let question_by_uuid = {}
    for (let question of this.data.query.questions) {
      question_by_uuid[question.uuid] = question
    }
    let shapes = new Set()
    this.marker_focus = null
    for (let point_data of this.data.point_list) {
      if (point_data.location && point_data.question_index !== null) {
        shapes.add(point_data.question_index)
        this._set_marker(map, question_by_uuid, point_data)
      }
    }
    if (this.marker_focus) {
      let marker = this.marker_focus
      setTimeout(function () {
        marker.openPopup();
      }, 100);
    }
    this._set_map_shapes(Array.from(shapes))
    this._set_fetch_meta()
  }

  _get_map () {
    if (this.map) {
      this.map.remove()
    }
    document.querySelector("#query-result-map").innerHTML = ""
    let latlng = L.latLng(-33.447869, -70.668423)
    let map = L.map("query-result-map").setView(latlng, 9)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
    }).addTo(map);
    map.attributionControl.setPrefix("")
    map.zoomControl.setPosition("bottomright")
    setTimeout(function () {
      window.dispatchEvent(new Event('resize'));
    }, 100);
    this.map = map
    return map
  }

  _set_map_shapes (shapes) {
    let shape_bottom = document.querySelector("#map-shapes-control .map-shapes-button")
    shape_bottom.active = false
    shape_bottom.addEventListener("click", this._click_map_shapes_button)
    let shape_list = document.querySelector("#map-shapes-control-list")
    shape_list.innerHTML = ""
    let counter = 0
    for (let shape of shapes) {
      let shape_element = document.createElement("div")
      shape_element.classList.add("map-shape-element")
      let icon_counter = counter < 3 ? counter: 0
      shape_element.innerHTML = `
        <div class="marker-preview-icon" counter="${icon_counter}"></div>
        <div class="map-shape-label">Pregunta ${counter + 1}</div>
        <div class="map-shape-icon icon switch-on"></div>
      `
      shape_list.appendChild(shape_element)
      shape_element.question_index = shape
      shape_element.active = true
      shape_element.querySelector(".icon").addEventListener("click", this._click_map_shape_action)
      counter += 1
    }
  }

  _click_map_shapes_button(event) {
    let shape_list = document.querySelector("#map-shapes-control-list")
    let shape_bottom = document.querySelector("#map-shapes-control .map-shapes-button")
    let bottom_icon = shape_bottom.querySelector(".icon")
    if (shape_bottom.active) {
      shape_bottom.active = false
      shape_list.classList.add("hidden")
      bottom_icon.classList.remove("back")
      bottom_icon.classList.add("right")
    } else {
      shape_bottom.active = true
      shape_list.classList.remove("hidden")
      bottom_icon.classList.remove("right")
      bottom_icon.classList.add("back")
    }
  }

  _click_map_shape_action (event) {
    let shape_element = event.target.closest(".map-shape-element")
    let action_icon = shape_element.querySelector(".map-shape-icon")
    if (shape_element.active) {
      shape_element.active = false
      action_icon.classList.remove("switch-on")
      action_icon.classList.add("switch-off")
      this._set_map_shape_visibility(shape_element.question_index, false)
    } else {
      shape_element.active = true
      action_icon.classList.remove("switch-off")
      action_icon.classList.add("switch-on")
      this._set_map_shape_visibility(shape_element.question_index, true)
    }
  }

  _set_map_shape_visibility(question_index, show) {
    if (this.map_markers[question_index]) {
      for (let marker of this.map_markers[question_index]) {
        if (show) {
          marker.setOpacity(1)
        } else {
          marker.setOpacity(0)
        }
      }
    }
  }

  _set_marker(map, question_by_uuid, point_data) {
    let icon = this._get_marker_icon(point_data, question_by_uuid)
    let marker = L.marker(
      [point_data.location.latitude, point_data.location.longitude], {
        icon: icon,
      }
    ).addTo(map)
    let message = "<div class='marker-content'>"
    message += this._set_html_message("Fecha de envío", new Date(point_data.response.send_at).toLocaleString())
    if (point_data.response.email) {
      message += this._set_html_message("Email", point_data.response.email)
    }
    if (point_data.response.rut) {
      message += this._set_html_message("Rut", point_data.response.rut)
    }
    message += this._get_answers_message(point_data, question_by_uuid)
    message += '</div>'
    marker.bindPopup(message)
    let current_markers = this.map_markers[point_data.question_index] ? this.map_markers[point_data.question_index]: []
    this.map_markers[point_data.question_index] = [...current_markers, marker]
    let param = new URLSearchParams(window.location.search).get("r")
    if (param && param == point_data.response.uuid) {
      this.marker_focus = marker
    }
  }

  _get_marker_icon(point_data, question_by_uuid) {
    let counter = 0
    for (let question_uuid in question_by_uuid) {
      let question = question_by_uuid[question_uuid]
      if (point_data.question_index === question.index) {
        break
      }
      if (question.kind === "POINT") {
        counter += 1
      }
      if (counter > 2) {
        break
      }
    }
    let icon_counter = counter < 3 ? counter: 0
    let icon_url = `/static/images/icons/marker-${icon_counter}.svg`
    let icon = L.icon({
      iconUrl: icon_url, iconSize: [20, 30],
    })
    return icon
  }

  _set_html_message(field, value, class_list) {
    return `<div class="item ${class_list? class_list: ""}"><div class="field">${field}: </div><div class="value">${value}</div></div>`
  }

  _get_answers_message (point_data, question_by_uuid) {
    let message = "<div class='responses-title'>Respuestas</div><div class='responses-list'>"
    for (let answer of point_data.response.answers) {
      let question = question_by_uuid[answer.question_uuid]
      message += this._set_html_message(`Pregunta ${question.index + 1}`, question.name)
      if (question.kind == "TEXT") {
        message += this._set_html_message("- Texto", answer.text)
      }
      if (question.kind == "IMAGE") {
        message += this._set_html_message("- Imagen", `<img class="image" src="${answer.image}">`)
      }
      if (["SELECT", "SELECT_IMAGE"].includes(question.kind)) {
        let options = "<div class='options-list'>"
        for (let option of answer.options) {
          options += `<div class="option">${option.name}</div>`
        }
        options += "</div>"
        message += this._set_html_message("- Opciones", options, "response")
      }
    }
    message += "</div>"
    return message
  }

  _set_fetch_meta () {
    if (this.data.response_range) {
      let start = new Date(this.data.response_range[0]).toLocaleString()
      let end = new Date(this.data.response_range[1]).toLocaleString()
      let range_responses = `${this.data.point_list.length} respuestas del ${start} al ${end}`
      document.querySelector("#query-map .range-responses").textContent = range_responses
    }
    document.querySelector("#query-map .fetch-at").textContent = `Consultado en ${new Date(this.data.fetch_at).toLocaleString()}`
  }

  _set_datatables () {
    if (this.data_table) {
      this.data_table.destroy()
    }
    let dataset = []
    for (let item of this.data.dataset) {
      let row = this._get_row_from_item(item)
      dataset.push(row)
    }
    let config = {...this.data.simpletables_config}
    config.rowRender = this._set_row_callback
    config.data.data = dataset
    config.data.headings = this._get_datables_heading(config)
    this.data_table = new simpleDatatables.DataTable("#query-result-data-table", config)
    this._set_cell_options()
    this._set_single_image_download()

  }
  _set_cell_options () {
    for (let button of document.querySelectorAll(".cell-options-button")) {
      button.addEventListener("click", function () {
        let content = this.nextElementSibling
        if (content.classList.contains("hidden")) {
          content.classList.remove("hidden")
        } else {
          content.classList.add("hidden")
        }
      })
    }
    for (let button of document.querySelectorAll(".dropdown-item.visiblity")) {
      button.addEventListener("click", this._click_response_visibility, false)
    }
  }

  _set_single_image_download() {
    let images = document.querySelectorAll(".query-datable-image")
    if (images.length > 0) {
      for (let image of images) {
        image.addEventListener("click", function () {
          let original_url = this.getAttribute("original")
          let send_at = this.getAttribute("send_at").slice(0, 19).replace(" ", ".")
          let filename = `${send_at}.png`
          new Promise((resolve, reject) => {
            let image_blob = fetch(original_url).then(response => response.blob());
            resolve(image_blob)
          }).then(blob => saveAs(blob, filename))
        })
      }
    }
  }

  _click_response_visibility (event) {
    this.manager.engine._set_loading()
    let response_uuid = event.target.getAttribute("response")
    let current_visibility = event.target.getAttribute("visible")
    if (response_uuid == null) {
      let dropdown_item = event.target.closest(".dropdown-item.visiblity")
      response_uuid = dropdown_item.getAttribute("response")
      current_visibility = dropdown_item.getAttribute("visible")
    }
    current_visibility = current_visibility === "true"
    let data = {
      response_uuid, visible: !current_visibility
    }
    fetch (`${this.manager.url_base}update_response_visibility/`, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {"Content-Type": "application/json", "X-CSRFToken": this.manager.engine.csrf_token},
      credentials: "same-origin"
    })
    .then((response)=>{
      this.show_view()
    })
  }

  _set_row_callback (rowValue, tr, index) {
    tr.attributes.class = "row-response"
  }

  _get_row_from_item(item) {
    let row = []
    for (let i = 0; i < this.data.fields.length; i++) {
      let field = this.data.fields[i]
      let value = item[field]
      if (field == "send_at") {
        let sat = new Date(value)
        let month = sat.getMonth() + 1
        month = month < 10 ? `0${month}`: month
        let day = sat.getDate() < 10 ? `0${sat.getDate()}`: sat.getDate()
        value = `${sat.getFullYear()}-${month}-${day} `
        value += `${sat.getHours()}:${sat.getMinutes()}:${sat.getSeconds()}`
      }
      if (field == "location" && value) {
        let lat = `<div class="latitude"><span class="label">Latitud: </span><span class="value">${value.latitude}</span></div>`
        let long = `<div class="latitude"><span class="label">Longitud: </span><span class="value">${value.longitude}</span></div>`
        value = `${lat}${long}`
      }
      if (field.includes("pregunta_")) {
        value = this._get_question_value(this.data.query.questions, field, value, item)
      }
      if (value == null) {
        value = ""
      }
      if (field == "visible") {
        let visible = value === "True"
        let label = visible ? "Ocultar respuestas": "Mostrar respuestas"
        value = `
          <div class="dropdown-wrapper">
            <div class="cell-options-button icon options"></div>
            <div class="dropdown-content cell-options-content hidden dd-content">
              <div class="dropdown-item visiblity" response="${item.uuid}" visible="${visible}">
                <div class="icon ${visible? 'hide': 'show'}"></div>
                <div class="dropdown-item-value">${label}</div>
              </div>
            </div>
          </div>
        `
      }
      row.push(value)
    }
    if (item.visible === "False") {
      row[1] = `
        <div class="response-hidden-alert">
          <div class="icon hide"></div>
          <div class="response-hidden-alert-message">
            <div class="response-hidden-title">
              Respuestas en modo oculto
            </div>
            <div class="response-hidden-subtitle">
              Las respuesta de esta persona no serán consideradas en los resultados de esta consulta.
            </div>
          </div>
        </div>
        <div class="response-hidden-alert-spacer"></div>
      `
    }
    return row
  }

  _get_datables_heading(config) {
    let headings = []
    for (let header of config.data.headings) {
      let description = header.desc ? `<div class="dt-field-desc">${header.desc}</div>`: ""
      let heading = `<div class="dt-field"><div class="dt-field-label">${header.label}</div>${description}</div>`
      headings.push(heading)
    }
    return headings
  }

  _get_question_value(questions, field, value, item) {
    let num = parseInt(field.match(/\d+/)[0])
    let index = num - 1
    let question = questions[index]
    let final_value = value

    if (question.kind == "IMAGE" && value) {
      final_value = `<div class="query-datable-image" style="background-image: url('${value.thumb}')" send_at="${item.send_at}" original="${value.original}"></div>`
    } else if (question.kind == "POINT" && value) {
      let query_url_code = this.data.query.url_code
      let link = item.visible === "True"? `href="?f=query-map&k=${query_url_code}&r=${item.uuid}"`: ""
      final_value = `
        <div class="query-result-to-map">
          <a class="query-result-to-map-link" ${link}>
            <div class="icon map-marker"></div>
            <div class="to-map-link-label">Ver en el mapa</div>
          </a>
        </div>
      `
    } else if (["SELECT", "SELECT_IMAGE"].includes(question.kind) && value) {
      final_value = "<ul>"
      for (let opt of value) {
        final_value += `<li>${opt}</li>`
      }
      final_value += "</ul>"
    }
    return final_value
  }

}

export {QueryResultManager}
