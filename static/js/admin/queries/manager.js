import {QueryListManager} from "./list.js"
import {QueryDetailManager} from "./detail.js"
import {QueryCreateManager} from "./edit.js"


class QueryManager {
  constructor({engine = null, url_base = ""}) {
    this.engine = engine
    this.url_base = url_base
    this.list = new QueryListManager({manager:this})
    this.detail = new QueryDetailManager({manager:this})
    this.create = new QueryCreateManager({manager:this})
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

}

export {
  QueryManager
}
