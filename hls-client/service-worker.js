let serverUrls = [];
let currentServerIndex = 0;
const coordinatorUrl = 'http://127.0.0.1:5000/servers/';

function getNextServerUrl() {
  if (serverUrls.length !== 0) {
    const serverUrl = serverUrls[currentServerIndex];
    currentServerIndex = (currentServerIndex + 1) % serverUrls.length;
    return serverUrl;
  }
}

async function handleServersRequest(request) {
  const modifiedRequest = new Request(request.url, {
    method: request.method,
    headers: {
      'Content-Type': 'application/json',
    },
    mode: 'cors',
    credentials: 'same-origin',
    redirect: 'follow',
    referrer: 'no-referrer'
  });
  console.log("Service worker modified:", modifiedRequest);

  return fetch(modifiedRequest).then(async response => {

    if (response.ok) {
      const clonedResponse = response.clone();
      const serverList = await clonedResponse.json();
      serverUrls = serverList.map(server => `http://${server.address}:${server.port}`);
      currentServerIndex = 0;
    }

    return response;
  });
}

function rerouteUrl(originalUrl) {
  const serverUrl = getNextServerUrl();
  console.log(serverUrls, currentServerIndex, serverUrl);
  return originalUrl.replace(/^(https?:\/\/[^\/]+)(\/.*)?$/, serverUrl + '$2');
}

self.addEventListener('fetch', event => {
  event.respondWith((async () => {
    const request = event.request;
    console.log("Service worker recived:", request);

    if (request.url.startsWith(coordinatorUrl) && request.method === 'GET') {
      // Pobranie parametrów z query string
      const url = new URL(request.url);
      const name = url.searchParams.get('name');
      const quality = url.searchParams.get('quality');

      if (!name || !quality) {
        return new Response('Invalid parameters', { status: 400, statusText: 'Bad Request' });
      }

      return handleServersRequest(request);
    } else if (request.url.endsWith('.m3u8') || request.url.endsWith('.ts')) {
      const newUrl = rerouteUrl(request.url);
      const modifiedRequest = new Request(newUrl, {
        method: request.method,
        headers: request.headers,
        mode: 'cors',
        credentials: 'same-origin',
        redirect: 'follow',
        referrer: 'no-referrer',
      });
      console.log("Service worker modified:", modifiedRequest);

      return fetch(modifiedRequest);
    } else {
      return fetch(request);
    }
  })());
});

