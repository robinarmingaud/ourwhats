$(onLoad)


function onLoad() {
    $('#filter-friends').on('input', filterRows)
    $('#filter-messages').on('input', filterMessages)
    $('#filter-users').on('input', filterUsers)
}

function filterRows() {
  let filter = this.value.toLowerCase();
  $('.chat_list')
      .show()
      .filter(function() {
        return !($(this).data('name').toLowerCase().includes(filter))
      })
      .hide()
}

function filterUsers() {
    let filter = this.value.toLowerCase();
    $('.user-list')
      .show()
      .filter(function() {
        return !($(this).text().toLowerCase().includes(filter))
      })
      .hide()
}

function filterMessages() {
  let filter = this.value.toLowerCase();
  $('.sent-block')
      .show()
      .filter(function() {
        return !($(this).text().toLowerCase().includes(filter))
      })
      .hide()

    $('.received-block')
      .show()
      .filter(function() {
        return !($(this).text().toLowerCase().includes(filter))
      })
      .hide()
}