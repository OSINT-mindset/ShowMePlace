#! /usr/bin/env python3

# credits:
#Watipaso Mulwafu
#https://github.com/thewati
#https://medium.com/@watipasomulwafu

import folium
import io
import json
from PIL import Image
import tqdm
import os
import overpy
import argparse


MAPBOX_TOKEN = 'XXX'
MAPBOX_TILESET_ID = 'mapbox.satellite'
TILES_URL = 'https://api.tiles.mapbox.com/v4/' + MAPBOX_TILESET_ID + '/{z}/{x}/{y}.png?access_token=' + MAPBOX_TOKEN


def get_sat_img(lat, lon, name: str):
    filename = str(name)+'.jpg'

    if os.path.exists(filename):
        print(f'Satellite image {filename} already exists!')
        return

    # workaround for old png images
    png_filename = str(name) + '.png'
    if os.path.exists(png_filename):
        img = Image.open(png_filename)
        rgb_im = img.convert('RGB')
        print(f'Converting {filename} to {png_filename}...')
        rgb_im.save(filename)
        os.remove(png_filename)
        return

    url = f'https://www.google.com/maps/@{lat},{lon},17.5z'
    print(f'Saving {lat}, {lon} to {filename}, check place in {url}')
    print()

    m = folium.Map(
        location=[lat, lon],
        zoom_start=25,
        tiles=TILES_URL,
        attr='mapbox.com')

    marker = folium.map.FeatureGroup()
    marker.add_child(
        folium.features.CircleMarker(
            [lat, lon], radius = 5,
            color = 'red', fill_color = 'Red'
        )
    )
    m.add_child(marker)

    img_data = m._to_png(4)
    img = Image.open(io.BytesIO(img_data))
    rgb_im = img.convert('RGB')
    rgb_im.save(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='showmeplace.py',
        description='ShowMePlace',
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--overpass-request', action='store_true', default=False)
    group.add_argument('--overpass-request-file', type=str)
    group.add_argument('--overpass-results-file', type=str)

    args = parser.parse_args()

    if args.overpass_results_file:
        print('Loading coords from Overpass results file...')
        coords_file = json.load(open(args.overpass_results_file))
        coords = coords_file['elements']

        for c in tqdm.tqdm(coords):
            try:
                lat = c.get('lat', c['geometry'][0]['lat'])
                lon = c.get('lon', c['geometry'][0]['lon'])
                name = str(c['id'])
                get_sat_img(lat, lon, name)
            except Exception as e:
                print(f'Error while trying to get coords: {str(e)}')

    else:  # if overpass
        api = overpy.Overpass()
        text = ''

        if args.overpass_request:
            print('Paste Overpass API request text, then enter END to run')
            lines = []
            while True:
                line = input()
                if line != 'END':
                    lines.append(line)
                else:
                    break
            text = '\n'.join(lines)
        elif args.overpass_request_file:
            with open(args.overpass_request_file) as f:
                text = f.read()

        print('Making request to Overpass API....')

        result = api.query(text)
        print(f'Found: {len(result.nodes)} nodes, {len(result.ways)} ways, {len(result.relations)} relations')

        print('Processing nodes...')
        for c in tqdm.tqdm(result.nodes):
            get_sat_img(c.lat, c.lon, c.id)

        print('Processing ways...')
        for c in tqdm.tqdm(result.ways):
            nodes = c.get_nodes(resolve_missing=True)
            get_sat_img(float(nodes[0].lat), float(nodes[0].lon), c.id)
