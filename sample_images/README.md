Put demo images here, for example:

```text
sample_images/desk.jpg
sample_images/person.jpg
```

Then pass the image path to the adapter:

```powershell
python openclaw_adapter.py "Check whether there is a cup in the image" --image sample_images\desk.jpg
```

Included demo images:

```text
bus_people.jpg     # Ultralytics sample image, useful for person/bus detection
zidane_people.jpg  # Ultralytics sample image, useful for person detection
```

Example commands:

```powershell
python openclaw_adapter.py "Check whether there is a person in the image" --image sample_images\bus_people.jpg
python openclaw_adapter.py "Check whether there is a bus in the image" --image sample_images\bus_people.jpg
python openclaw_adapter.py "Check whether there is a person in the image" --image sample_images\zidane_people.jpg
```
