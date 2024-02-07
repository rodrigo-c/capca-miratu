class QueryListManager {
  constructor ({manager = null}) {
    this.manager = manager
    this.data = []
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
      let action_button = returned_query_item.querySelector(".action-button")
      action_button.query_uuid = item.uuid
      action_button.addEventListener(
        "click", this.manager.engine.click_query_detail, false
      )
      query_list.appendChild(returned_query_item)
    }
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_list.classList.remove("hidden")
  }

}

export {QueryListManager}
