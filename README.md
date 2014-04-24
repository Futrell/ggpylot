ggpylot
=======

ggplot2 interface in Python via rpy2

Requirements
------------

* You need to have the latest version of `R` installed and the `ggplot2` package installed inside R.
* `pandas`
* The latest `rpy2`

Example
-------
```python
from ggpylot import *
p = ggplot(mtcars, aes(x='mpg', y='qsec', colour='factor(cyl)')) + geom_point()
p.plot()
```
(PLOT HERE)

**To close the window, you must do this:**
```python
dev_off()
```
Or else bad things will happen! (I'm working on fixing this.)

Installation
------------
```
python setup.py build
python setup.py install
```

Goals
-----

1. I want to be able to use R's `ggplot2` package from Python without making the user explicitly deal with R. 
2. The Python interface should be very similar to the underlying R interface
and to the interface in the yhat `ggplot` project.
3. To the greatest extent possible, automatic compability with updated 
versions of `ggplot2`. 
4. It should work in IPython notebooks.



Previous projects along these lines
-----------------------------------

I will be building on these things.

1. `rpy2`'s interface to `ggplot2`

The `rpy2` interface to `ggplot2` attempts to align the universe of R ggplot objects with Python objects connected to underlying R objects. This is a good idea but it is hard to keep it up to date as the underlying R package changes. For instance, the interface of `rpy2`'s `ggplot2` is already out of date. 

2. Yhat's `ggplot` module

This is an attempt to recreate ggplot on the basis of `matplotlib`. This is an
admirable project: it is probably the way to go in the long run. But right now the python `ggplot` lacks some of the functionality of R's `ggplot2`, and I find the defaults in the python `ggplot` to not be as good as the defaults in R. I do think that is the way of the future though, so I'm going to try to make the interface here compatible with the yhat `ggplot` package.


The Approach Here
-----------------

All we need is a thin layer over R's `ggplot2` library as imported with `rpy2`'s `importr` function, and some ad-hoc fixes for weird stuff that arises. We also need some customized object conversion. Shouldn't be hard, right?
