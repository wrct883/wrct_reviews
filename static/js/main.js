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
  const links = document.querySelectorAll('a:not(nav a)');
  links.forEach((link) => {
    if (link.href === window.location.href) {
      const textNode = document.createTextNode(link.textContent);
      link.parentNode.replaceChild(textNode, link);
    }
  });
}
removeSelfLinks();
