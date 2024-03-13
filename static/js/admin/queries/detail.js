class QueryDetailManager {
  constructor ({manager = null}) {
    this.manager = manager
    this.data = {}
    this.charts = {
      summary: null
    }
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
    document.querySelector("#detail-action-submit").setAttribute("href", this.data.links.submit)
    this._set_query_preview()
    this.manager._build_sidebar()
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_detail.classList.remove("hidden")
  }

  _click_query_edit (event) {
    this.manager.engine.show_view("query-update", true)
  }

  _set_query_preview () {
    document.querySelector("#query-detail .query-preview-description").textContent = this.data.query.description
    let questions = document.querySelector("#query-detail .query-preview-questions")
    questions.innerHTML = ""
    let index = 0
    for (let answer_result of this.data.answer_results) {
      let question = answer_result.question
      let question_container = document.createElement("div")
      question_container.classList.add("question-container")
      question_container.innerHTML = `
        <div class="subtitle">Pregunta ${index + 1}</div>
        <div class="question-name">${question.name}</div>
        <div class="question-description">${question.description}</div>
      `
      if (question.kind == "POINT") {
        question_container.innerHTML += "<div class='question-map map-bg'></div>"
      } else if (question.kind == "SELECT") {
        question_container.innerHTML += `<div class="question-options"></div>`
        let options_container = question_container.querySelector(".question-options")
        let option_index = 0
        for (let option of question.options) {
          options_container.innerHTML += `
            <div class="option">
              <span class="option-label">${this.manager.letters[option_index]}.</span>
              <span class="option-value">${option.name}</span>
            </div>
          `
        }
        option_index += 1
      }
      questions.appendChild(question_container)
      index += 1
    }
  }
}

export {QueryDetailManager}
