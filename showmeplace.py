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
from concurrent import futures
import sys


MAPBOX_TOKEN = 'XXX'
MAPBOX_TILESET_ID = 'mapbox.satellite'
TILES_URL = 'https://api.tiles.mapbox.com/v4/' + MAPBOX_TILESET_ID + '/{z}/{x}/{y}.png?access_token=' + MAPBOX_TOKEN
PARALLEL_THREADS_NUM = 4
OVERPASS_SERVER = 'https://maps.mail.ru/osm/tools/overpass/api/interpreter'


def _get_sat_img(lat, lon, name: str, pbar=None):
    filename = str(name)+'.jpg'

    if pbar:
        pbar.update(1)

    if os.path.exists(filename):
        print(f'Satellite image {filename} already exists!')
        return False

    # workaround for old png images
    png_filename = str(name) + '.png'
    if os.path.exists(png_filename):
        img = Image.open(png_filename)
        rgb_im = img.convert('RGB')
        print(f'Converting {filename} to {png_filename}...')
        rgb_im.save(filename)
        os.remove(png_filename)
        return False

    url = f'https://www.instantstreetview.com/@{lat},{lon},-132.4h,5p,1z'
    # url = f'https://www.google.com/maps/@{lat},{lon},17.5z'
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

    return True


def get_sat_img(lat, lon, name: str, pbar=None):
    try:
        return _get_sat_img(lat, lon, name, pbar)
    except Exception as e:
        print(f'Error: {str(e)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='showmeplace.py',
        description='ShowMePlace',
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--overpass-request', action='store_true', default=False)
    group.add_argument('--overpass-request-file', type=str)
    group.add_argument('--overpass-results-file', type=str)

    parser.add_argument('--no-ways', action='store_true', default=False)
    parser.add_argument('--generate-overpass-files', type=str, help='Coords in format lat1,lon1,lat2,lon2')

    args = parser.parse_args()

    if args.generate_overpass_files:
        with open(args.overpass_request_file) as f:
                text = f.read()
        print('Loaded requests...')
        if not '{{bbox}}' in text:
            print('Text of request should include {{bbox}} pseudovariable!')
            sys.exit(1)

        # 24.806681353851964,-126.5185546875,53.4357192066942,-65.3466796875
        coords = list(map(float, args.generate_overpass_files.split(',')))
        print(coords)
        api = overpy.Overpass(url=OVERPASS_SERVER)

        step = 20
        delta_x = (coords[2] - coords[0]) / step
        delta_y = (coords[3] - coords[1]) / step

        all_coords = []
        for i in range(step):
            for j in range(step):
                new_coords = [
                    coords[0]+i*delta_x,
                    coords[1]+j*delta_y,
                    coords[0]+(i+1)*delta_x,
                    coords[1]+(j+1)*delta_y,
                ]
                all_coords.append(new_coords)

        print(f'Total areas: {len(all_coords)}')

        # try to run request for the first area
        new_text = text.replace('{{bbox}}', ','.join(map(str, all_coords[0])))
        print(new_text)

        result = api.query(new_text)

        for i, c in enumerate(all_coords):
            new_text = text.replace('{{bbox}}', ','.join(map(str, all_coords[i])))
            filename = args.overpass_request_file+f'_{str(i)}'
            with open(filename, 'w') as f:
                f.write(new_text)
            print(f'Write {filename}')

        sys.exit(0)

    if args.overpass_results_file:
        print('Loading coords from Overpass results file...')
        coords_file = json.load(open(args.overpass_results_file))
        coords = coords_file['elements']

        img_args = []
        for c in tqdm.tqdm(coords):
            if args.no_ways and not 'lat' in c:
                continue
            try:
                lat = c.get('lat', c['geometry'][0]['lat'])
                lon = c.get('lon', c['geometry'][0]['lon'])
                name = str(c['id'])
                img_args.append((lat, lon, name))
                # get_sat_img(lat, lon, name)
            except Exception as e:
                print(f'Error while trying to get coords: {str(e)}')

    else:  # if overpass
        api = overpy.Overpass(url=OVERPASS_SERVER, max_retry_count=5)
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
            print(f'Processing file {args.overpass_request_file}...')
            with open(args.overpass_request_file) as f:
                text = f.read()

        print('Making request to Overpass API, please, wait...')

        result = api.query(text)
        print(f'Found: {len(result.nodes)} nodes, {len(result.ways)} ways, {len(result.relations)} relations')

        img_args = []
        print('Processing nodes...')
        for c in tqdm.tqdm(result.nodes):
            # get_sat_img(c.lat, c.lon, c.id)
            img_args.append((c.lat, c.lon, c.id))

        if not args.no_ways:
            print('Processing ways...')
            for c in tqdm.tqdm(result.ways):
                nodes = c.get_nodes(resolve_missing=True)
                img_args.append((float(nodes[0].lat), float(nodes[0].lon), c.id))
                # get_sat_img(float(nodes[0].lat), float(nodes[0].lon), c.id)

    future_test_results = []
    # run
    pbar = tqdm.tqdm(total=len(img_args))
    with futures.ThreadPoolExecutor(max_workers=PARALLEL_THREADS_NUM) as executor:
        future_test_results = [ executor.submit(get_sat_img, *a, pbar) for a in img_args ]

    for _ in future_test_results:
        pass
