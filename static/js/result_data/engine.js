class QueryDataResultEngine {
  constructor ({resource_url = "", map_url = ""}) {
    this.ready = this.ready.bind(this)
    this.resource_url = resource_url
    this.map_url = map_url
    document.addEventListener("DOMContentLoaded", this.ready)
  }

  ready (event) {
    fetch(this.resource_url)
      .then(response => response.json())
      .then((data) =>{
        this.set_datatables(data)
        document.querySelector(".load").classList.add("hidden")
      });
  }

  set_datatables (data) {
    let dataset = []
    for (let item of data.dataset) {
      let row = []
      for (let i = 0; i < data.fields.length; i++) {
        let field = data.fields[i]
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
          value = this._get_question_value(data.query.questions, field, value, item.uuid)
        }
        if (value == null) {
          value = ""
        }
        row.push(value)
      }
      dataset.push(row)
    }
    let config = {...data.simpletables_config}
    config.data.data = dataset
    this.data_table = new simpleDatatables.DataTable("#data-table", config)
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

export {QueryDataResultEngine}
