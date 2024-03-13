import {
  get_chart
} from "../charts.js"


class QueryResultManager {
  constructor ({manager = null, kind = null}) {
    this.manager = manager
    this.data = {}
    this.kind = kind
    this.charts = {summary: null, questions: []}
    this._set_pre_in_view()
    this.map = null
    this.data_table = null
  }

  _set_pre_in_view () {
    let tab_links = document.querySelector(`.view.query-${this.kind} .result.tab-links`)
    let click_got_to = this.manager._click_go_to_view.bind(this.manager)
    for (let tab_link of tab_links.children) {
      tab_link.addEventListener("click", click_got_to, false)
    }
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
      if (answer_result.question.kind == "SELECT") {
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
      if (answer_result.question.kind == "SELECT") {
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
    for (let point_data of this.data.point_list) {
      if (point_data.location) {
        this._set_marker(map, question_by_uuid, point_data)
      }
    }

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
    setTimeout(function () {
      window.dispatchEvent(new Event('resize'));
    }, 100);
    this.map = map
    return map
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
          value = this._get_question_value(this.data.query.questions, field, value, item.uuid)
        }
        if (value == null) {
          value = ""
        }
        row.push(value)
      }
      dataset.push(row)
    }
    let config = {...this.data.simpletables_config}
    config.data.data = dataset
    this.data_table = new simpleDatatables.DataTable("#query-result-data-table", config)
  }

  _get_question_value(questions, field, value, response_uuid) {
    let num = parseInt(field.match(/\d+/)[0])
    let index = num - 1
    let question = questions[index]
    let tooltip_content = `<div class="tooltip-title"><b>Pregunta ${num}: </b>${question.name}</div>`
    let final_value = value

    if (question.kind == "IMAGE" && value) {
      final_value = `<img class="tooltip-image" src="${value}">`
      tooltip_content += `<a href="${value}" target="_blank">${final_value}</a>`
    } else if (question.kind == "POINT" && value) {
      let lat = `<div class="latitude"><span class="label">Latitud: </span><span class="value">${value.latitude}</span></div>`
      let long = `<div class="latitude"><span class="label">Longitud: </span><span class="value">${value.longitude}</span></div>`
      final_value = `${lat}${long}`
      tooltip_content += `<div class="link-tabs"><a class="link-tab" href="${this.map_url}?f=${response_uuid}">Ver en mapa</a></div>`
    } else if (question.kind == "SELECT" && value) {
      final_value = "<ul>"
      for (let opt of value) {
        final_value += `<li>${opt}</li>`
      }
      final_value += "</ul>"
    }
    return `${final_value}<div class="tooltip">${tooltip_content}</div>`
  }

}

export {QueryResultManager}
