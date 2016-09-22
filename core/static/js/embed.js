var progressive_events_embed = (function(){

    var self = {

        init: function(){

            self.scriptTag = document.currentScript;

            self.initAssets(function(){
                self.initMap();
                self.loadEvents();
            });

            return self;
        },

        initAssets: function(callback){
            var head = document.querySelector('head');
            var body = document.querySelector('body');

            if(!body.dataset.progressiveEventsEmbedInitialized){

                // add leaflet css and js
                var leafletCss = document.createElement('link');
                leafletCss.rel = 'stylesheet';
                leafletCss.href = 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css'
                head.appendChild(leafletCss);

                var leafletJS = document.createElement('script');
                leafletJS.type = 'text/javascript';
                leafletJS.src = 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js';
                leafletJS.setAttribute('id', 'leaflet-js');
                head.appendChild(leafletJS);

                body.dataset.progressiveEventsEmbedInitialized = "true";
            
            } else {

                leafletJS = document.getElementById('leaflet-js');

            }

            var oldOnload = leafletJS.onload;

            leafletJS.onload = function(){
                if(oldOnload){
                    oldOnload();
                }
                callback();
            }
        },

        createId: function(filters){

            var base = 'progressive-events-map';
            if(filters){
                return base + '-' + filters.replace(/\W+/, '-');
            }

            return base;

        },

        initMap: function(){

            self.filters = self.scriptTag.dataset.filters;

            // init map.
            self.mapElement = document.createElement('div');

            var mapId = self.createId(self.filters);
            self.mapElement.setAttribute('id', mapId);

            // arbitrary
            self.mapElement.setAttribute('style', 'min-height: 300px; width: 100%;');

            self.scriptTag.parentNode.insertBefore(self.mapElement, self.scriptTag.nextSibling);

            self.map = L.map(self.mapElement.getAttribute('id'), {
                scrollWheelZoom: false
            });

            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(self.map);

            // add zip code search field?
            self.showSearch = self.scriptTag.dataset.search;

            if(self.showSearch){
                searchWrapper = document.createElement('div');
                searchLabel = document.createElement('label');
                searchLabel.innerHTML = "Filter Events by Zip Code:";
                self.searchField = document.createElement('input');
                self.searchField.setAttribute('placeholder', '90210');
                self.searchField.setAttribute('size', '5');
                self.searchField.setAttribute('style', 'margin-left: 0.5em; text-align: center; padding: 0 0.5em;');

                searchLabel.appendChild(self.searchField);
                searchWrapper.appendChild(searchLabel);

                self.scriptTag.parentNode.insertBefore(searchWrapper, self.scriptTag.nextSibling);

                // should be bound somewhere separately, but...
                self.searchField.addEventListener('keyup', self.handleZipSearch);

            }

        },

        handleZipSearch: function(e){

            if(typeof self.clearEventsTimeout !== 'undefined'){
                clearTimeout(self.clearEventsTimeout);
            }

            if(e.which == 13 || e.target.value.length >= 5){

                self.clearEventsTimeout = setTimeout(function(){

                    if(e.which == 13 && e.target.value.length == 0){
                        self.filters = self.scriptTag.dataset.filters;
                    } else {
                        self.filters = (self.filters.replace(/address=[^&]+/, "") + "&address=" + e.target.value).replace(/&+/, '&');
                        self.filters = (self.filters.replace(/distance=[^&]+/, "") + "&distance=" + 5).replace(/&+/, '&');
                    }
                    self.clearEvents();
                    self.loadEvents();
                }, 300);
            }

        },

        queryfyJSON: function(blob){

            var keys = Object.keys(blob);

            if(keys.length === 0){
                return '';
            }

            return keys.map(function(key) {
                        return encodeURIComponent(key) + '=' +
                            encodeURIComponent(blob[key]);
                    }).join('&');

        },

        clearEvents: function(){
            self.map.removeLayer(self.markerGroup);
        },

        loadEvents: function(){

            var points = [];

            var populatePoints = function(events){

                for(var i = 0; i < events.length; i++){

                    var event = events[i];

                    points.push(L.marker([event.venue.point.y, event.venue.point.x])
                            // todo: need some way to decouple this better.
                            // could be passed in as a data-* attribute, maybe?
                            .bindPopup(`<h4>${event.title}</h4>
                                        <p><a href="https://www.google.com/maps/place/${encodeURIComponent(event.venue.address)}%2C+${encodeURIComponent(event.venue.city)}%2C+${encodeURIComponent(event.venue.state)}+${encodeURIComponent(event.venue.zipcode)}" target="_blank"><b>${event.venue.title}</b><br /><span class="text-muted">${event.venue.address}, ${event.venue.city}</span></a></p>
                                        <p>${event.description}</p>
                                        <p><a href="${event.url}" target="_blank">${event.url}</a></p>`));

                }

                self.markerGroup = L.featureGroup(points);
                self.markerGroup.addTo(self.map);
                if(points.length > 1){
                    self.map.fitBounds(self.markerGroup.getBounds().pad(0.2));
                } else {
                    self.map.setView(L.latLng(points[0]._latlng.lat, points[0]._latlng.lng), 13);
                }

            };

            var embedLookup = new XMLHttpRequest();
            // todo: better suss out environments
            embedLookup.open('GET', 'http://www.progressiveevents.org/api/1/events?' + self.filters);
            embedLookup.send(null);
            embedLookup.onreadystatechange = function(){
                var DONE = 4, OK = 200;
                if(embedLookup.readyState == DONE && embedLookup.status == OK){
                    var response = JSON.parse(embedLookup.responseText);
                    if(response.length){
                        populatePoints(response);
                    }
                }
            }

        }

    };

    return self.init();


})();