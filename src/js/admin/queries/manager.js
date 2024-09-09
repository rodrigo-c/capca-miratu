import {QueryListManager} from "./list.js"
import {QueryDetailManager} from "./detail.js"
import {QueryCreateManager, QueryUpdateManager} from "./edit.js"
import {QueryResultManager} from "./results.js"
import {QueryShareManager} from "./share.js"
import {QueryAPIManager} from "./api.js"


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
    this.api = new QueryAPIManager({manager: this})
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

  _get_question_kind_html (question_data) {
    let html_text = ""
    if (question_data.kind === "TEXT") {
      let type = question_data.text_max_length > 150 ? "largo": "corto"
      html_text += `<div class="query-question-kind-text">Respuesta de texto ${type} (${question_data.text_max_length} caracteres)</div>`
    } else if (question_data.kind === "IMAGE") {
      html_text += `<div class="query-question-kind-image">Respuesta de imagen o foto</div>`
    } else if (question_data.kind === "POINT") {
      html_text += `<div class="query-map-pointer" id="map-pointer-${question_data.uuid}"></div>`
    }
    return html_text
  }

  _set_times(item, query_item) {
    query_item.querySelector(".times").classList.remove("hidden")
    if (item.start_at) {
      let start_at = new Date(item.start_at).toLocaleString().split(",")[0]
      query_item.querySelector(".start-at").classList.remove("hidden")
      query_item.querySelector(".start-at").textContent = `Desde: ${start_at}`
    } else {
      query_item.querySelector(".start-at").classList.add("hidden")
    }
    if (item.end_at) {
      query_item.querySelector(".end-at").classList.remove("hidden")
      let end_at = new Date(item.end_at).toLocaleString().split(",")[0]
      query_item.querySelector(".end-at").textContent = `Hasta: ${end_at}`
    } else {
      query_item.querySelector(".end-at").classList.add("hidden")
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
        <div class="sidebar-element${result_views.includes(current)?' current': ''}" to="query-result">
          Resultados
        </div>
        <div class="sidebar-element${current == 'query-share'?' current': ''}" to="query-share">
          Compartir
        </div>
        <div class="sidebar-element${current == 'query-update'?' current': ''}" to="query-update">
          Editar
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

  get_kind_label(question_data) {
    let kind_label = ""
    if (question_data.kind === "TEXT" && question_data.text_max_length > 150) {
      kind_label = "Texto largo"
    } else if (question_data.kind === "TEXT" && question_data.text_max_length <= 150) {
      kind_label = "Texto corto"
    } else if (question_data.kind === "SELECT") {
      kind_label = "Selección múltiple"
    } else if (question_data.kind === "SELECT_IMAGE") {
      kind_label = "Selección múltiple e imágenes"
    } else if (question_data.kind === "IMAGE") {
      kind_label = "Imagen"
    } else if (question_data.kind === "POINT") {
      kind_label = "Ubicación"
    }
    return kind_label
  }

}

export {
  QueryManager
}
