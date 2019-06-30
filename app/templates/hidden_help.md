# Hidden Help

## Disclaimer

Since the url for this area of my site can change for any reason and at any time,
I will be referring to the page as `/hidden` for the sake of continuity,
but whichever the url is under, the help page will always be at '/hidden/help', where '/hidden' is previously mentioned url.
the url can change at any time with a small change in a config file or anywhere else, so I cannot guarentee that it will stay the same.
I may even have it change every hour if I say so.

## Background

The API currently uses the Gelbooru API to request and it's CDN to serve images to you.
Beyond that, the formatting of the site (the cards) and the base64 behind it are all processed server side.
The small form built-in can be used to interact with the site's commands with ease, but only here will it specify what does what and what can be
expected given certain arguments.

## Arguments

### Basic Explanation

Arguments are specified in this format:

```http
/hidden?argument1=VALUE&argument2=VALUE
```

The first argument is prefixed with a `?` and the second and beyond are prefixed with a `&`.
A `=` symbol follows each argument and the Value for it is placed afterwards.
The value can be empty, the server *should* be able to process it fine, but to be on the safe side,
booleans (true or false values) should be `true` or `True` or `false` or `False`.

---

### Usage

#### `tags` parameter

##### Type

The `tags` parameter is a string.
It defaults to `trap` when not specified.

##### Description

The `tags` parameter specifies what you're searching for. Refer to Gelbooru to what tags are available.
For some basic guidance, here are the tags for SFW and probably not SFW stuff:

* `rating:safe` Probably SFW, but not always correct.

* `rating:questionable` Probably *not* SFW, but probably correct.

The chain multiple tags, instead of space character like most sites use, you would chain them without a space, and instead use a `+` character.

##### Example

*`/hidden?tags=rating:safe`
will load all images with the `rating:safe` tag.

*`/hidden?tags=rating:questionable+yuri`
will load all images with the `rating:questionable` and the `yuri` tag.

*`/hidden?tags=rating:safe+yuri`
will load all images with the `rating:safe` tag and the `yuri` tag.

---

#### `count` parameter

##### Type

The `count` parameter is a integer.
It defaults to `50` when not specified, or is `0` or is negative.
Floating point numbers will error, along with strings.
It's maxmimum value is `1000`.

##### Description

The `count` parameter specifies how many images will load on the page at once.
It is recommended you do not exceed `100`, as most images will not load past this.
When `base64` is enabled, count is automatically set back to `50` to stop server load, unless `showfull` is enabled, where it will be set to `25`.

##### Example

* `/hidden?count=50`
will load `50` images and display them.

* `/hidden?count=365`
will load `365` images

* `/hidden?count=889&base64=True`
will load `50` images using `base64` encoding.

---

#### `showfull` parameter

##### Type

The `showfull` parameter is a boolean.
As usual, it expects some form of `True`, `False`, `0`, or `1`.
The parameter is not case sensitive.
`showfull` defaults to `False` if not specified.

##### Description

The `showfull` parameter is very simple.
This requests that the page load with high quality images instead of the default thumbnail quality image.
The Gelbooru API provides multiple links for any given image, one of which is a link for the thumnbail.
The Gelbooru site staff prefer that sites like mine link to the thumbnail image, of which this parameter does. The thumnbail image is of significantly lower quality, but it lowers loading time for both you, as well as reduce load on the Gelbooru CDN. Out of respect for them, we ask that this parameter be kept on, as to view the full high quality version of the image, you need but click on the image itself.

##### Example

* `/hidden?showfull=True`
shows all images in high quality

* `/hidden?showfull=False`
shows all images in thumbnail quality

* `hidden/showfull=0&base64=True`
shows all images in thumnbnail quality using `base64` encoding

---

#### `showtags` parameter

##### Type

The `showtags` parameter is a boolean.
As usual, it expects some form of `True`, `False`, `0`, or `1`.
The parameter is not case sensitive.
`showtags` defaults to `False` if not specified.

##### Description

The `showtags` parameter is very simple, it shows all relevant tags for a specific image below, in the card's content box.

##### Example

* `/hidden?showtags=True`
will show tags for all images displayed
* `/hidden?showtags=0`
will not show tags for all images displayed
* `/hidden?showtags=1&count=39`
will show tags for all `39` images displayed.