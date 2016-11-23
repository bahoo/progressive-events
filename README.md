# progressive-events

Decisions get made by people who show up. Progressive Events is here to tell you about where you should show up. A civic / activist / politically-themed hub for events in your area.

## Prerequisites

`git`, `virtualenvwrapper`, and `pip`


## Installation

    git clone git@github.com:bahoo/progressive-events.git
    cd progressive-events
    mkvirtualenv progressiveevents
    pip install -r requirements.txt


## Requirements

Things you'll need:
   

1. Postgres database: https://wiki.postgresql.org/wiki/Detailed_installation_guides#MacOS
2. The GDAL library (http://www.gdal.org/), `brew install GDAL`
3. The Postgres/GIS library, `brew install postgis`
4. A unique, secure Django `SECRET_KEY` http://www.miniwebtool.com/django-secret-key-generator/
5. A Google Maps API key (server side, for geocoding) https://console.developers.google.com/flows/enableapi?apiid=maps_backend,geocoding_backend,directions_backend,distance_matrix_backend,elevation_backend&keyType=CLIENT_SIDE&reusekey=true
6. Optionally, Redis: http://jasdeep.ca/2012/05/installing-redis-on-mac-os-x/


## Configuration

Then set some variables in your `.env` file:

    echo "DATABASE_URL=postgis://username:password@localhost:5432/database" > .env
    echo "SECRET_KEY=[ Secret Key goes here ]" > .env
    echo "GOOGLE_MAPS_API_KEY=[ Google API Key goes here ]" > .env
    echo "REDIS_URL=[ Redis URL goes here ]" > .env
