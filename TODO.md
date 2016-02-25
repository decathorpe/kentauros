# TODO items for kentauros

- check internet connection before running code requiring internet access:

```python3
import urllib2

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False
```

- ```package.__init__()```: make sure no hyphen is in source/version

- mock: use lockfile for waiting for running builds to finish?

- allow variables in package.conf and substitute
 - ```$(VERSION)```, ```$(NAME)```, etc.

- bzr: allow lightweight checkouts (conf/bzr/shallow=true)
- construct: sources do not neccessarily exist, calling source.rev() doesn't work then

