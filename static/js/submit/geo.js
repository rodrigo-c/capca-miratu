
function set_point_input_event(input) {
  let map_data = input.parentElement.querySelector(".map-data")
  let base_layer = new ol.layer.Tile({source: new ol.source.OSM()})
  let options = JSON.parse(map_data.getAttribute("data"))
  input.mapwidget = new MapWidget(options);
  document.getElementById(options.map_id).style = null;
  try {
    let _serializeFeatures = input.mapwidget.serializeFeatures
    let _clearFeatures = input.mapwidget.clearFeatures
    _serializeFeatures = _serializeFeatures.bind(input.mapwidget)
    _clearFeatures = _clearFeatures.bind(input.mapwidget)
    input.mapwidget.serializeFeatures = () => {
      _serializeFeatures()
      input.dispatchEvent(new Event("input"))
    }
    input.mapwidget.clearFeatures = () => {
      _clearFeatures()
      input.dispatchEvent(new Event("input"))
    }
    input.mapwidget.map.getView().setCenter(
      ol.proj.transform([-70.668423, -33.447869], 'EPSG:4326', 'EPSG:3857')
    )
  } catch (e){
    console.log(e)
  }
}

function set_response_geolocation (manager, containers, input_map) {
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition((position) => {
      manager.user_location = {
        lon: position.coords.longitude,
        lat: position.coords.latitude,
      }
      let geolocation_input = containers.identifier.querySelector("input[name='location']")
      geolocation_input.value = `POINT(${manager.user_location.lon} ${manager.user_location.lat})`;

      for (let question_inputs of input_map.question_list) {
        for (let input of question_inputs) {
          if (input.mapwidget) {
            input.mapwidget.map.getView().setCenter(
              ol.proj.transform(
                [manager.user_location.lon, manager.user_location.lat],
                'EPSG:4326',
                'EPSG:3857',
              )
            )
          }
        }
      }
    })
  }
}


export {
  set_point_input_event, set_response_geolocation
}
