
# Box annotator

Simple webservice for image annotation using bounding boxes, for multiclass object detection.


## Requirements

```
pip install aiohttp
```


## Usage

```
python -m box.server -H 0.0.0.0 -P 80 -M ./metadata.json -I ./images/ -A ./annotation.json
```

Where `metadata.json` has the following format:

```json
{
    "classes" : [
        {
            "id": "foo",
            "label": "Foo",
            "color": "red"
        },
        {
            "id": "bar",
            "label": "Bar",
            "color": "blue"
        }
    ]
}
```

And `annotation.json`:

```json
{"name":"dummy.jpg","boxes":[{"x":10,"y":20,"width":50,"height":20}]}
{"name":"screenshot.jpg","boxes":[{"x":25.5,"y":2,"width":100,"height":100}]}
{"name":"screenshot.jpg","boxes":[{"x":25.5,"y":2,"width":100,"height":100},{"x":200,"y":100,"width":16,"height":42}]}
```

Note that only the last entry for a given image is considered.

As for now, only `.jpg` files are supported.
