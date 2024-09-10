class QueryAPIManager {
  constructor ({manager = null, kind = null}) {
    this.manager = manager
    this.api_config = {}
    this._click_copy_link = this._click_copy_link.bind(this)
    this._get_curl_example = this._get_curl_example.bind(this)
    this._click_endpoint_send = this._click_endpoint_send.bind(this)
    this._input_endpoint_url_code = this._input_endpoint_url_code.bind(this)
    this.comp = {
      token: {
        value: document.querySelector("#query-api-token-value"),
        copy_link: document.querySelector("#query-api-token-copy-link"),
      },
      endpoints: document.querySelector("#query-api-endpoints"),
    }
    this.desc_paths = {
      list: {
        name: "Todas las consultas",
        description: "Retorna los datos generales de todas las consultas creadas por el usuario.",
      },
      results: {
        name: "Resultados de una consulta",
        description: "Retorna los resultados de una consulta creada por el usuario."
      },
      geojson: {
        name: "Resultados de una consulta en GeoJSON",
        description: "Retorna los resultados de una consulta en GeoJSON"
      }
    }
  }
  show_view(on_history) {
    this.comp.endpoints.innerHTML = ""
    fetch (`${this.manager.url_base}api_config/`, {
      method: "GET",
      headers: {"Content-Type": "application/json"},
      credentials: "same-origin"
    })
    .then(response=> {
      if (response.ok) {
        response.json()
        .then((data)=> {
          this.api_config = data
          this._set_in_view()
          if (on_history) {
            this.manager.engine._set_url_params("query-api", null)
          }
        })
      } else {
        console.log(response)
      }
    })
  }
  _set_in_view() {
    this.manager._build_sidebar()
    this._set_token_control()
    this._set_endpoints()
    this.manager.engine._hide_all_views()
    this.manager.engine.views.query_api.classList.remove("hidden")
  }

  _set_token_control () {
    this.comp.token.value.innerText = this.api_config.token
    this.comp.token.copy_link.addEventListener(
      "click", this._click_copy_link, false
    )
  }

  _set_endpoints () {
    for (let path in this.api_config.paths) {
      let container = this._get_endpoint_container_element(path)
      this.comp.endpoints.appendChild(container)
      this._set_endpoint_events(container, path)
    }
  }

  _get_endpoint_container_element (path) {
    let container = document.createElement("div")
    container.classList.add("query-api-endpoint")
    container.setAttribute("id", `query-api-endpoint-${path}`)
    container.setAttribute("path", path)
    let curl = this._get_curl_example(path)
    container.innerHTML = `
      <div class="endpoint-name">${this.desc_paths[path].name}</div>
      <div class="endpoint-description">${this.desc_paths[path].description}</div>
      <div class="endpoint-controls">
        <div class="endpoint-params hidden"></div>
        <div class="endpoint-buttons">
          <div class="endpoint-clear secondary-button">Limpiar</div>
          <div class="endpoint-send primary-button">Enviar</div>
        </div>
      </div>
      <div class="endpoint-curl-preview">
        <div class="endpoint-curl-desc">Ejemplo con curl</div>
        <div class="endpoint-curl-value" id="endpoint-${path}-curl-value">${curl}</div>
        <div class="endpoint-curl-copy copy-link-container">
          <div class="secondary-button"
             value="endpoint-${path}-curl-value">Copiar
          </div>
        </div>
      </div>
      <div class="endpoint-response">
        <div class="endpoint-response-desc">Respuesta</div>
        <textarea class="endpoint-response-value"></textarea>
      </div>
    `
    return container
  }

  _set_endpoint_events (container, path) {
    if (["results", "geojson"].includes(path)) {
      let params_container = container.querySelector(".endpoint-params")
      params_container.innerHTML = `
        <div class="param-url-code">
          <div class="param-url-code-desc">Código URL</div>
          <input class="param-url-code-input" type="text">
        </div>
      `
      params_container.classList.remove("hidden")
      let input = params_container.querySelector(".param-url-code-input")
      input.addEventListener("input", this._input_endpoint_url_code, false)
    }
    let send = container.querySelector(".endpoint-send")
    send.addEventListener("click", this._click_endpoint_send, false)
    let copy = container.querySelector(".endpoint-curl-copy")
    copy.addEventListener("click", this._click_copy_link, false)
    let clear = container.querySelector(".endpoint-clear")
    clear.addEventListener("click", this._click_clear_endpoint_response, false)
  }

  _input_endpoint_url_code (event) {
    let container = event.target.closest(".query-api-endpoint")
    let path = container.getAttribute("path")
    let curl = this._get_curl_example(path, event.target.value)
    container.querySelector(".endpoint-curl-value").innerText = curl
  }

  _click_clear_endpoint_response (event) {
    let container = event.target.closest(".query-api-endpoint")
    let response_value = container.querySelector(".endpoint-response-value")
    response_value.value = ""
    response_value.removeAttribute("rows")
  }

  _click_endpoint_send (event) {
    let container = event.target.closest(".query-api-endpoint")
    let response_value = container.querySelector(".endpoint-response-value")
    event.target.classList.add("disabled")
    response_value.value = "Cargando..."
    let path = container.getAttribute("path")
    let url_code_input = container.querySelector(".param-url-code-input")
    let url_code = url_code_input ? url_code_input.value: null
    let url = this._get_full_path(path, url_code)
    fetch (url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Token ${this.api_config.token}`
      },
    })
    .then(response=> {
      if (response.ok) {
        response.json()
        .then((data)=> {
          response_value.value = JSON.stringify(data, null, "\t")
          response_value.setAttribute("rows", "20")
          event.target.classList.remove("disabled")
        })
      } else if (response.status == 404){
        response_value.value = "No encontrado, verifique el código URL (url_code) de la consulta."
        event.target.classList.remove("disabled")
      } else {
        console.log(response)
      }
    })
  }

  _get_full_path (path, url_code) {
    let full_path = this.api_config.paths[path]
    if (["results", "geojson"].includes(path)) {
      let code = url_code ? url_code: "[url_code]"
      full_path = full_path.replace("--url_code--", code)
    }
    return full_path
  }

  _get_curl_example (path, url_code) {
    let full_path = this._get_full_path(path, url_code)
    return `curl -X GET ${this.api_config.host}${full_path} -H 'Authorization: Token ${this.api_config.token}'`
  }

  _click_copy_link (event) {
    let value_element_id = event.target.getAttribute("value")
    let value = document.querySelector(`#${value_element_id}`).innerText
    navigator.clipboard.writeText(value)
    let container = event.target.closest(".copy-link-container")
    if (!container.querySelector(".action-success")) {
      let success = document.createElement("div")
      success.classList.add("action-success")
      success.innerHTML = "<i class='icon ok-simple'></i> Copiado"
      container.appendChild(success)
      setTimeout(function () {
        container.querySelector(".action-success").remove()
      }, 3000)
    }
  }
}

export {
  QueryAPIManager
}
