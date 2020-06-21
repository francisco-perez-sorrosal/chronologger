# Chronologger

Time utilities for Python

[![Build Status](https://travis-ci.org/francisco-perez-sorrosal/chronologger.svg?branch=master)](https://travis-ci.org/francisco-perez-sorrosal/chronologger)
[![Coverage Status](https://coveralls.io/repos/github/francisco-perez-sorrosal/chronologger/badge.svg?branch=master)](https://coveralls.io/github/francisco-perez-sorrosal/chronologger?branch=master)

# Requirements
Requirements: Python >= 3.6

Use the *Makefile* targets to access most of the functionality: `make install-dev`, `make dbuild`, `make drun`, `make dstart`...

Otherwise...

# Install
```shell script
pip install git+https://git@github.com/francisco-perez-sorrosal/chronologger.git
```

# Run the Simple Example

## Docker

Clone the project...
```shell script
git clone git@github.com:francisco-perez-sorrosal/chronologger.git
```

and then...
```shell script
cd chronologger
docker build -f Dockerfile.example -t chronologger-example .
docker run -itd --name chronologger-example chronologger-example:latest
docker exec -it chronologger-example python simple_example.py 
```

## Local

After installing the package, just clone the project and execute example with:

```shell script
git clone git@github.com:francisco-perez-sorrosal/chronologger.git ; cd chronologger
python examples/simple_example.py
``` 

or open your python environment/IDE and execute:

```python
import time

from chronologger import Chronologger, TimeUnit

@Chronologger(name="Foo method!", unit=TimeUnit.ms, simple_log_msgs=False, log_when_exiting_context=True)
def foo():
    time.sleep(0.1)

with Chronologger(name="Test Loop!", unit=TimeUnit.s,
                  simple_log_msgs=False, log_when_exiting_context=True).start() as timer:
    for i in range(3):
        time.sleep(0.1)  # e.g. simulate IO
        foo()
        timer.mark("i_{}".format(i))
```

# Development

Install: 

```shell script
make install-dev
```

Use other commands in the Makefile for extra functionality.

## Docker

```shell script
make dbuild
make drun
make dtests
```

Use other commands in the Makefile for extra functionality.

### IDE (PyCharm) Docker Interpreter
Once you create the Docker image with `make dbuild` you can specify the `chronologger-dev:latest` image as a Ptyhon
Docker interpreter in IntelliJ/PyCharm for example.
