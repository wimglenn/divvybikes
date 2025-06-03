# Divvy Bikes

City Explorer is cool, but figuring out what are really Divvy bike stations and what are just public racks is not fun.
See https://community.bikeangels.com/discussions/bike-angels-general/please-remove-public-racks-from-the-city-explorer/3333 

This repository contains some tooling for rendering your City Explorer using the Google Maps API and removing those public racks.

Quickstart:

```
git clone git@github.com:wimglenn/divvybikes.git
cd divvybikes
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# get Lyft access token from browser cookies after signing in on divvybikes.com
# the access token should be placed at ~/.lyft_token

# (optional) get a Google Maps API token and place it at ~/.google_api_key

python3 -m divvybikes.render
```

The result should be something like this:

![Image](https://github.com/user-attachments/assets/8641b01f-677f-46d4-a9e7-352df715bf14)
