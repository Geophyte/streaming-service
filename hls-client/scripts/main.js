const videoPlayer = document.getElementById('video-player');
const videoNameInput = document.getElementById('video-name');
const videoQualitySelect = document.getElementById('video-resolution');
const coordinatorUrl = 'http://127.0.0.1:5000/servers/';

function loadSource(videoUrl) {
  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(videoUrl);
    hls.attachMedia(videoPlayer);
  } else {
    window.alert('HLS is not supported');
  }
}

async function loadVideo() {
  const videoName = videoNameInput.value.trim();
  const videoQuality = parseInt(videoQualitySelect.value);
  
  if (videoName) {
    const url = `${coordinatorUrl}?name=${encodeURIComponent(videoName)}&quality=${videoQuality}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.status === 404) {
      window.alert('404 file not found');
    } else if (response.ok) {
      const serverList = await response.json();
      const serverData = serverList[0];
      const path = serverData.location;
      const videoUrl = `${path}`;
      loadSource(videoUrl);
    } else {
      window.alert(`Error processing request. Status:${response.status}`);
    }
  } else {
    window.alert('Please enter a valid video name');
  }
}
