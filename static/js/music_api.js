const MB = "https://musicbrainz.org/ws/2/";
const CAA = "https://coverartarchive.org/release/";
const HEADERS = { headers: { 'User-Agent': 'wrct_reviews (eng@wrct.org)'} };
const parentEl = document.querySelector('#api-info');

function getMBUrl(method, mbid, params){
  var allParams = {
    ...params,
    "fmt": "json",
  }
  const mbidEncoded = mbid ? encodeURIComponent(mbid) : "";
  return MB + method + "/" + mbidEncoded + "?" + new URLSearchParams(allParams).toString();
}

async function getAlbumMBID(albumName, artistName) {
  const albumNameEncoded = encodeURIComponent(albumName);
  const artistNameEncoded = encodeURIComponent(artistName);
  const searchUrl =
    getMBUrl(
      'release',
      null,
      { query: `release:${albumNameEncoded} AND artist:${artistNameEncoded}` }
    );

  const searchResponse = await fetch(searchUrl, HEADERS);

  const searchData = await searchResponse.json();

  if (!searchData.releases || searchData.releases.length === 0) {
    return { error: 'Album not found' };
  }

  const releases = searchData.releases;
  let mbid = null;

  const digitalRelease = releases.find(release =>
    release.media && release.media.some(media =>
      media.format && media.format.toLowerCase().includes('digital')
    )
  );

  const cdRelease = digitalRelease ? null :
    releases.find(release =>
      release.media && release.media.some(media =>
        media.format && media.format.toLowerCase() === 'cd'
      )
    );

  // Digital over cd over other (musicbrainz has a lot of poor art because of alternative releases)
  mbid = digitalRelease ? digitalRelease.id : (cdRelease ? cdRelease.id : releases[0].id);
  return mbid;
}

// #TODO: this doesnt filter good enough (there are too many results)
async function getArtistMBID(albumName, artistName) {
  const albumNameEncoded = encodeURIComponent(albumName);
  const artistNameEncoded = encodeURIComponent(artistName);
  const searchUrl =
    getMBUrl(
      'artist',
      null,
      {
        query: `release:${albumNameEncoded} AND artist:${artistNameEncoded}`,
        limit: 1,
      }
    );
  const searchResponse = await fetch(searchUrl, HEADERS);
  const searchData = await searchResponse.json();
  if (!searchData.artists || searchData.artists.length === 0) {
    return { error: 'Artist not found' };
  }
  return searchData.artists[0].id;
}

async function getAlbum(mbid) {
  const releaseUrl = getMBUrl('release', mbid, { inc: 'recordings+artist-credits', limit: 1 });

  const releaseResponse = await fetch(releaseUrl, HEADERS);

  const releaseData = await releaseResponse.json();

  const coverUrl = `${CAA}${mbid}/front-500`;

  const tracks = releaseData.media[0].tracks.map(track => ({
    position: track.position,
    title: track.title,
    duration: track.length ? Math.floor(track.length / 1000) : null
  }));

  return {
    tracks: tracks,
    coverUrl: coverUrl,
  };
}

async function getArtist(mbid) {
  console.log("unimplemented");
}

// Very east to add more information, musicbrainz has a lot of data
async function handleAlbum() {
  // #TODO: start storing the mbids in the backend to simplify this, it will also
  // make the artist search much easier. Need to add musicbrainz integration to the
  // add interface
  const mbid = await getAlbumMBID(album, artist);
  const albumInfo = await getAlbum(mbid);

  var tracksHTML = ""; var imageHTML = "";

  if (albumInfo.coverUrl) {
    imageHTML = `<img src="${albumInfo.coverUrl}" alt="Cover Art"/>`;
  }

  if (albumInfo.tracks) {
    tracksHTML = `<div class='no-contents'><h2>Tracks</h2><ol>`;
    albumInfo.tracks.forEach(track => {
      tracksHTML += `<li>${track.title} - ${track.duration ? `${Math.floor(track.duration / 60)}:${String(track.duration % 60).padStart(2, '0')}` : 'N/A'}</li>`;
    });
    tracksHTML += '</ol></div>';
  }

  var section = document.createElement("section");

  section.innerHTML = `${imageHTML}
  ${tracksHTML}`;
  parentEl.appendChild(section);
}

function getApi() {
  try {
    if (table == "Album")
      handleAlbum();
    else
      console.error('currently only handle albums');
  } catch (error) {
    console.error('Error:', error);
  }
}

getApi();

