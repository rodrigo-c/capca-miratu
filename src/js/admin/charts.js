function get_chart (config) {
    let id = config.id
    let type = config.type
    let values = config.values
    let labels = config.labels
    let options = config.options? config.options: {}
    let barColors = [
        "#c1368c", "#a34895","#143358","#495599","#54baae"
    ]
    let data = {
        labels: labels,
        datasets: [
            {backgroundColor: barColors, data: values, label: config.label}
        ]
    }
    options.scales = {x: {ticks: {display: false}, grid: {display: false}}, y: {ticks:{display: false}}}
    options.plugins = {
        datalabels: {color: "#fff"}, legend: {display: false}, tooltip: {enabled: false}
    }
    options.animation = {duration: 0}
    Chart.register(ChartDataLabels)
    let chart = new Chart(id, {
        type: type,
        data: data,
        options: options,
    })
    let labels_container = document.querySelector(`#${id}-labels`)
    let color_index = 0
    let value_index = 0

    for (let label of labels) {
        let element = document.createElement("div")
        element.classList.add("chart-label-container")
        let color_element = document.createElement("div")
        color_element.classList.add("chart-label-color")
        if (color_index >= barColors.length) {color_index = 0}
        color_element.style.backgroundColor = barColors[color_index]
        element.appendChild(color_element)
        let label_value = document.createElement("div")
        label_value.classList.add("chart-label-value")
        label_value.textContent = `${values[value_index]} - ${label}`
        element.appendChild(label_value)
        labels_container.append(element)
        color_index += 1
        value_index += 1
    }
    labels_container.classList.remove("hidden")
    return chart
}

export {get_chart}
