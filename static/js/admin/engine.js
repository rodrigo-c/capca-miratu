import {
  QueryManager
} from "./queries/manager.js"



class AdminEngine {
  constructor (
    { url_base = "" , csrf_token = "", focus = null, key = null}
  ) {
    this.csrf_token = csrf_token
    this.cursor = {focus: focus?focus:"query-list", key}
    this.url_base = url_base
    this.ready = this.ready.bind(this)
    this._onpopstate = this._onpopstate.bind(this)
    document.addEventListener("DOMContentLoaded", this.ready)
  }

  ready() {
    this.query_manager = new QueryManager({engine: this, url_base: this.url_base})
    window.addEventListener("popstate", this._onpopstate, false)
    this._set_admin_menu()
    this._set_views()
    this.show_view(this.cursor.focus, true)
  }

  _onpopstate (event) {
    let query_params = new URLSearchParams(window.location.search)
    this.cursor = event.state
    this.show_view(this.cursor.focus, false)
  }

  _click_menu_item(event) {
    let focus = event.target.focus
    this.show_view(focus, true)
    event.target.closest(".menu-content").classList.add("hidden")
  }

  _set_admin_menu() {
    this._click_menu_item = this._click_menu_item.bind(this)
    let menu_button = document.querySelector("#navbar .menu-dropdown .menu-button")
    let menu_content = document.querySelector("#navbar .menu-dropdown .menu-content")
    menu_button.addEventListener("click", (event) => {
      if (menu_content.classList.contains("hidden")) {
        menu_content.classList.remove("hidden")
      } else {
        menu_content.classList.add("hidden")
      }
    })
    this._set_admin_menu_item("query-create-link", "query-create", menu_content)
    this._set_admin_menu_item("query-list-link", "query-list", menu_content)
  }

  _set_admin_menu_item(id, focus, menu_content) {
    let menu_item = menu_content.querySelector(`#${id}`)
    menu_item.focus = focus
    for (let child of menu_item.children) {
      child.focus = focus
    }
    menu_item.addEventListener("click", this._click_menu_item, false)
  }

  _set_views () {
    let loading = document.querySelector("#loading")
    let query_list = document.querySelector("#query-list")
    let query_detail = document.querySelector("#query-detail")
    let query_create = document.querySelector("#query-create")
    let query_update = document.querySelector("#query-update")
    let query_map = document.querySelector("#query-map")
    let query_data = document.querySelector("#query-data")
    this.views = {
      loading, query_list,
      query_detail,
      query_create,
      query_update,
      query_map,
      query_data,
    }
    this.click_query_list = this.click_query_list.bind(this)
    this.click_query_detail = this.click_query_detail.bind(this)
    for (let view of [query_detail, query_create, query_update]) {
      view.querySelector("#link-to-query-list").addEventListener(
        "click", this.click_query_list, false
      )
    }
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
    this.views.query_update.classList.add("hidden")
    this.views.query_map.classList.add("hidden")
    this.views.query_data.classList.add("hidden")
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
    else if (name == "query-detail") {
      this.query_manager.detail.show_view(on_history)
    }
    else if (name == "query-create") {
      this.query_manager.create.show_view(on_history)
    }
    else if (name == "query-update") {
      this.query_manager.update.show_view(on_history)
    }
    else if (name == "query-map") {
      this.query_manager.map.show_view(on_history)
    }
    else if (name == "query-data") {
      this.query_manager.data.show_view(on_history)
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
