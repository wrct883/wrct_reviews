let xhr = new XMLHttpRequest();
xhr.timeout = 5 * 1000; // 5 seconds
xhr.responseType = 'json';

function getUrl(method, params){
  const API_SECRET = "8c96e05d82dcc8bd73ad54b96dd26c25";
  var root = "https://ws.audioscrobbler.com/2.0/";
  var allParams = {
    "method": method,
    "api_key": API_SECRET,
    ...params,
    "format": "json",
  }
  return root +  "?" + new URLSearchParams(allParams).toString();
}

function getAlbum(response){
  var a = response.album;

  var tracksHTML = ""; var imageHTML = "";

  if (a.hasOwnProperty('image')) {
    var image = a.image[Math.min(a.image.length, 3)]["#text"];
    if (image)
      imageHTML = `<img src="${image}"/>`;
  }

  if (a.hasOwnProperty('tracks')) {
    var tracks = a.tracks.track;
    tracksHTML = `<div class='no-contents'><h2>Tracks</h2><ol>`;
    tracks.forEach((track) => {
      tracksHTML += `<li>${track.name}</li>`
    });
    tracksHTML += '</ol></div>';
  }

  var section = document.createElement("section");
  section.innerHTML = `${imageHTML}
  ${tracksHTML}`;
  const parentEl = document.querySelector('#api-info');
  parentEl.appendChild(section);
}

function getArtist(response){
}

function getApi() {
  var url = getUrl(`${table.toLowerCase()}.getinfo`, {"album": album, "artist": artist});
  xhr.open('GET', url);
  xhr.send();
  xhr.onload = function() {
    if (xhr.status != 200) { // analyze HTTP status of the response
      console.log('error', xhr.status, xhr.statusText);
    } else { // show the result
      if (table === "Album")
        getAlbum(xhr.response);
      else if (table === "Artist")
        getArtist(xhr.response);
    }
  };
}
getApi();
