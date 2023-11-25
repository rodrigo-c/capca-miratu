/* Public query submit view */


class QuerySubmitManager {
  constructor (
    {
      detail_id = "detail-container",
      response_id = "response-container",
      question_class_name = "question",
      hidden_class_name = "hidden"
    } = {}
  ) {
    this.detail = document.getElementById(detail_id);
    this.response = document.getElementById(response_id);
    this.question_list = document.getElementsByClassName(question_class_name);
    this.hidden_class_name = hidden_class_name
    this._add_listener_events()
  }

  _add_listener_events() {
    var start_button = document.getElementById("start-button")
    var next_response_button = document.getElementById("next-response-button")
    console.log(start_button)
    console.log(next_response_button)
    start_button.addEventListener("click", this.show_initial_form, false)
    start_button.manager = this
    next_response_button.addEventListener("click", this.show_question, false)
    next_response_button.manager = this
    next_response_button.question_index = 0
    for (var i = this.question_list.length - 1; i >= 0; i--) {
        var next_question_button = document.getElementById(`next-question-button-${i}`)
        if (next_question_button) {
            next_question_button.addEventListener("click", this.show_question, false)
            next_question_button.question_index = i + 1
            next_question_button.manager = this
        }
    }
  }

  hide_all () {
    this.detail.classList.add(this.hidden_class_name)
    this.response.classList.add(this.hidden_class_name)
    for (let question of this.question_list) {
        question.classList.add(this.hidden_class_name)
    }
  }

  show_initial_form (event) {
    var manager = event.currentTarget.manager
    manager.hide_all()
    manager.response.classList.remove("hidden")
  }

  show_question(event) {
    var manager = event.currentTarget.manager
    var question_index = event.currentTarget.question_index
    manager.hide_all()
    manager.question_list[question_index].classList.remove("hidden")
  }
}
