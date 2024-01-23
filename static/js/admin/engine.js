import {
  get_chart
} from "./charts.js"


class AdminEngine {
  constructor (
    { url_base = "" }
  ) {
    this.url_base = url_base
    this.query_detail_uuid = null
    this.storage = {}
    this._set_admin_sidebar()
    this._set_views()
    this.show_view("query-list")
    this.charts = {
      summary: null
    }
  }

  _set_admin_sidebar() {

  }

  _set_views () {
    let loading = document.querySelector("#loading")
    let query_list = document.querySelector("#query-list")
    let query_detail = document.querySelector("#query-detail")
    let query_create = document.querySelector("#query-create")
    this.views = {
      loading, query_list, query_detail, query_create
    }
    this.click_query_list = this.click_query_list.bind(this)
    this.click_query_detail = this.click_query_detail.bind(this)
    query_detail.querySelector("#link-to-query-list").addEventListener(
      "click", this.click_query_list, false
    )

    this.click_detail_summary = this.click_detail_summary.bind(this)
    this.click_detail_questions = this.click_detail_questions.bind(this)
    query_detail.querySelector("#summary-link").addEventListener(
      "click", this.click_detail_summary, false
    )
    query_detail.querySelector("#questions-link").addEventListener(
      "click", this.click_detail_questions, false
    )
  }

  _hide_all_views () {
    this.views.loading.classList.add("hidden")
    this.views.query_list.classList.add("hidden")
    this.views.query_detail.classList.add("hidden")
    this.views.query_create.classList.add("hidden")
  }

  _set_loading () {
    this._hide_all_views()
    this.views.loading.classList.remove("hidden")
  }

  show_view(name) {
    this._set_loading()
    if (name == "query-list") {
      this._show_query_list_view()
    }
    if (name == "query-detail") {
      this._show_query_detail_view()
    }
  }

  _show_query_list_view() {
    fetch (this.url_base, {
      method: "GET",
      headers: {"Content-Type": "application/json"},
      credentials: "same-origin"
    })
    .then(response=> {
      if (response.ok) {
        response.json()
        .then((data)=> {
          this.storage.query_list = data.list
          this._set_query_list_in_view()
        })
      } else {
        console.log(response)
      }
    })
  }

  _show_query_detail_view() {
    fetch (`${this.url_base}${this.query_detail_uuid}`, {
      method: "GET",
      headers: {"Content-Type": "application/json"},
      credentials: "same-origin"
    })
    .then(response=> {
      if (response.ok) {
        response.json()
        .then((data)=> {
          this.storage.query_detail = data
          this._set_query_detail_in_view()
        })
      } else {
        console.log(response)
      }
    })
  }

  _set_query_list_in_view() {
    let template = document.querySelector("#query-item-template").cloneNode(true)
    template.classList.remove("hidden")
    let query_list = this.views.query_list.querySelector(".query-item-list")
    query_list.innerHTML = ""
    for (let item of this.storage.query_list) {
      let query_item = template.cloneNode(true)
      let returned_query_item = this._create_query_item(item, query_item)
      let action_button = returned_query_item.querySelector(".action-button")
      action_button.query_uuid = item.uuid
      action_button.addEventListener(
        "click", this.click_query_detail, false
      )
      query_list.appendChild(returned_query_item)
    }
    this._hide_all_views()
    this.views.query_list.classList.remove("hidden")
  }

  _set_query_detail_in_view () {
    let query_item = document.querySelector("#query-detail-item")
    let returned_query_item = this._create_query_item(this.storage.query_detail.query, query_item)
    this._clean_query_detail()
    this._set_detail_summary()
    this._set_detail_questions()
    this._hide_all_views()
    this.views.query_detail.classList.remove("hidden")
  }

  _set_detail_summary () {
    document.querySelector(
      "#query-detail .responses-total .total-value"
    ).textContent = this.storage.query_detail.total_responses
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
    }

  }

  _set_detail_questions() {
    let questions_container = document.querySelector("#query-detail-questions")
    let content = questions_container.querySelector(".content")
    for (let answer_result of this.storage.query_detail.answer_results) {
      let template = questions_container.querySelector("#question-template").cloneNode(true)
      template.removeAttribute("id")
      let index = answer_result.question.index
      template.querySelector(".question-number .value").textContent = index
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
        this.charts.summary = chart
        canvas.classList.remove("hidden")
        labels.classList.remove("hidden")
      }
      template.classList.remove("hidden")
    }

  }

  _get_first_select_result () {
    let result = null
    for (let answer_result of this.storage.query_detail.answer_results) {
      if (answer_result.question.kind == "SELECT") {
        result = answer_result
        break
      }
    }
    return result
  }

  _create_query_item(item, query_item) {
    query_item.querySelector(".name").textContent = item.name
    if (!item.start_at && !item.end_at) {
      query_item.querySelector(".times").classList.add("hidden")
    } else {
      query_item.querySelector(".times").classList.remove("hidden")
      if (item.start_at) {
        let start_at = new Date(item.start_at).toLocaleString().split(",")[0]
        query_item.querySelector(".start-at").textContent = `Desde: ${start_at}`
      }
      if (item.end_at) {
        let end_at = new Date(item.end_at).toLocaleString().split(",")[0]
        query_item.querySelector(".end-at").textContent = `Hasta: ${end_at}`
      }
    }
    let status_value = query_item.querySelector(".status > .status-value")
    status_value.classList.remove("draft", "finished", "active")
    if (!item.active) {
      status_value.textContent = "Borrador"
      status_value.classList.add("draft")
    } else if (item.active && !item.is_active) {
      status_value.textContent = "Finalizada"
      status_value.classList.add("finished")
    } else if (item.active && item.is_active) {
      status_value.textContent = "Activa"
      status_value.classList.add("active")
    }
    return query_item
  }

  _clean_query_detail () {
    let view = document.querySelector("#query-detail")
    view.querySelector(".responses-total .total-value").textContent = ""
    view.querySelector("#query-detail-summary .content").innerHTML = ""
    view.querySelector("#query-detail-questions .content").innerHTML = ""
    document.querySelector("#summary-chart").classList.add("hidden")
    if (this.charts.summary) {
      this.charts.summary.destroy()
    }
  }

  click_query_detail (event) {
    this.query_detail_uuid = event.currentTarget.query_uuid
    this.show_view("query-detail")
  }

  click_query_list (event) {
    this.show_view("query-list")
  }

  click_detail_summary (event) {
    document.querySelector("#query-detail #query-detail-summary").classList.remove("hidden")
    document.querySelector("#query-detail #query-detail-questions").classList.add("hidden")
    document.querySelector("#query-detail #summary-link").classList.add("active")
    document.querySelector("#query-detail #questions-link").classList.remove("active")
  }

  click_detail_questions (event) {
    document.querySelector("#query-detail #query-detail-summary").classList.add("hidden")
    document.querySelector("#query-detail #query-detail-questions").classList.remove("hidden")
    document.querySelector("#query-detail #summary-link").classList.remove("active")
    document.querySelector("#query-detail #questions-link").classList.add("active")
  }

}

export {AdminEngine}
