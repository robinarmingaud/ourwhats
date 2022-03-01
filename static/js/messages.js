$(onLoad)



function onLoad() {
  $('#filter-friends').on('input', filterRows)
}

function filterRows() {
  let filter = this.value.toLowerCase();
  console.log(filter)
  $('#h5').show().filter( function() {return !$(this).data.includes(filter).hide()})
}
