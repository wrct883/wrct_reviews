/*
 * Note: the following javascript makes several assumptions, including but not limited to:
 * * `totalCount` is defined in `list.html`
 * * the id of the "select all" checkbox is "select-all"
 * * The list table is the first table on the page
 * * the "album" table column is the first column
 * * the album id is in the link "/album/ALBUM_ID" in the album column
 * * the bulk modify url is at /albums/bulk_modify
 *
 * Breaking these assumptions will break the code :(
 * So make sure that if you modify list.html, propogate relevant tables over to this js file
 */
var selectAll = false;
var selected = new Set();
var excluded = new Set();

var checkboxElList = [];

const selectAllEl = document.querySelector("#select-all");
selectAllEl.checked = false;
selectAllEl.addEventListener('change', () => {
  selectAll = selectAllEl.checked;
  if (selectAllEl.checked) {
    checkboxElList.forEach((el) => {
      el.checked = true;
    });
    excluded.clear();
    formEl.classList.remove('hidden');
    updateCount(totalCount);
  }
  else if (excluded.size === 0) {
    checkboxElList.forEach((el) => {
      el.checked = false;
    });
    formEl.classList.add('hidden');
  }
  selected.clear();
});
selectAll.value = selectAllEl.checked;

const tableElBulkModify = document.querySelector("table");
tableElBulkModify.querySelectorAll('tr').forEach((trEl) => {
  var albumEl = trEl.querySelector('td');
  if (!albumEl)
    return;
  var albumId = Number(trEl.querySelector('a').href.split("/album/")[1]);
  var checkboxEl = document.createElement('input');
  checkboxElList.push(checkboxEl);
  checkboxEl.setAttribute("type", "checkbox");
  checkboxEl.addEventListener('change', () => {toggleAlbum(checkboxEl, albumId)});
  albumEl.prepend(checkboxEl);
});

const formEl = document.createElement('form');
formEl.setAttribute('method', "POST");
formEl.setAttribute('action', "/album/bulk_modify");
formEl.innerHTML = token;

const selectAllInput = document.createElement('input');
const selectedInput = document.createElement('input');
const excludedInput = document.createElement('input');
selectAllInput.setAttribute("type", "hidden");
selectAllInput.setAttribute("name", "selectAll");
selectedInput.setAttribute("type", "hidden");
selectedInput.setAttribute("name", "selected");
excludedInput.setAttribute("type", "hidden");
excludedInput.setAttribute("name", "excluded");

const submitEl = document.createElement('button');
submitEl.setAttribute("name", "bulk-modify-list");
submitEl.innerText = "edit selected albums";
submitEl.classList.add('bulk-modify-submit');
// write the values of selected, excluded, and selectAll on submit
submitEl.addEventListener('click', () => {
  selectAllInput.value = selectAll;
  selectedInput.value = JSON.stringify([...selected]);
  excludedInput.value = JSON.stringify([...excluded]);
  formEl.submit();
});
formEl.appendChild(selectAllInput);
formEl.appendChild(selectedInput);
formEl.appendChild(excludedInput);
formEl.appendChild(submitEl);
document.body.appendChild(formEl);
formEl.style.marginTop = submitEl.offsetHeight + "px";
formEl.classList.add('hidden');

function updateCount(count) {
  submitEl.innerText = `edit ${count} selected albums`;
}


function toggleAlbum(el, albumId) {
  if (selectAll) {
    if (el.checked) {
      excluded.delete(albumId);
      if (excluded.size === 0)
        selectAllEl.checked = true;
      updateCount(totalCount - excluded.size);
    }
    else {
      excluded.add(albumId);
      selectAllEl.checked = false;
      updateCount(totalCount - excluded.size);
    }
  } else {
    if (el.checked) {
      selected.add(albumId);
      formEl.classList.remove('hidden');
      updateCount(selected.size);
    }
    else {
      selected.delete(albumId);
      if (selected.size === 0)
        formEl.classList.add('hidden');
      updateCount(selected.size);
    }
  }
}
