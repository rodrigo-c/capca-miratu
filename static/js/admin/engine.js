class AdminEngine {
  constructor (
    { url_base = "" }
  ) {
    this.url_base = url_base
    this.storage = {}
    this._set_admin_sidebar()
    this._set_views()
    this.show_view("querylist")
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
    if (name == "querylist") {
      this._show_query_list_view()
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

  _set_query_list_in_view() {
    let query_list = this.views.query_list.querySelector(".query-item-list")
    for (let item of this.storage.query_list) {
      let query_item = this._create_query_item(item)
      query_list.appendChild(query_item)
    }
    this._hide_all_views()
    this.views.query_list.classList.remove("hidden")
  }

  _create_query_item(item) {
    let template = document.querySelector("#query-item-template").cloneNode(true)
    template.classList.remove("hidden")
    let query_item = template.cloneNode(true)
    query_item.querySelector(".name").textContent = item.name
    if (!item.start_at && !item.end_at) {
      query_item.querySelector(".times").remove()
    } else {
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

export {AdminEngine}
