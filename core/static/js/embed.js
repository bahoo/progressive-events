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
                return base + '-' + filters.replace(/\W+/g, '-');
            }

            return base;

        },

        initMap: function(){

            self.filters = self.scriptTag.dataset.filters;

            // init map.
            self.mapElement = document.createElement('div');

            self.mapId = self.createId(self.filters);
            self.mapElement.setAttribute('id', self.mapId);

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
                self.addZipSearch();
            }


            // show list itself?
            self.showList = self.scriptTag.dataset.showlist;
            if(self.showList){
                self.addList();
            }

        },

        addZipSearch: function(){

            searchWrapper = document.createElement('div');

            // zip code filter
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

            // distance filter
            distanceLabel = document.createElement('label');
            distanceLabel.setAttribute('style', 'margin-left: 1em;')
            distanceLabel.innerHTML = "Distance:";
            self.distanceField = document.createElement('select');
            self.distanceField.setAttribute('style', 'margin-left: 1em;')

            var distances = self.scriptTag.dataset.distances;
            if(distances){
                distances = JSON.parse(distances);
            } else {
                distances = [5, 10, 20, 50];                
            }
            var setDistance = self.filters.match(/distance=(\d+)/i);
            if(setDistance){
                setDistance = parseInt(setDistance[1]);
            } else {
                setDistance = 20;
            }
            
            if(distances.indexOf(setDistance) == -1){
                distances.push(setDistance);
            }

            var compareIntegers = function(a, b){
                return a-b;
            }

            distances = distances.sort(compareIntegers);

            for(var d in distances){
                var elem = document.createElement('option')
                elem.innerHTML = `${distances[d]} miles`;
                elem.setAttribute('value', distances[d]);
                if(distances[d] == setDistance){
                    elem.setAttribute('selected', 'selected');
                }
                self.distanceField.appendChild(elem);
            }

            distanceLabel.appendChild(self.distanceField);
            searchWrapper.appendChild(distanceLabel);

            // todo: set events
            self.distanceField.addEventListener('input', self.handleDistanceChange)
        },


        addList: function(){

            self.eventsList = document.createElement('div');
            self.eventsList.setAttribute('id', self.mapId + '-list');

            self.scriptTag.parentNode.insertBefore(self.eventsList, self.map.nextSibling);

        },

        handleDistanceChange: function(){

            self.filters = (self.filters.replace(/distance=[^&]+/gi, "") + "&distance=" + self.distanceField.options[self.distanceField.selectedIndex].value).replace(/&+/g, '&');
            self.clearEvents();
            self.loadEvents();

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
                        self.filters = (self.filters.replace(/address=[^&]+/gi, "") + "&address=" + e.target.value).replace(/&+/g, '&');
                        self.filters = (self.filters.replace(/distance=[^&]+/gi, "") + "&distance=" + self.distanceField.options[self.distanceField.selectedIndex].value).replace(/&+/g, '&');
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

        populatePoints: function(events){

            var points = [];

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

        },

        populateList: function(events){

            var fetchList = new XMLHttpRequest();
            // todo: better suss out environments
            fetchList.open('GET', 'http://www.progressiveevents.org/?' + self.filters);
            fetchList.send(null);
            fetchList.onreadystatechange = function(){
                var DONE = 4, OK = 200;
                if(fetchList.readyState == DONE && fetchList.status == OK){
                    var context = document.implementation.createHTMLDocument("");
                    // sooooo gross. so, so, so gross.
                    var pattern = /<body[^>]*>((.|[\n\r])*)<\/body>/im
                    var baseTag = document.createElement('base');
                    context.querySelector('body').innerHTML = pattern.exec(fetchList.responseText)[1];

                    var relativeLinks = context.querySelectorAll('.event-items a[href^="/"]');
                    for(var a = 0; a < relativeLinks.length; a++){
                        relativeLinks[a].setAttribute('href', 'http://www.progressiveevents.org' + relativeLinks[a].getAttribute('href'));
                    }

                    self.eventsList.innerHTML = context.querySelector('.event-items').innerHTML;
                }
            }

            

        },

        loadEvents: function(){

            var embedLookup = new XMLHttpRequest();
            // todo: better suss out environments
            embedLookup.open('GET', 'http://www.progressiveevents.org/api/1/events?' + self.filters);
            embedLookup.setRequestHeader('Accept', 'application/json');
            embedLookup.send(null);
            embedLookup.onreadystatechange = function(){
                var DONE = 4, OK = 200;
                if(embedLookup.readyState == DONE && embedLookup.status == OK){
                    var response = JSON.parse(embedLookup.responseText);
                    if(response.length){
                        self.populatePoints(response);
                        if(self.showList){
                            self.populateList(response)
                        }
                    }
                }
            }

        }

    };

    return self.init();


})();