import {
  get_chart
} from "../charts.js"


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
    document.querySelector("#detail-action-map").setAttribute("href", this.data.links.map)
    document.querySelector("#detail-action-data").setAttribute("href", this.data.links.data)
    let edit_button = document.querySelector("#detail-action-edit")
    edit_button.addEventListener("click", this._click_query_edit, false)
    this._clean()
    this._set_summary()
    this._set_questions()
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_detail.classList.remove("hidden")
  }

  _click_query_edit (event) {
    this.manager.engine.show_view("query-update", true)
  }

  _set_summary () {
    document.querySelector(
      "#query-detail .responses-total .total-value"
    ).textContent = this.data.total_responses
    let summary_answer = this._get_first_select_result()
    if (summary_answer) {
      document.querySelector("#summary-chart").classList.remove("hidden")
      let answer_labels = summary_answer.options.map((x)=> x.option_name)
      let answer_values = summary_answer.options.map((x)=> x.total)
      let options = {indexAxis: "x"}
      let chart = get_chart({
        id: "summary-chart",
        type: "bar",
        labels: answer_labels,
        values: answer_values,
        options
      })
      this.charts.summary = chart
    }

  }

  _set_questions() {
    let questions_container = document.querySelector("#query-detail-questions")
    let content = questions_container.querySelector(".content")
    for (let answer_result of this.data.answer_results) {
      let template = questions_container.querySelector("#question-template").cloneNode(true)
      template.removeAttribute("id")
      let index = answer_result.question.index
      template.querySelector(".question-number .value").textContent = index + 1
      template.querySelector(".question-name").textContent = answer_result.question.name
      template.querySelector(".responses-total .total-value").textContent = answer_result.total
      content.appendChild(template)
      if (answer_result.question.kind == "SELECT") {
        let id = `question-chart-${index}`
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
        canvas.classList.remove("hidden")
        labels.classList.remove("hidden")
      }
      template.classList.remove("hidden")
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

  _clean () {
    let view = document.querySelector("#query-detail")
    view.querySelector(".responses-total .total-value").textContent = ""
    view.querySelector("#query-detail-summary .content").innerHTML = ""
    view.querySelector("#query-detail-questions .content").innerHTML = ""
    document.querySelector("#summary-chart").classList.add("hidden")
    if (this.charts.summary) {
      this.charts.summary.destroy()
    }
  }



}

export {QueryDetailManager}
