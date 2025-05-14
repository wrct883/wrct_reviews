let xhr = new XMLHttpRequest();
xhr.timeout = 5 * 1000; // 5 seconds
xhr.responseType = 'json';

function getAlbum(response){

  var tracksHTML = ""; var imageHTML = "";

  if (response.hasOwnProperty('image')) {
    imageHTML = `<img src="${response.image}"/>`;
  }

  if (response.hasOwnProperty('tracks')) {
    var tracks = response.tracks;
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
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  xhr.open('POST', '/api/music', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.setRequestHeader('X-CSRFToken', csrfToken);

  var data = {
    album: album,
    artist: artist,
    table: table,
  };

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

  xhr.send(JSON.stringify(data));
}
getApi();

