import {
  QueryManager
} from "./queries/manager.js"



class AdminEngine {
  constructor (
    { url_base = "" , csrf_token = "", focus = null, key = null, user = null}
  ) {
    this.user = user
    this.csrf_token = csrf_token
    this.cursor = {focus: focus?focus:"query-list", key}
    this.url_base = url_base
    this.ready = this.ready.bind(this)
    this._onpopstate = this._onpopstate.bind(this)
    document.addEventListener("DOMContentLoaded", this.ready)
    this.view_names = [
      "loading",
      "query_list",
      "query_detail",
      "query_create",
      "query_update",
      "query_result",
      "query_questions",
      "query_map",
      "query_data",
      "query_share",
    ]
    this.views = {}
    this._general_click = this._general_click.bind(this)
    document.querySelector("body > .main-container").addEventListener("click", this._general_click, false)
  }

  ready() {
    this.query_manager = new QueryManager({engine: this, url_base: this.url_base})
    window.addEventListener("popstate", this._onpopstate, false)
    this._set_admin_menu()
    this._set_views()
    this._set_modal()
    this.show_view(this.cursor.focus, true)
  }

  _general_click (event) {
    let dropdown_class = "dropdown-wrapper"
    let current_wrapper = event.target.classList.contains(dropdown_class)? event.target : event.target.closest(`.${dropdown_class}`)
    for (let wrapper of document.querySelectorAll(`.${dropdown_class}`)) {
      if (wrapper !== current_wrapper) {
        wrapper.querySelector(".dd-content").classList.add("hidden")
      }
    }
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
    let menu_button = document.querySelector("#menu-button")
    let menu_content = document.querySelector("#menu-content")
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
    for (let name of this.view_names) {
      let view = document.querySelector(`#${name.replace("_", "-")}`)
      this.views[name] = view
    }
  }

  _set_modal() {
    this._click_out_modal_content = this._click_out_modal_content.bind(this)
    let modal = document.querySelector("#admin-modal")
    modal.addEventListener("click", this._click_out_modal_content, false)
  }

  _click_out_modal_content(event) {
    if (["admin-modal", "admin-modal-close"].includes(event.target.getAttribute("id"))) {
      this.hide_modal()
    }
  }

  _hide_all_views () {
    for (let name in this.views) {
      this.views[name].classList.add("hidden")
    }
  }

  _set_loading () {
    this._hide_all_views()
    this.views.loading.classList.remove("hidden")
  }

  show_view(name, on_history) {
    this._set_loading()
    this.cursor.focus = name
    let view_name = name.split("-")
    let view_kind = view_name[0]
    let view_selector = view_name[1]
    let manager = null
    if (view_kind == "query") {
      manager = this.query_manager[view_selector]
    }
    if (manager && manager.show_view) {
      manager.show_view(on_history)
    } else {
      this.cursor.focus = "query-list"
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
    if (focus !== "query-map") {
      query_params.delete("r")
    }
    history.pushState(this.cursor, null, "?" + query_params.toString())
  }

  show_modal(config) {
    let modal = document.querySelector("#admin-modal")
    modal.config = config
    let html_element = null
    if (config.html_element) {
      html_element = config.html_element
    }
    else {
      html_element = document.createElement("div")
      html_element.innerHTML = `
        <div class="modal-icon-${config.icon}"></div>
        <div class="modal-title">${config.title}</div>
        <div class="modal-content">${config.content}</div>
        <div class="modal-actions"></div>
      `
      let actions = html_element.querySelector(".modal-actions")
      for (let action of config.actions) {
        let button = document.createElement("div")
        button.classList.add("primary-button")
        button.innerText = action.name
        button.addEventListener("click", action.click, false)
        actions.appendChild(button)
      }
    }
    html_element.classList.add(config.class)
    modal.querySelector(".admin-modal-content").appendChild(html_element)
    modal.classList.remove("hidden")
  }

  hide_modal() {
    let modal = document.querySelector("#admin-modal")
    modal.classList.add("hidden")
    modal.querySelector(`.${modal.config.class}`).remove()
  }

  set_navbar_message(message, timeout) {
    let container = document.querySelector(".navbar .navbar-message-container")
    container.querySelector(".navbar-message-text").innerText = message
    if (timeout) {
      container.classList.remove("hidden")
      setTimeout(function() {
        container.classList.add("hidden")
      }, timeout);
    }
  }
}

export {AdminEngine}
