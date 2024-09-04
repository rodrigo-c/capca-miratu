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
    this._click_copy_link = this._click_copy_link.bind(this)
    this._click_download_link = this._click_download_link.bind(this)
    this._click_print_link = this._click_print_link.bind(this)
    let copy_link = document.querySelector("#query-share-copy-link")
    copy_link.addEventListener("click", this._click_copy_link, false)
    let download_link = document.querySelector("#query-share-download-link")
    download_link.addEventListener("click", this._click_download_link, false)
    let print_link = document.querySelector("#query-share-print-link")
    print_link.addEventListener("click", this._click_print_link, false)
  }

  _click_copy_link(event) {
    let submit_link = this._get_submit_link()
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
  }

  _click_download_link (event) {
    let pdf_link = this._get_pdf_link()
    window.open(pdf_link + "?k=download")
  }

  _click_print_link (event) {
    let pdf_link = this._get_pdf_link()
    let w = window.open(pdf_link)
    w.print()
  }

  _get_submit_link() {
    return `https://${location.host}/submit/${this.manager.engine.cursor.key}`
  }

  _get_pdf_link () {
    return `${this.manager.url_base}${this.manager.engine.cursor.key}/share/`
  }
}

export {QueryShareManager}
