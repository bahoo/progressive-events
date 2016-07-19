var progressive_events_embed = (function(){

    var self = {

        init: function(){
            self.initAssets(function(){
                self.initMap();
                self.loadEvents();
            });

            return self;
        },

        initAssets: function(callback){
            var head = document.querySelector('head');

            // add leaflet css and js
            var leafletCss = document.createElement('link');
            leafletCss.rel = 'stylesheet';
            leafletCss.href = 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css'
            head.appendChild(leafletCss);

            var leafletJS = document.createElement('script');
            leafletJS.type = 'text/javascript';
            leafletJS.src = 'http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js';
            head.appendChild(leafletJS);

            leafletJS.onload = callback;
        },

        initMap: function(){

            self.scriptTag = document.getElementById('progressive-events-embed');

            self.filters = self.scriptTag.dataset.filters;

            // init map.
            self.mapElement = document.createElement('div');
            self.mapElement.setAttribute('id', 'progressive-events-map');

            // arbitrary
            self.mapElement.style = 'min-height: 300px; width: 100%;';

            self.scriptTag.parentNode.insertBefore(self.mapElement, self.scriptTag.nextSibling);

            self.map = L.map(self.mapElement.getAttribute('id'), {
                scrollWheelZoom: false
            });

            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(self.map);

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

        loadEvents: function(){

            var points = [];

            var populatePoints = function(events){

                for(var i = 0; i < events.length; i++){

                    var event = events[i];

                    points.push(L.marker([event.venue.point.y, event.venue.point.x])
                            .bindPopup(`{% spaceless %}
                                        <h5>${event.title}</h5>
                                        {% if event.venue.address %}
                                            <p>
                                                <a href="https://www.google.com/maps/place/{{ event.venue.address|urlencode }}%2C+{{ event.venue.city|urlencode }}%2C+{{ event.venue.state|urlencode }}+{{ event.venue.zipcode|urlencode }}" target="_blank"><span class="glyphicon glyphicon-map-marker" style="margin-right: 0.33em;"></span><b>{{ event.venue.title }}</b><span class="text-muted" style="margin-left: 0.333em;">{{ event.venue.address }}, {{ event.venue.city }}</span></a>
                                            </p>
                                        {% endif %}
                                        {% if event.description %}
                                            <p>{{ event.description | linebreaksbr | safe }}</p>
                                        {% endif %}
                                        <p>
                                            {% if event.url %}
                                                <a href="{{ event.url }}" target="_blank" class="link"><span class="glyphicon glyphicon-link" style="margin-right: 0.33em;"></span>{{ event.url }}</a><br />
                                            {% endif %}
                                            <a href="#{{ event.title | slugify }}-{{ event.pk }}"><span class="glyphicon glyphicon-info-sign" style="margin-right: 0.33em"></span>Jump to listing</a>
                                        </p>{% endspaceless %}`));

                }

                var markerGroup = L.featureGroup(points);
                markerGroup.addTo(self.map);
                self.map.fitBounds(markerGroup.getBounds().pad(0.2));

            };

            var filters = self.filters;

            var embedLookup = new XMLHttpRequest();
            embedLookup.open('GET', 'http://localhost:8000/api/1/events' + location.search);
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