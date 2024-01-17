class QueryMapResultEngine {
  constructor ({resource_url = "", focus = null}) {
    this.ready = this.ready.bind(this)
    this.resource_url = resource_url
    this.focus = focus
    document.addEventListener("DOMContentLoaded", this.ready)
  }

  ready (event) {
    fetch(this.resource_url)
      .then(response => response.json())
      .then((data) =>{
        this.set_map(data)
        document.querySelector(".load").classList.add("hidden")
      });
  }

  set_map (data) {
    let latlng = L.latLng(-33.447869, -70.668423)
    let map = this._get_map()
    let question_by_uuid = this._get_question_by_uuid(data)

    for (let point_data of data.point_list) {
      if (point_data.location) {
        this._set_marker(map, question_by_uuid, point_data)
      }
    this._set_fetch_meta(data)
    }
  }

  _get_map () {
    let latlng = L.latLng(-33.447869, -70.668423)
    let map = L.map("map").setView(latlng, 9)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
    }).addTo(map);
    map.attributionControl.setPrefix("")
    return map
  }

  _get_question_by_uuid (data) {
    let question_by_uuid = {}
    for (let question of data.query.questions) {
      question_by_uuid[question.uuid] = question
    }
    return question_by_uuid
  }

  _set_marker(map, question_by_uuid, point_data) {
    let marker = L.marker(
      [point_data.location.latitude, point_data.location.longitude]
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
    if (this.focus == point_data.response.uuid) {
      marker.openPopup()
    }
  }

  _set_html_message(field, value, class_list) {
    return `<div class="item ${class_list? class_list: ""}"><div class="field">${field}: </div><div class="value">${value}</div></div>`
  }

  _get_answers_message (point_data, question_by_uuid) {
    let message = "<div class='responses-title'>Respuestas</div><div class='responses-list'>"
    for (let answer of point_data.response.answers) {
      let question = question_by_uuid[answer.question_uuid]
      console.log(question)
      message += this._set_html_message(`Pregunta ${question.index + 1}`, question.name)
      if (question.kind == "TEXT") {
        message += this._set_html_message("- Texto", answer.text)
      }
      if (question.kind == "IMAGE") {
        message += this._set_html_message("- Imagen", `<img class="image" src="${answer.image}">`)
      }
      if (question.kind == "SELECT") {
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

  _set_fetch_meta (data) {
    let start = new Date(data.response_range[0]).toLocaleString()
    let end = new Date(data.response_range[1]).toLocaleString()
    let range_responses = `${data.point_list.length} respuestas del ${start} al ${end}`
    document.querySelector(".range-responses").textContent = range_responses
    document.querySelector(".fetch-at").textContent = `Consultado en ${new Date(data.fetch_at).toLocaleString()}`
  }
}

export {QueryMapResultEngine}
