class QueryListManager {
  constructor ({manager = null}) {
    this.manager = manager
    this.data = []
    this._click_query_detail = this._click_query_detail.bind(this)
    this._click_query_update = this._click_query_update.bind(this)
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
    let template = document.querySelector("#query-item-template").cloneNode(true)
    template.classList.remove("hidden")
    let query_list = this.manager.engine.views.query_list.querySelector(".query-item-list")
    query_list.innerHTML = ""
    for (let item of this.data) {
      let query_item = template.cloneNode(true)
      let returned_query_item = this.manager._create_query_item(item, query_item)
      let detail_link = returned_query_item.querySelector(".action-button.item-detail-link")
      detail_link.query_uuid = item.uuid
      detail_link.addEventListener(
        "click", this._click_query_detail, false
      )
      let update_link = returned_query_item.querySelector(".action-button.item-update-link")
      update_link.query_uuid = item.uuid
      update_link.addEventListener(
        "click", this._click_query_update, false
      )
      if (this.manager.engine.user.is_superuser && item.created_by_email) {
        let email = document.createElement("div")
        email.classList.add("query-item-created-by")
        email.textContent = item.created_by_email
        returned_query_item.appendChild(email)
      }
      query_list.appendChild(returned_query_item)
    }
    this.manager._build_sidebar()
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_list.classList.remove("hidden")
  }

  _click_query_detail (event) {
    this.manager.engine.cursor.key = event.currentTarget.query_uuid
    this.manager.engine.show_view("query-detail", true)
  }

  _click_query_update (event) {
    this.manager.engine.cursor.key = event.currentTarget.query_uuid
    this.manager.engine.show_view("query-update", true)
  }

}

export {QueryListManager}
