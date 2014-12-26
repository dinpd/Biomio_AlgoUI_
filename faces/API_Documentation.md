**This documentation is automatically generated.**

**Output schemas only represent `data` and not the full output; see output examples and the JSend specification.**

# /api/identiffy/?

    Content-Type: application/json

## POST
**Input Schema**
```json
{
    "required": [
        "image"
    ], 
    "type": "object", 
    "properties": {
        "image": {
            "media": {
                "type": "image/png", 
                "binaryEncoding": "base64"
            }, 
            "type": "string"
        }
    }
}
```

**Output Schema**
```json
{
    "type": "object", 
    "properties": {
        "distance": {
            "type": "number"
        }, 
        "face": {
            "required": [
                "x", 
                "y", 
                "width", 
                "height"
            ], 
            "type": "object", 
            "properties": {
                "y": {
                    "type": "number"
                }, 
                "x": {
                    "type": "number"
                }, 
                "height": {
                    "type": "number"
                }, 
                "width": {
                    "type": "number"
                }
            }
        }, 
        "label": {
            "type": "string"
        }
    }
}
```


**Notes**

Match an input image vs. faces in a recognizer's model (currently, only Fisher recognizer is available.)

"Distance": estimate of how bad the match is (the lower the better.)
"Label": UID, corresponded to the match
"Face": coordinates of the upper left corner, as well as width and height, of a detected face area

Empty JSON object is returned in case of no match



<br>
<br>

# /api/labels/\(?P\<label\>\[a\-zA\-Z0\-9\_\]\+\)/?$

    Content-Type: application/json

## GET
**Input Schema**
```json
null
```

**Output Schema**
```json
{
    "type": "object", 
    "properties": {
        "img_count": {
            "type": "number"
        }
    }
}
```


**Notes**

Provide a number of faces associated with a label



<br>
<br>

# /api/train/\(?P\<uid\>\[a\-zA\-Z0\-9\_\]\+\)/?$

    Content-Type: application/json

## POST
**Input Schema**
```json
{
    "required": [
        "images", 
        "count"
    ], 
    "type": "object", 
    "properties": {
        "count": {
            "type": "number"
        }, 
        "images": {
            "items": {
                "media": {
                    "type": "image/png", 
                    "binaryEncoding": "base64"
                }, 
                "type": "string"
            }, 
            "type": "array"
        }
    }
}
```

**Output Schema**
```json
{
    "required": [
        "count"
    ], 
    "type": "object", 
    "properties": {
        "count": {
            "type": "number"
        }
    }
}
```


**Notes**

Add a new user and/or new faces for the user. Training is triggered if number of faces is equal or exceed value of the input parameter "count."
Value of the output parameter "count" corresponds to a deficit of the faces after transaction.

"Images" is an array of base64 encoded PNG images.  Images, with no faces detected, are ignored in all the calculations, described above.



<br>
<br>

# /api/verify/\(?P\<uid\>\[a\-zA\-Z0\-9\_\]\+\)/?$

    Content-Type: application/json

## POST
**Input Schema**
```json
{
    "required": [
        "image"
    ], 
    "type": "object", 
    "properties": {
        "image": {
            "media": {
                "type": "image/png", 
                "binaryEncoding": "base64"
            }, 
            "type": "string"
        }
    }
}
```

**Output Schema**
```json
{
    "required": [
        "match"
    ], 
    "type": "object", 
    "properties": {
        "distance": {
            "type": "number"
        }, 
        "match": {
            "type": "bool"
        }
    }
}
```


**Notes**

Match an input image and UID vs. faces in a recognizer's model.


