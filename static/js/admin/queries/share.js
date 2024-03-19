class QueryShareManager {
  constructor ({manager = null, kind = null}) {
    this.manager = manager
    this.data = {}

  }
  show_view(on_history) {
    this.manager._build_sidebar()
    this.manager.engine._hide_all_views()
    this._set_in_view()
    this.manager.engine.views.query_share.classList.remove("hidden")
    if (on_history) {
      this.manager.engine._set_url_params(`query-share`, this.manager.engine.cursor.key)
    }
  }

  _set_in_view() {
    this._set_copy_link()
    this._set_download_link()
    this._set_print_link()
  }

  _set_copy_link () {
    let copy_link = document.querySelector("#query-share-copy-link")
    let submit_link = this._get_submit_link()
    copy_link.addEventListener("click", (event) => {
      navigator.clipboard.writeText(submit_link)
      let action_container = event.target.closest(".action-container")
      if (!action_container.querySelector(".action-success")) {
        let success = document.createElement("div")
        success.classList.add("action-success")
        success.innerHTML = "<i class='icon ok-simple'></i> Copiado correctamente"
        action_container.appendChild(success)
        setTimeout(function () {
          action_container.querySelector(".action-success").remove()
        }, 3000)
      }
    })
  }

  _set_download_link () {
    let download_link = document.querySelector("#query-share-download-link")
    let pdf_link = this._get_pdf_link()
    download_link.addEventListener("click", (event) => {
      window.open(pdf_link + "?k=download")
    })
  }

  _set_print_link () {
    let print_link = document.querySelector("#query-share-print-link")
    let pdf_link = this._get_pdf_link()
    print_link.addEventListener("click", (event) => {
      window.open(pdf_link).print()
    })
  }

  _get_submit_link() {
    return `https://${location.host}/submit/${this.manager.engine.cursor.key}`
  }

  _get_pdf_link () {
    return `${this.manager.url_base}${this.manager.engine.cursor.key}/share/`
  }
}

export {QueryShareManager}
