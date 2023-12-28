
class SubmitMapWidget extends MapWidget {
  constructor (options) {
    super(options)
    document.getElementById(options.map_id).style = null;
    this.map.getView().setCenter(
      ol.proj.transform([-70.668423, -33.447869], 'EPSG:4326', 'EPSG:3857')
    )
    this.interactions.modify.setActive(false)
    this.map.getView().on(
      "change:center", (event) => {
        let feature = this.get_feature_marker()
        if (feature) {
          let center = this.map.getView().getCenter()
          let geometry = feature.getGeometry()
          geometry.setCoordinates(center)
          this.serializeFeatures()
        }
      }
    )
    this.featureOverlay.setStyle(new ol.style.Style({
      image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
        color: '#8959A8',
        crossOrigin: 'anonymous',
        src: options.point_image_url,
      })),
    }));
  }
  get_feature_marker() {
    let features = this.featureOverlay.getSource().getFeatures()
    return features.length > 0 ? features[0]: null
  }

  createMap() {
    return new ol.Map({
        target: this.options.map_id,
        controls: ol.control.defaults.defaults({attribution: false}),
        layers: [new ol.layer.Tile({source: new ol.source.OSM()})],
        view: new ol.View({
            zoom: this.options.default_zoom
        })
    });
  }

  dispatch_input_event() {
    document.getElementById(this.options.id).dispatchEvent(new Event("input"))
  }

  serializeFeatures () {
    super.serializeFeatures()
    let feature = this.get_feature_marker()
    let geometry = feature.getGeometry()
    this.map.getView().setCenter(geometry.getCoordinates())
    this.dispatch_input_event()
  }

  clearFeatures () {
    super.clearFeatures()
    this.dispatch_input_event()
  }

}

function set_point_input_event(input) {
  let map_data = input.parentElement.querySelector(".map-data")
  let options = JSON.parse(map_data.getAttribute("data"))
  input.mapwidget = new SubmitMapWidget(options);
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
