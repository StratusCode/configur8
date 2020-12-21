configur8
=========

Python configuration and validation library.

## Usage

This library has been developed to help manage and mitigate configuration issues
when deploying code.

An example:

```python
from configur8 import env

SECRET_KEY = env.str("SECRET_KEY")
NUM_WORKERS = env.int("NUM_WORKERS", "2")
DEBUG = env.bool("DEBUG", "false")
```

In the example above:
1. ``SECRET_KEY`` is a required environment variable - attempting execute the
   code without it defined will result in an exception. This is typically what
   you want so that apps and services don't start in an unintended state.
2. ``NUM_WORKERS`` will be parsed into an integer. If the env var is not
   defined, ``2`` will be used as a default. If a non integer value is parsed,
   an error will be raised.
3. ``DEBUG`` is a boolean with a default of ``False``. "Truthy" values can be
   used, e.g. "on", "1", etc.

Everything is designed to be type safe.

## Types of values supported

* String - ``env.str``
* Integer - ``env.int``
* Float - ``env.float``
* Boolean - ``env.bool``
* Url - ``env.url``
* Path - ``env.path``

Each type can support optional values and work with lists:

```python
from configur8 import env

ALLOWED_HOSTS = env.url.list("ALLOWED_HOSTS")
```

Given the environment:

```
ALLOWED_HOSTS=http://localhost,http://my-staging-server
```

The python value of ``ALLOWED_HOSTS`` would be:

```python
["http://localhost", "http://my-staging-server"]
```

## Boolean flags

Boolean values are supported. See ``configur8.env.BOOLEAN_TRUTHY_VALUES``:
* `true`
* `1`
* `on`
* `yes`
* `ok`

Will all result in a ``True`` Python value. Anything else will result in
``False``.

## Urls

These are augmented objects that have extra attributes in case you need them:

```python
from configur8 import env

# https://my-bucket.s3.us-west-2.amazonaws.com
bucket = env.url("S3_BUCKET_URL")

assert bucket.protocol == "https"
assert bucket.host == "my-bucket.s3.us-west-2.amazonaws.com"
```

There are a bunch more properties - see ``configur8.url.Url``.

## Paths

These are augmented objects that have extra attributes in case you need them:

```python
from configur8 import env

# /var/run/secrets/my-mounted-volume/my-secret
my_creds = env.path("SERVICE_CREDS").read()

# my_creds will hold the contents of the file in the env var
```

## Development

```shell
mkvirtualenv configur8 --python=`which python3`
make local
```

### Running tests

```shell
workon configur8
make test
```

### Publishing to PyPI

**NOTE** Replace `__VERSION__` with a semver identifier such as `0.9.3`

1. Ensure that you are on a clean master.
2. Update `version_info` in `src/configur8/__about__.py` to `__VERSION__`.
3. ```shell
   git add src/configur8/__about__.py
   git commit -m "Bump to __VERSION__"
   git tag v__VERSION__
   git push origin master --tags
4. Wait for CircleCI to succeed and publish the library to the private PyPI.
