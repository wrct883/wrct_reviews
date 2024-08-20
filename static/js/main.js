function close_message(el){
  el.parentElement.remove();
}

var urlParams = new URLSearchParams(window.location.search);

function setParam(param, page) {
    urlParams.set(param, page);
    var newUrl = window.location.pathname + '?' + urlParams.toString() + '#' + param;
    window.location.href = newUrl;
}

const ORDERING_SUFFIX = "_o";
const ORDERING_DIV = "."
function shuffleOrdering(field, param) {
  var orderingParam = param + ORDERING_SUFFIX;
  var currentOrdering = urlParams.get(orderingParam);
  var orderingList = currentOrdering ? currentOrdering.split(ORDERING_DIV) : [];
  var descField = "-" + field;

  // descending -> ascending -> none -> descending

  // we're currently filtering descending -> ascending
  if (orderingList.indexOf(descField) >= 0)
    orderingList[orderingList.indexOf(descField)] = field;
  // currently filtering ascending -> none
  else if (orderingList.indexOf(field) >= 0)
    orderingList.splice(orderingList.indexOf(field), 1);
  // not filtering by this field -> descending
  else
    orderingList.push(descField);


  if (orderingList.length > 0)
    urlParams.set(orderingParam, orderingList.join(ORDERING_DIV));
  else
    urlParams.delete(orderingParam);

  var newUrl = window.location.pathname;
  if (urlParams.toString())
    newUrl += '?' + urlParams.toString();
  newUrl += "#" + param;
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
  var tables = ['album', 'artist', 'genre', 'review', 'label', 'user'];
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

  function setSelect(...names) {
    names.forEach((name) => {
      var value = urlParams.get(name);
      if (value) {
        document.querySelectorAll(`select[name='${name}'] option[value='${value}']`).forEach((el) => {
          el.selected = true;
        });
      }
    });
  }
  function setInput(...names) {
    names.forEach((name) => {
      console.log(name);
      var value = urlParams.get(name);
      if (value) {
        console.log('has value', value);
        document.querySelectorAll(`input[name="${name}"]`).forEach((el) => {
          console.log('hey!', el);
          el.value = value;
          el.placeholder = value;
        });
      }
    });
  }

  setInput('query');
  setSelect('pos');

  setSelect('genre', 'status');
  setInput('start_date', 'end_date');
}
setSearchForm();
