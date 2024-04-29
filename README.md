# ShowMePlace

This tool shows satellite images for certain coordinates (latitude and longitude) by Overpass API request / raw response

# Instructions
0. Install Python 3.
1. Create a mapbox account here: www.mapbox.com. 
2. Once logged in, scroll down to Default Public Token. Copy it! You will need it in the `shomewplace.py` file
3. Make sure you have downloaded and installed GeckoDriver in your computer in program or bin folder. You can get it here: https://github.com/mozilla/geckodriver/releases
4. Run the showmeplace.py file

You can use other satellite image providers (example in the file `shomewplace.py`).
But in some places there may not be detailed images. In this case, try reducing the `max_zoom` parameter.

## Docker

```bash
docker build . -t showmeplace
docker run -it -v ./output:/showmeplace/output showmeplace ./showmeplace.py --overpass-request
```

# Theory

- [OSINT/GEOINT - Investigating and geolocating #2 - Overpass Turbo](https://haax.fr/en/writeups/osint-geoint/osint-flight-volume2-overpassturbo/)
- [Overpass Turbo and Night GEOINT](https://www.youtube.com/watch?v=h-_Z7xHGEh4)

# Usage

The main value of the tool is the ability to do batch checks for big regions, but you can do simple request also.

## Simple execution without params

You must copy the prepared request in **Overpass => Export => Request** panel (without `{{variables}}`).

```sh
$ ./showmeplace.py --overpass-request
Paste Overpass API request text, then enter END to run
[out:json][timeout:800];
nwr["addr:housenumber"="1832"](44.80230124552821,-93.52729797363281,45.22025894300122,-92.7252960205078);
out center;
END

Making request to Overpass API...
...
```

> [!WARNING]
> add the `center` argument to the `out` statement. This will speed up data processing and place the object in the center of the image.

## Simple execution without params from file

Also you can use a file:

```sh
$ ./showmeplace.py --overpass-request-file request.txt

Making request to Overpass API....
Found: 0 nodes, 20 ways, 0 relations
Processing nodes...
0it [00:00, ?it/s]
Processing ways...
Saving 44.9733591, -92.7328901 to 242000245.jpg, check place in https://www.google.com/maps/@44.9733591,-92.7328901,17.5z
...
```

## Execution of raw json request

You can use raw Overpass API from Overpass => Export => Data => raw

```sh
$ ./showmeplace.py --overpass-results-file test.json
Loading coords from Overpass results file...
Satellite image 88081666.jpg already exists!
Saving 44.9733591, -92.7328901 to 242000245.jpg, check place in https://www.google.com/maps/@44.9733591,-92.7328901,17.5z
...
```

## Batch processing mode (Use it for big territory scanning!)

The idea of a batch processing mode: split big territory for search into small parts (step*step, see source code) and run overpass search for each part.

1. Put request to some txt file.

```sh
$ cat batch.txt
[out:json][timeout:800];
(
  nwr["power"="tower"]["design"="barrel"]["material"="steel"]["structure"="tubular"]({{bbox}});
)->.tower;

(
  nwr(around.tower:100)["highway"="stop"];
)->.sign;

out center geom;
```

2. Generate N files for the bounding box from the request file batch.txt. You can copy bounding box coordinates from the Overpass interface by doing **Overpass => Export => Request**.

```sh
$ ./showmeplace.py --generate-overpass-files 24.806681353851964,-126.5185546875,53.4357192066942,-65.3466796875 --overpass-request-file batch.txt
```

Check that you have a lot of files with filenames of format `batch.txt_0`

3. Run batch processing (advanced: fix shell script on your own if the script is failing and you have to change mileage = step).

```
$ ./batch.sh
```

# Results

You'll get JPG files in the directory of the script with satellite images of target coordinates in the closest approximation 👍
