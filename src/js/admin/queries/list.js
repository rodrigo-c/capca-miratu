class QueryListManager {
  constructor ({manager = null}) {
    this.manager = manager
    this.data = []
    this._click_query_detail = this._click_query_detail.bind(this)
    this._click_query_create = this._click_query_create.bind(this)
    this._click_status_dropdown = this._click_status_dropdown.bind(this)
    this._click_status_filter = this._click_status_filter.bind(this)
    this._change_search_input = this._change_search_input.bind(this)
    this.filters = {
      search: null,
      status: null,
    }
    this.comps = {
      status: {
        button: document.querySelector("#query-list .status-filter-button"),
        content: document.querySelector("#query-list .status-filter-dropdown"),
        items: document.querySelectorAll("#query-list .status-filter .dropdown-item"),
      },
      search: document.querySelector("#query-list #query-list-search-input"),
      query_list: document.querySelector("#query-list .query-item-list"),
      query_template: document.querySelector("#query-item-template"),
      query_create: {
        content: document.querySelector("#query-list-empty-content"),
        action: document.querySelector("#query-list-create-query"),
      }
    }
    this.comps.status.button.addEventListener(
      "click", this._click_status_dropdown, false
    )
    for (let item of this.comps.status.items) {
      item.addEventListener("click", this._click_status_filter, false)
    }
    this.comps.search.addEventListener("input", this._change_search_input, false)
    this.comps.query_create.action.addEventListener("click", this._click_query_create, false)
  }

  show_view(on_history) {
    fetch (this.manager.url_base, {
      method: "GET",
      headers: {"Content-Type": "application/json"},
      credentials: "same-origin"
    })
    .then(response=> {
      if (response.ok) {
        response.json()
        .then((data)=> {
          this.data = data.list
          this._set_in_view()
          if (on_history) {
            this.manager.engine._set_url_params("query-list", null)
          }
        })
      } else {
        console.log(response)
      }
    })
  }

  _set_in_view() {
    if (this.data.length > 0) {
      this.comps.query_create.content.classList.add("hidden")
      this._set_query_list()
    } else {
      this.comps.query_list.innerHTML = ""
      this.comps.query_create.content.classList.remove("hidden")
    }
    this.manager._build_sidebar()
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_list.classList.remove("hidden")
  }

  _set_query_list() {
    this.comps.query_list.innerHTML = ""
    let template = this.comps.query_template.cloneNode(true)
    template.classList.remove("hidden")
    for (let item of this.data) {
      if (this._is_query_in_the_filter(item)) {
        let query_item = template.cloneNode(true)
        let returned_query_item = this.manager._create_query_item(item, query_item)
        let detail_link = returned_query_item.querySelector(".secondary-button.item-detail-link")
        detail_link.query_uuid = item.uuid
        detail_link.addEventListener(
          "click", this._click_query_detail, false
        )
        if (this.manager.engine.user.is_superuser && item.created_by_email) {
          let email = document.createElement("div")
          email.classList.add("query-item-created-by")
          email.textContent = item.created_by_email
          returned_query_item.appendChild(email)
        }
        this.comps.query_list.appendChild(returned_query_item)
      }
    }
  }

  _is_query_in_the_filter(query) {
    if (!this.filters.search && !this.filters.status) {
      return true
    }
    let lower_search = typeof this.filters.search === "string" ? this.filters.search.toLowerCase() : null
    let search_in_name = lower_search ? query.name.toLowerCase().includes(lower_search): true
    let equal_status = this.filters.status ? query.status_verbose.code === this.filters.status: true
    return search_in_name && equal_status
  }

  _click_query_detail (event) {
    this.manager.engine.cursor.key = event.currentTarget.query_uuid
    this.manager.engine.show_view("query-detail", true)
  }

  _click_query_create (event) {
    this.manager.engine.show_view("query-create", true)
  }

  _click_status_dropdown (event) {
    if (this.comps.status.content.classList.contains("hidden")) {
      this.comps.status.content.classList.remove("hidden")
    } else {
      this.comps.status.content.classList.add("hidden")
    }
  }

  _click_status_filter (event) {
    for (let item of this.comps.status.items) {
      item.classList.remove("active")
    }
    event.target.classList.add("active")
    let status_code = event.target.getAttribute("code")
    if (status_code) {
      this.comps.status.button.querySelector(".current").textContent = event.target.textContent
      this.filters.status = status_code
    } else {
      this.comps.status.button.querySelector(".current").textContent = "Filtrar"
      this.filters.status = null
    }
    this._set_query_list()
    this.comps.status.content.classList.add("hidden")
  }

  _change_search_input (event) {
    let value = typeof event.target.value === "string" ? event.target.value.trim(): null
    value = value !== ""? value : null
    event.target.value = value
    this.filters.search = value
    this._set_query_list()
  }

}

export {QueryListManager}
