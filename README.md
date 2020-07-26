# dl-router
router of download URLs

currently designed for app folder to be mapped into a usgi container.
see sample launch script
`launch_redirect.sh`

expects `userdata.csv` in app folder.. map as needed.

run local
```
cd app
export FLASK_APP=main
python -m flask run --host 0.0.0.0 --port 5000
```

## API

`/status`
meant for simplee healtcheck.  returns 200 OK

`/reload`
Flushes cache and reloads userdata file.  Return JSON of what new userdata is

