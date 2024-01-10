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
    let template = document.querySelector("#query-item-template").cloneNode(true)
    template.classList.remove("hidden")

    let list_container = this.views.query_list.querySelector(".query-item-list")
    for (let item of this.storage.query_list) {
      let container = template.cloneNode(true)
      container.querySelector(".name").textContent = item.name
      if (!item.start_at && !item.end_at) {
        container.querySelector(".times").remove()
      } else if (item.start_at) {
        container.querySelector(".start-at").textContent = item.start_at
      } else if (item.end_at) {
        container.querySelector(".end-at").textContent = item.end_at
      }

      let status_value = container.querySelector(".status > .value")
      if (!item.active) {
        status_value.textContent = "Borrador"
      } else if (item.active && !item.is_active) {
        status_value.textContent = "Finalizada"
      } else if (item.active && item.is_active) {
        status_value.textContent = "Activa"
      }
      list_container.appendChild(container)
    }
    this._hide_all_views()
    this.views.query_list.classList.remove("hidden")
  }
}

export {AdminEngine}
