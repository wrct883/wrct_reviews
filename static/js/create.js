function debounce(func, delay) {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
}

let xhr = new XMLHttpRequest();
xhr.timeout = 5 * 1000; // 5 seconds
xhr.responseType = 'json';

function clearResults(resultsEl) {
  resultsEl.innerHTML = "";
}
function hideResults(resultsEl) {
  resultsEl.classList.add("hidden");
}
function showResults(resultsEl) {
  resultsEl.classList.remove("hidden");
}

function populateResults(json, searchEl, resultsEl, hiddenEl) {
  json.forEach((obj) => {
    var el = document.createElement("div");
    el.classList.add("search-result");
    var name = document.createElement("div");
    name.classList.add("name");
    name.innerText = obj.name;
    el.appendChild(name);
    if (obj.artist) {
      var subtitle = document.createElement("div");
      subtitle.classList.add("subtitle");
      subtitle.innerText = obj.artist;
      el.appendChild(subtitle);
    }

    el.addEventListener("click", () => {
      searchEl.value = obj.name;
      hiddenEl.value = obj.id;
      clearResults(resultsEl);
    });

    resultsEl.appendChild(el);
  });
}

function search(endpoint, query, searchEl, resultsEl, hiddenEl) {
  var url = `${endpoint}?pos=istartswith&query=${query}`;
  xhr.open('GET', url);
  xhr.send();
  xhr.onload = function() {
    if (xhr.status != 200) { // analyze HTTP status of the response
      console.log(xhr.status, xhr.statusText);
    } else { // show the result
      clearResults(resultsEl);
      populateResults(xhr.response, searchEl, resultsEl, hiddenEl);
      searchEl.setAttribute("data-prev-query", searchEl.value);
    }
  };
}

const searchEls = document.querySelectorAll('.search');
searchEls.forEach((el) => {
  const searchEl = el.querySelector("input[type='text']");
  const resultsEl = el.querySelector(".results");
  const hiddenEl = el.querySelector("input[type='hidden']");
  const endpoint = `/search/${hiddenEl.name}`;
  searchEl.addEventListener('keyup', debounce((event) => {

    var query = searchEl.value;
    if (!query.trim())
      hiddenEl.value = "";
    else if (query !== searchEl.getAttribute("data-prev-query")) {
      search(endpoint, searchEl.value, searchEl, resultsEl, hiddenEl);
    }
  }, 300));

  searchEl.addEventListener("blur", () => {
    setTimeout(() => {hideResults(resultsEl)}, 200);
  });

  searchEl.addEventListener("focus", () => {
    showResults(resultsEl);
  });
});


// show/hide subgenres based on what genre is currently selected
function subgenreFiltering() {
  const genreEl = document.querySelector("#id_genre");
  const subgenreEl = document.querySelector("#id_subgenre");
  if (!genreEl || !subgenreEl)
    return;

  // all subgenres start hidden

  function genreChange() {
    var genre = genreEl.options[genreEl.selectedIndex].text;
    subgenreEl.querySelectorAll(`div`).forEach((el) => {
      el.classList.add('hidden');
    });
    subgenreEl.querySelectorAll(`div[data-genre='${genre}']`).forEach((el) => {
      el.classList.remove('hidden');
    });
  }
  genreEl.addEventListener("change", genreChange);
  genreChange();
}
subgenreFiltering();
