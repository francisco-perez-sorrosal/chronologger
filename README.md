# Chronologger

Time utilities for Python<sup>[1](#footnote1)</sup>

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

from chronologger import Timer, TimeUnit, root_timer


# Example of decorator: This should report ~100ms each time that is called
@Timer(name="Foo method!", unit=TimeUnit.ms, simple_log=True)
def foo():
    time.sleep(0.1)


def main():
    # Example of explicit timer: This should report ~100ms
    timer = Timer("Individual Timer", unit=TimeUnit.ms).start()
    time.sleep(0.1)
    timer.stop()

    # Example of explicit context timer: This should report ~1s
    with Timer(name="Test Loop!", unit=TimeUnit.s, simple_log=True) as timer:
        for i in range(5):
            time.sleep(0.1)  # e.g. simulate IO
            foo()
            timer.mark("i_{}".format(i))


if __name__ == "__main__":
    root_timer.label("   STARTING!!!")
    main()
    root_timer.label("   PRINTING TIME")
    root_timer.print()

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

---

<a name="footnote1">1</a>: Inspired by the blog post [Python Timer Functions: Three Ways to Monitor Your Code](https://realpython.com/python-timer/) by Geir Arne Hjelle 