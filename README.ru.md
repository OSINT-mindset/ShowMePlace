# ShowMePlace

Этот инструмент позволяет получать спутниковые снимки для определённых координат-результатов запроса к Overpass API (напрямую или через файл с ответом). 

# Как пользоваться
0. Установите себе Python 3.
1. Установите зависимости `pip install -r requirements.txt`
2. Зарегистрируйте аккаунт в провайдере спутниковых снимков: www.mapbox.com. 
3. Скопируйте свой личный Default Public Token. Его нужно указать в файле `shomewplace.py` для того, чтобы получать снимки.
4. Запустите файл `showmeplace.py`

Вы можете использовать других поставщиков спутниковых снимков (пример в файле `shomewplace.py`). Но в некоторых местах может не быть детальных снимков.

# Примеры использования

Запуск со вводом запроса Overpass прямо в командной строке:
```sh
$ ./showmeplace.py --overpass-request
Paste Overpass API request text, then enter END to run
[out:json][timeout:800];
(
  nwr["addr:housenumber"="1832"](44.80230124552821,-93.52729797363281,45.22025894300122,-92.7252960205078);
)->.house;

(.house;);

out center geom;
END

Making request to Overpass API...
...
```

> [!WARNING] 
> добавляйте в оператор `out` аргумент `center`. Это ускорит обработку данных и разместит объект по центру снимка

Можно использовать подготовленный файл с запросом из Overpasss Turbo (он не должен содержать переменных в двойных фигурных скобах, {{таких}}).
Пункт меню Overpass => Export => Request panel.

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

Также можно сохранить ответ на запрос из Overpass Turbo через Overpass => Export => Data => raw и использовать в скрипте:

```sh
$ ./showmeplace.py --overpass-results-file test.json
Loading coords from Overpass results file...
Satellite image 88081666.jpg already exists!
Saving 44.9733591, -92.7328901 to 242000245.jpg, check place in https://www.google.com/maps/@44.9733591,-92.7328901,17.5z
...
```

А для обработки больших территорий можно разбить их на части и сгенерировать запросы по каждую из них.

```sh
# создать N файлов по указанной координатами территории для файла с запросом batch.txt
$ ./showmeplace.py --generate-overpass-files 24.806681353851964,-126.5185546875,53.4357192066942,-65.3466796875 --overpass-request-file batch.txt

# файл с шаблоном запроса
$ cat batch.txt
[out:json][timeout:800];
(
  nwr["power"="tower"]["design"="barrel"]["material"="steel"]["structure"="tubular"]({{bbox}});
)->.tower;

(
  nwr(around.tower:100)["highway"="stop"];
)->.sign;

out center geom;

# запускаем пакетную обработку запросов (важно не забыть поправить переменную step в скрипте)
$ ./batch.sh
```

# Результаты

You get JPG files in the directory of script.
