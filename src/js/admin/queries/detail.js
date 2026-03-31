class QueryDetailManager {
  constructor ({manager = null}) {
    this.manager = manager
    this.data = {}
    this.charts = {
      summary: null
    }
    this.map_pointers = []
    this._click_query_edit = this._click_query_edit.bind(this)
  }

  show_view(on_history) {
    fetch (`${this.manager.url_base}${this.manager.engine.cursor.key}`, {
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
            this.manager.engine._set_url_params("query-detail", data.query.url_code)
          }
        })
      } else {
        console.log(response)
        this.manager.engine.show_view("query-list", false)
      }
    })
  }

  _set_in_view () {
    let query_item = document.querySelector("#query-detail-item")
    let returned_query_item = this.manager._create_query_item(this.data.query, query_item)
    if (this.data.query.is_active || this.data.query.is_earring) {
      document.querySelector("#detail-action-submit").setAttribute("href", this.data.links.submit)
      document.querySelector("#detail-action-submit").classList.remove("hidden")
    } else {
      document.querySelector("#detail-action-submit").classList.add("hidden")
    }
    this._set_query_preview()
    this.manager._build_sidebar()
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_detail.classList.remove("hidden")
  }

  _click_query_edit (event) {
    this.manager.engine.show_view("query-update", true)
  }

  _set_query_preview () {
    let description_element = document.querySelector("#query-detail .query-preview-description")
    if (this.data.query.description) {
      description_element.textContent = this.data.query.description
    } else {
      description_element.textContent = "*Sin descripción configurada"
    }
    let questions = document.querySelector("#query-detail .query-preview-questions")
    questions.innerHTML = ""
    for (let i in this.map_pointers) {
      this.map_pointers[i].remove()
    }
    this.map_pointers = []
    let index = 0
    for (let answer_result of this.data.answer_results) {
      let question = answer_result.question
      let question_container = document.createElement("div")
      question_container.classList.add("question-container")
      question_container.innerHTML = `
        <div class="subtitle">Pregunta ${index + 1}</div>
        <div class="question-item-kind">${this.manager.get_kind_label(question)}</div>
        <div class="question-name">${question.name}</div>
        <div class="question-description">${question.description? question.description: ""}</div>
      `
      if (question.image) {
        question_container.innerHTML += `<div class="question-item-image-preview-content"><img class="question-item-image-preview" src="${question.image}"></div>`
      }
      // here
      if (["SELECT", "SELECT_IMAGE"].includes(question.kind)) {
        question_container.innerHTML += `<div class="question-options"></div>`
        let options_container = question_container.querySelector(".question-options")
        let option_index = 0
        for (let option of question.options) {
          let inner_html = ""
          if (question.kind === "SELECT") {
            inner_html = `
              <div class="option">
                <span class="option-label">${this.manager.letters[option_index]}.</span>
                <span class="option-value">${option.name}</span>
              </div>
            `
          } else {
            inner_html = `
              <div class="option-image">
                <div class="option-image-index">${option_index + 1}.</div>
                <div class="option-image-content">
                  <img class="option-image-img" src="${option.image}">
                  <div class="option-image-label">${option.name}</div>
                </div>
              </div>
            `
          }
          options_container.innerHTML += inner_html
          option_index += 1
        }
      } else {
        question_container.innerHTML += this.manager._get_question_kind_html(question)
      }
      questions.appendChild(question_container)
      if (question.kind === "POINT") {
        if (question.default_point == null) {
          question.default_point = {latitude: -33.447869, longitude: -70.668423}
        }
        let latitude = question.default_point.latitude? question.default_point.latitude: -33.447869
        let longitude = question.default_point.longitude? question.default_point.longitude: -70.668423
        let zoom = question.default_zoom? question.default_zoom: 9
        let latlng = L.latLng(latitude, longitude)
        let map = L.map(`map-pointer-${question.uuid}`).setView(latlng, zoom)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
          maxZoom: 19,
          zoomControl: false,
        }).addTo(map);
        map.attributionControl.setPrefix("")
        map.zoomControl.remove()
        map.dragging.disable()
        map.doubleClickZoom.disable()
        map.scrollWheelZoom.disable()
        setTimeout(function () {
          window.dispatchEvent(new Event('resize'));
        }, 100);
        this.map_pointers.push(map)
      }
      index += 1
    }
  }
}

export {QueryDetailManager}
