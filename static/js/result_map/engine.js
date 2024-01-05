class QueryMapResultEngine {
  constructor ({resource_url = ""}) {
    this.ready = this.ready.bind(this)
    this.resource_url = resource_url
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
    let map = L.map("map").setView(latlng, 9)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
    }).addTo(map);
    map.attributionControl.setPrefix("")
    let question_by_uuid = this._get_question_by_uuid(data)

    for (let point_data of data.point_list) {
      if (point_data.location) {
        let marker = L.marker(
          [point_data.location.latitude, point_data.location.longitude]
        ).addTo(map)
        let message = this._set_html_message("Enviado en", new Date(point_data.response.send_at))
        if (point_data.response.email) {
          message += this._set_html_message("Email", point_data.response.email)
        }
        if (point_data.response.rut) {
          message += this._set_html_message("Rut", point_data.response.rut)
        }
        message += this._get_answers_message(point_data, question_by_uuid)
        marker.bindPopup(message)
      }

    }
    document.querySelector(".fetch-at").textContent = `Fecha de resultado: ${data.fetch_at}`
  }

  _get_question_by_uuid (data) {
    let question_by_uuid = {}
    for (let question of data.query.questions) {
      question_by_uuid[question.uuid] = question
    }
    return question_by_uuid
  }

  _set_html_message(field, value) {
    return `<div><b>${field}: </b>${value}</div>`
  }

  _get_answers_message (point_data, question_by_uuid) {
    let message = this._set_html_message("Respuestas", "")
    for (let answer of point_data.response.answers) {
      let question = question_by_uuid[answer.question_uuid]
      message += this._set_html_message("Pregunta", question.name)
      if (question.kind == "TEXT") {
        message += this._set_html_message("", answer.text)
      }
      if (question.kind == "IMAGE") {
        message += `<img src="${answer.image}" width="50%">`
      }
      if (question.kind == "SELECT") {
        let options = ""
        for (let option of answer.options) {
          message += this._set_html_message("Opción", option.name)
        }
      }
    }
    return message
  }
}

export {QueryMapResultEngine}
