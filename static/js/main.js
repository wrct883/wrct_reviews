function close_message(el){
  el.parentElement.remove();
}

var urlParams = new URLSearchParams(window.location.search);

function setParam(param, page) {
    urlParams.set(param, page);
    var newUrl = window.location.pathname + '?' + urlParams.toString() + '#' + param;
    window.location.href = newUrl;
}

function shuffleOrdering(ordering_str, param='o', id=null) {
  var current_ordering = urlParams.get(param);
  var desc_ordering = '-' + ordering_str;
  urlParams.set(param, desc_ordering);
  // if there is already an ordering, and that ordering is the same as the descending one...
  if (current_ordering && current_ordering == desc_ordering)
    urlParams.set(param, ordering_str); // set it to be ascending now
  else if (current_ordering && current_ordering == ordering_str)
    urlParams.delete(param); // clear it

  var newUrl = window.location.pathname + '?' + urlParams.toString();
  if (id)
    newUrl += "#" + id;
  window.location.href = newUrl;
}


// remove a tags that point to the current page
function removeSelfLinks() {
  const links = document.querySelectorAll('a:not(nav a):not(.active)');
  links.forEach((link) => {
    if (link.href === window.location.href) {
      const textNode = document.createTextNode(link.textContent);
      link.parentNode.replaceChild(textNode, link);
    }
  });
}
removeSelfLinks();


// if there are any search query parameters set
// make the search inputs have those selected
function setSearchForm() {
  var path = window.location.pathname;
  var tables = ['album', 'artist', 'genre', 'review', 'label'];
  var table;
  for (var i = 0; i < tables.length; i++) {
    table = tables[i];
    if (path.search(table) >= 0) {
      document.querySelectorAll(`select[name='table'] option[value='${table}']`).forEach((el) => {
        el.selected = true;
      });
      break;
    }
  }

  var pos = urlParams.get("pos");
  var query = urlParams.get("query");
  if (!query || !pos)
    return;

  document.querySelectorAll(`select[name='pos'] option[value='${pos}']`).forEach((el) => {
    el.selected = true;
  });
  document.querySelectorAll("input[name='query']").forEach((el) => {
    el.value = query;
    el.placeholder = query;
  });
}
setSearchForm();
