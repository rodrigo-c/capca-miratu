import {QueryListManager} from "./list.js"
import {QueryDetailManager} from "./detail.js"
import {QueryCreateManager, QueryUpdateManager} from "./edit.js"
import {QueryResultManager} from "./results.js"
import {QueryShareManager} from "./share.js"


class QueryManager {
  constructor({engine = null, url_base = ""}) {
    this.letters = "ABCDEFGHIJKLMNOPQRSTUXYZ"
    this.engine = engine
    this.url_base = url_base
    this.list = new QueryListManager({manager:this})
    this.detail = new QueryDetailManager({manager:this})
    this.create = new QueryCreateManager({manager:this})
    this.update = new QueryUpdateManager({manager:this})
    this.result = new QueryResultManager({manager:this, kind: "result"})
    this.questions = new QueryResultManager({manager:this, kind: "questions"})
    this.map = new QueryResultManager({manager:this, kind: "map"})
    this.data = new QueryResultManager({manager:this, kind: "data"})
    this.share = new QueryShareManager({manager: this})
    this._click_go_to_view = this._click_go_to_view.bind(this)
  }

  _create_query_item(item, query_item) {
    query_item.querySelector(".name").textContent = item.name
    query_item.querySelector(".total-responses .value").textContent = item.total_responses
    if (!item.start_at && !item.end_at) {
      query_item.querySelector(".times").classList.add("hidden")
    } else {
      this._set_times(item, query_item)
    }
    let status_value = query_item.querySelector(".status > .status-value")
    status_value.classList.remove("draft", "finished", "active", "earring")
    status_value.textContent = item.status_verbose.label
    status_value.classList.add(item.status_verbose.code)
    return query_item
  }

  _set_times(item, query_item) {
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

  _build_sidebar () {
    let current = this.engine.cursor.focus
    let views_with_sidebar = ["query-detail", "query-update", "query-share"]
    let result_views = ["query-result", "query-data", "query-map", "query-questions"]
    let admin_content = document.querySelector(".admin-content")
    let sidebar = document.querySelector(".admin-content > .sidebar")
    if (!sidebar) {
      sidebar = document.createElement("div")
      sidebar.classList.add("sidebar")
      admin_content.prepend(sidebar)
    } else {
      sidebar.innerHTML = ""
    }
    if ([...result_views, ...views_with_sidebar].includes(current)) {
      sidebar.innerHTML = `
        <div class="sidebar-element${current == 'query-detail'?' current': ''}" to="query-detail">
          Ver consulta
        </div>
        <div class="sidebar-element${current == 'query-update'?' current': ''}" to="query-update">
          Editar
        </div>
        <div class="sidebar-element${current == 'query-share'?' current': ''}" to="query-share">
          Compartir
        </div>
        <div class="sidebar-element${result_views.includes(current)?' current': ''}" to="query-result">
          Resultados
        </div>
      `
      for (let element of sidebar.querySelectorAll(".sidebar-element")) {
        element.addEventListener("click", this._click_go_to_view, false)
      }
    } else if (current == "query-create") {
      sidebar.innerHTML = `
        <div class="sidebar-element current" to="query-create">
          Crear consulta
        </div>
      `
    } else {
      sidebar.remove()
    }
  }

  _click_go_to_view(event) {
    let view = event.target.getAttribute("to")
    if (view != this.engine.cursor.focus) {
      this.engine.show_view(view, true)
    }
  }
}

export {
  QueryManager
}
