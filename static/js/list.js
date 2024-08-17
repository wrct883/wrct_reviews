const query = urlParams.get('query');
const pos = urlParams.get('pos');
const tableEl = document.querySelector('table');

// make text matching search query bold
function highlightMatches() {
  var regex;
  if (pos === 'icontains')
    regex = new RegExp(query, 'gi');
  else if (pos === 'istartswith')
    regex = new RegExp("^(?:<.+?>)?(" + query + ")", 'i');
  else if (pos === 'iendswith')
    regex = new RegExp("(" + query + ")(?:<.+?>)?$", 'i');

  if (regex) {
    tableEl.querySelectorAll("td").forEach((el) => {
      el.innerHTML = el.innerHTML.trim().replace(regex, (match) => `<b>${match}</b>`);
    });
    // I'm pretty sure someone could use this code to do an XSS attack,
    // but at the same time it's just javascript, it's not like that'll fuck up
    // anyone else
  }
}

if (query && tableEl && pos)
  highlightMatches();
