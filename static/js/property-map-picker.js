/**
 * Selector de ubicación para formularios de propiedad.
 * Guarda lat/lng en los inputs del formulario (se envían con POST al guardar).
 */
(function (w) {
  'use strict';

  function init(options) {
    if (typeof L === 'undefined') {
      console.warn('[TL map picker] Leaflet no cargado');
      return;
    }

    var mapEl = document.getElementById(options.mapId);
    var latIn = document.querySelector(options.latInput);
    var lngIn = document.querySelector(options.lngInput);
    if (!mapEl || !latIn || !lngIn) return;

    var defaultLat = options.defaultLat != null ? options.defaultLat : 20.5888;
    var defaultLng = options.defaultLng != null ? options.defaultLng : -100.3899;
    var zoom = options.defaultZoom != null ? options.defaultZoom : 13;

    var lat = parseFloat(latIn.value);
    var lng = parseFloat(lngIn.value);
    if (isNaN(lat) || isNaN(lng)) {
      lat = defaultLat;
      lng = defaultLng;
    }

    var tiles = (w.TL_MAP_TILES && typeof w.TL_MAP_TILES === 'object') ? w.TL_MAP_TILES : {};
    var tileUrl = tiles.url || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    var tileAttribution = tiles.attribution || '&copy; OpenStreetMap contributors';
    var tileSubdomains = tiles.subdomains || 'abc';
    var tileMaxZoom = Number(tiles.maxZoom || 19);

    var map = L.map(mapEl).setView([lat, lng], zoom);
    L.tileLayer(tileUrl, {
      attribution: tileAttribution,
      subdomains: tileSubdomains,
      maxZoom: tileMaxZoom
    }).addTo(map);

    var marker = L.marker([lat, lng], { draggable: true }).addTo(map);

    function setInputs(ll) {
      latIn.value = ll.lat.toFixed(6);
      lngIn.value = ll.lng.toFixed(6);
    }

    marker.on('dragend', function (e) {
      setInputs(e.target.getLatLng());
    });

    map.on('click', function (e) {
      marker.setLatLng(e.latlng);
      setInputs(e.latlng);
    });

    if (latIn.value && lngIn.value && !isNaN(parseFloat(latIn.value)) && !isNaN(parseFloat(lngIn.value))) {
      var ll0 = L.latLng(parseFloat(latIn.value), parseFloat(lngIn.value));
      marker.setLatLng(ll0);
      map.setView(ll0, 16);
    }

    var statusEl = options.statusEl ? document.querySelector(options.statusEl) : null;
    var geocodeBtn = options.geocodeBtn ? document.getElementById(options.geocodeBtn) : null;

    if (geocodeBtn && typeof options.getQuery === 'function') {
      geocodeBtn.addEventListener('click', function () {
        var q = options.getQuery();
        if (!q || !String(q).trim()) {
          if (statusEl) statusEl.textContent = 'Completa dirección, ciudad y estado primero.';
          return;
        }
        if (statusEl) statusEl.textContent = 'Buscando ubicación...';
        var url =
          'https://nominatim.openstreetmap.org/search?format=json&q=' +
          encodeURIComponent(q) +
          '&limit=1';
        fetch(url, { headers: { 'Accept-Language': 'es,en' } })
          .then(function (r) {
            return r.json();
          })
          .then(function (data) {
            if (!data || !data.length) {
              if (statusEl) statusEl.textContent = 'No se encontró. Ajusta la dirección o coloca el pin a mano.';
              return;
            }
            var ll = L.latLng(parseFloat(data[0].lat), parseFloat(data[0].lon));
            marker.setLatLng(ll);
            map.setView(ll, 16);
            setInputs(ll);
            if (statusEl) statusEl.textContent = 'Listo: coordenadas actualizadas (se guardan al enviar el formulario).';
          })
          .catch(function () {
            if (statusEl) statusEl.textContent = 'Error al buscar. Intenta de nuevo o coloca el pin en el mapa.';
          });
      });
    }

    setTimeout(function () {
      map.invalidateSize();
    }, 400);
  }

  w.TLPropertyMapPicker = { init: init };
})(window);
