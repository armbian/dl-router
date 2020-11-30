# dl-router
router of download URLs

returns 302 to a mirror configured.  Can manually select region.

currently designed for app folder to be mapped into a usgi container.
see sample launch script
`launch_redirect.sh`

expects `userdata.csv` in app folder.. map as needed.
expects `mirrors.yaml` in app folder.. map as needed

run local
```
cd app
export FLASK_APP=main
python -m flask run --host 0.0.0.0 --port 5000
```

## configuration

_see [examples](examples/) folder_

### modes
`redirect` - standard redirect functionality
`dl_map` - will attempt to use contents of userdata.csv to map downloads
### mirrors
mirror target with trailing slash is placed in a yaml list under a key for regions
### yaml configured
```yaml
---
mode: dl_map
NA:
  - https://mirror1.example/images/
  - https://mirror2.example/images/
EU:
  - https://mirror3.example/weirdfolder/images/
  - https://mirror4.example/many/sub/folders/images/
````

## API

`/status`
meant for simplee healtcheck.  returns 200 OK

`/reload`
Flushes cache and reloads userdata file.  Return JSON of what new userdata is

`/mirrors`
Shows all mirrors configured

`/regions`
Shows all mirror regions

`/dl_map`
shows download map for images

`/region/REGIONCODE/`
will redirect to desired configurd regions:  
NA - north america
EU - Europe
AS - Asia (currently China)
