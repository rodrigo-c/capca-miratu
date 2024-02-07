import {
  QueryManager
} from "./queries/manager.js"



class AdminEngine {
  constructor (
    { url_base = "" , csrf_token = "", focus = null, key = null}
  ) {
    this.csrf_token = csrf_token
    this.cursor = {focus: focus?focus:"query-list", key}
    this.query_manager = new QueryManager({engine: this, url_base})

    this._onpopstate = this._onpopstate.bind(this)
    window.addEventListener("popstate", this._onpopstate, false)
    this._set_admin_sidebar()
    this._set_views()
    this.show_view(this.cursor.focus, true)
  }

  _onpopstate (event) {
    let query_params = new URLSearchParams(window.location.search)
    this.cursor = event.state
    this.show_view(this.cursor.focus, false)
  }

  _set_admin_sidebar() {
    this.click_query_create = this.click_query_create.bind(this)
    let create_button = document.querySelector("#query-create-link")
    create_button.addEventListener("click", this.click_query_create, false)
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
    query_create.querySelector("#link-to-query-list").addEventListener(
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

  show_view(name, on_history) {
    this._set_loading()
    if (name == "query-list") {
      this.query_manager.list.show_view(on_history)
    }
    if (name == "query-detail") {
      this.query_manager.detail.show_view(on_history)
    }
    if (name == "query-create") {
      this.query_manager.create.show_view(on_history)
    }
    else {
      this.query_manager.list.show_view(on_history)
    }
  }

  _set_url_params(focus, key) {
    let query_params = new URLSearchParams(window.location.search)
    query_params.set("f", focus)
    this.cursor.focus = focus
    if (key) {
      query_params.set("k", key)
      this.cursor.key = key
    } else {
      query_params.delete("k")
      this.cursor.key = null
    }
    history.pushState(this.cursor, null, "?" + query_params.toString())
  }

  click_query_detail (event) {
    this.cursor.key = event.currentTarget.query_uuid
    this.show_view("query-detail", true)
  }

  click_query_list (event) {
    this.show_view("query-list", true)
  }

  click_query_create (event) {
    this.show_view("query-create", true)
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
