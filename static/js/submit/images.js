
function set_image_preview (input) {
  let files = input.files
  let input_container = input.parentElement
  let input_add_icon = input_container.querySelector(".image-icon")
  let input_close_icon = input_container.querySelector(".closed-icon")
  let payload = ""
  for (var i = files.length - 1; i >= 0; i--) {
    let url = URL.createObjectURL(files[i])
    payload+=`url(${url})`
    if (i > 0) {payload+=", "}
  }
  if (payload != "") {
    input_container.style.backgroundImage = payload
  } else {
    input_container.style.backgroundImage = null
  }

  if (files.length > 0) {
    input_add_icon.classList.add("hidden")
    input_close_icon.classList.remove("hidden")

  } else {
    input_add_icon.classList.remove("hidden")
    input_close_icon.classList.add("hidden")
  }
}


export {set_image_preview}
