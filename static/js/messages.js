$(onLoad)


function onLoad() {
    $('#filter-friends').on('input', filterRows)
    $('.chat_list').on('click',selectChat)
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

function selectChat() {
    $('.chat_list').attr('style',  'background-color:white')
    $(this).attr('style',  'background-color:#dddddd')
}
