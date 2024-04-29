#! /usr/bin/env python3

# credits:
#Watipaso Mulwafu
#https://github.com/thewati
#https://medium.com/@watipasomulwafu

import json
from PIL import Image
import tqdm
import os
import overpy
import argparse
from concurrent import futures
import sys
from staticmap import StaticMap, CircleMarker


MAPBOX_TOKEN = ''


class TileSet:
    def __init__(self, tiles_url, attr):
        self.tiles_url = tiles_url
        self.attr = attr


tilesets = [
    # you can add custom tiles. For example, uncomment this:
    # TileSet(
    #     'https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    #     'ESRI'
    # ),
    # TileSet(
    #     'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    #     'OSM',
    # ),
]

if MAPBOX_TOKEN != "":
    tilesets.append(TileSet(
        'https://api.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=' + MAPBOX_TOKEN,
        'Mapbox',
    ))

PARALLEL_THREADS_NUM = len(tilesets)
OVERPASS_SERVER = 'https://overpass-api.de/api/interpreter'


def _get_sat_img(lat, lon, name: str, obj_type: str, pbar=None, folder="", tileset: TileSet = None):
    filename = os.path.join(folder, obj_type + name + "_" + tileset.attr + '.jpg')

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

    m = StaticMap(1366, 768, 10, url_template=tileset.tiles_url, delay_between_retries=2)
    m.add_marker(CircleMarker((float(lon), float(lat)), 'red', 5))
    image = m.render()
    image.save(filename)

    return True


def get_sat_img(lat, lon, name, obj_type: str, tileset: TileSet, pbar=None, folder=""):
    try:
        _get_sat_img(lat, lon, str(name), obj_type, pbar, folder, tileset)
        return True
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

    parser.add_argument('--generate-overpass-files', type=str, help='Coords in format lat1,lon1,lat2,lon2')
    parser.add_argument('--output-folder', type=str, help='Folder for saving images', default='output')

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
                try:
                    line = input()
                except EOFError as e:
                    break
                if line != 'END':
                    lines.append(line)
                else:
                    break
            text = '\n'.join(lines)
        elif args.overpass_request_file:
            print(f'Processing file {args.overpass_request_file}...')
            with open(args.overpass_request_file) as f:
                text = f.read()

        if " center" not in text:
            print('WARN: The coordinates of ways and relations will be requested separately, which may take a long time.', file=sys.stderr)
            print('WARN: Add "center" to line with "out ... " in Overpass Query', file=sys.stderr)

        print('Making request to Overpass API, please, wait...')

        result = api.query(text)
        print(f'Found: {len(result.nodes)} nodes, {len(result.ways)} ways, {len(result.relations)} relations')

        img_args = []
        for c in tqdm.tqdm(result.nodes):
            img_args.append((c.lat, c.lon, c.id, "node"))

        print('Processing ways...')
        for c in tqdm.tqdm(result.ways):
            if c.center_lat is None:
                nodes = c.get_nodes(resolve_missing=True)
                img_args.append((float(nodes[0].lat), float(nodes[0].lon), c.id, "way"))
            else:
                img_args.append((float(c.center_lat), float(c.center_lon), c.id, "way"))

        print('Processing relations...')
        for c in tqdm.tqdm(result.relations):
            if c.center_lat is None:
                if isinstance(c.members[0], overpy.RelationWay):
                    node = c.members[0].resolve(resolve_missing=True).get_nodes(resolve_missing=True)[0]
                else:
                    node = c.members[0].resolve(resolve_missing=True)
                img_args.append((float(node.lat), float(node.lon), c.id, "rel"))
            else:
                img_args.append((float(c.center_lat), float(c.center_lon), c.id, "rel"))

    future_test_results = []
    # run
    pbar = tqdm.tqdm(total=len(img_args)*len(tilesets))
    with futures.ThreadPoolExecutor(max_workers=PARALLEL_THREADS_NUM) as executor:
        future_test_results = [executor.submit(get_sat_img, *a, t, pbar, args.output_folder)
                               for a in img_args
                               for t in tilesets]

    for _ in future_test_results:
        pass
