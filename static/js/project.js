import {QuerySubmitEngine} from "./submit/engine.js"

// need https://leafletjs.com/
function set_answer_result_map (id, dataset) {
  let latlng = L.latLng(-33.447869, -70.668423)
  let map = L.map(id).setView(latlng, 9)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
  }).addTo(map);
  map.attributionControl.setPrefix("")

  for (let answer of dataset) {
    if (answer.point) {
      let marker = L.marker(answer.point).addTo(map)
      let message = `<b>Enviado en: </b> ${new Date(answer.send_at)}`
      marker.bindPopup(message)
    }
  }
  return map
}

export {QuerySubmitEngine, set_answer_result_map}
