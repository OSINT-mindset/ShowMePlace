# ShowMePlace

This tool shows satellite images for certain coordinates (latitude and longitude) by Overpass API request / raw response

# Instructions
1. Create a mapbox account here: www.mapbox.com. 
2. Once logged in, scroll down to Default Public Token. Copy it! You will need it in the `shomewplace.py` file
3. Make sure you have downloaded and installed GeckoDriver in your computer. You can get it here: https://github.com/mozilla/geckodriver/releases
4. Store the GeckoDriver.exe file in your root folder
5. Run the ExtractSatelliteImages.py file. More explanations are in the comments

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

# Results

You get JPG files in the directory of script.