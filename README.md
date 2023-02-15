# ShowMePlace

This tool shows satellite images for certain coordinates (latitude and longitude) by Overpass API request / raw response

# Instructions
0. Установите себе Python 3.
1. Create a mapbox account here: www.mapbox.com. 
2. Once logged in, scroll down to Default Public Token. Copy it! You will need it in the `shomewplace.py` file
3. Make sure you have downloaded and installed GeckoDriver in your computer in program or bin folder. You can get it here: https://github.com/mozilla/geckodriver/releases
4. Run the showmeplace.py file

# Usage

```sh
$ ./showmeplace.py --overpass-request
Paste Overpass API request text, then enter END to run
[out:json][timeout:800];
(
  nwr["addr:housenumber"="1832"](44.80230124552821,-93.52729797363281,45.22025894300122,-92.7252960205078);
)->.house;

(.house;);

out geom;
END

Making request to Overpass API...
...
```

You must copy prepared request in Overpass => Export => Request panel (without `{{variables}}`).

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

You can use raw Overpass API from Overpass => Export => Data => raw

```sh
$ ./showmeplace.py --overpass-results-file test.json
Loading coords from Overpass results file...
Satellite image 88081666.jpg already exists!
Saving 44.9733591, -92.7328901 to 242000245.jpg, check place in https://www.google.com/maps/@44.9733591,-92.7328901,17.5z
...
```

Batch processing mode: split big territory for search into small parts (step*step, see source code) and run overpass search for each part.

```sh
# generate N files for the bounding box from request file batch.txt
$ ./showmeplace.py --generate-overpass-files 24.806681353851964,-126.5185546875,53.4357192066942,-65.3466796875 --overpass-request-file batch.txt

# request template
$ cat batch.txt
[out:json][timeout:800];
(
  nwr["power"="tower"]["design"="barrel"]["material"="steel"]["structure"="tubular"]({{bbox}});
)->.tower;

(
  nwr(around.tower:100)["highway"="stop"];
)->.sign;

out geom;

# run batch processing (fix shell script if you changed step)
$ ./batch.sh
```

# Results

You get JPG files in the directory of script.
