function _show_without_image (input) {
  let container = input.parentElement
  container.style.backgroundImage = null
  container.querySelector(".image-icon").classList.remove("hidden")
  container.querySelector(".image-icon-description").classList.remove("hidden")
  container.querySelector(".closed-icon").classList.add("hidden")
}

function _show_with_image (input, url) {
  let container = input.parentElement
  container.style.backgroundImage = `url(${url})`
  container.querySelector(".image-icon").classList.add("hidden")
  container.querySelector(".image-icon-description").classList.add("hidden")
  container.querySelector(".closed-icon").classList.remove("hidden")
}

function set_image_preview (input) {
  _show_without_image(input)
  let files = input.files
  let reducer = new window.ImageBlobReduce({
    pica: window.ImageBlobReduce.pica({ features: [ 'js', 'wasm', 'ww' ] })
  });
  if (files.length > 0) {
    let file = files[0]
    reducer.toBlob(
      file, {max: 1000}
    ).then(
      blob => {
        let url = URL.createObjectURL(blob)
        let reduced_file = new File([blob], input.files[0].name, {type:"mime/type", lastModified:new Date().getTime()})
        let files_container = new DataTransfer()
        files_container.items.add(reduced_file)
        input.files = files_container.files
        _show_with_image(input, url)
      }
    ).catch(
      error => {console.log(error)}
    )
  }
}


export {set_image_preview}
