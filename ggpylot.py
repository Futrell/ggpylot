""" ggpylot: Python interface to ggplot2 via rpy2. 

==Goals==

1. I want to be able to use R's ggplot package from Python without ever having 
to make the user explicitly deal with R. 
2. The Python interface should be very similar to the underlying R interface. 
3. It should work in IPython notebooks.

Bonus: Easily or automatically extensible to keep up with updates to the R
package.

==Previous projects along these lines== 

I will be building on these things.

1. Rpy2's interface to ggplot2

The rpy2 interface to ggplot attempts to align the universe of R ggplot 
objects with Python objects connected to underlying R objects. This is a good 
idea but it is hard to keep it up to date as the underlying R package changes.
The interface of rpy2's ggplot2 is already out of date. 

2. Yhat's ggplot module

This is an attempt to recreate ggplot on the basis of matplotlib. I wish those
fellows well: that is probably the way to go in the long run. But right now
the python ggplot lacks some of the functionality of R's ggplot2, and I find
the defaults in the python ggplot to not be as good as the defaults in R. I do
think that is the way of the future though, so I'm going to try to make the
interface here compatible with the yhat ggplot package. 

==The Approach==

All we need is a thin layer over R's ggplot2 library as imported with rpy2's
importr function, and some ad-hoc fixes for weird stuff that arises. We also
need some customized object conversion. 

"""
# TODO
# Figure out facet_grid problems
#   1. 'cyl' not found
#   2. weird closure thing.
# Figure out source of segfaults. Patch.
# Fix order-dependence
# Documentation for patched functions

import tempfile

from rpy2 import robjects
from rpy2.robjects import pandas2ri

grdevices = robjects.packages.importr('grDevices')
ggplot2 = robjects.packages.importr('ggplot2')


###########################################################
#####                 CONVERSIONS                     #####
###########################################################

pandas2ri.activate()

_old_py2ri_with_pandas_activated = robjects.conversion.py2ri

def _sequence_to_r_vector(lst, c=robjects.r['c']):
    return c(*lst)

_py2ri_conversions = {
    list : _sequence_to_r_vector,
    tuple : _sequence_to_r_vector,
    }

def _my_py2ri(pyobj):
    convert_fn = _py2ri_conversions.get(type(pyobj))
    if convert_fn is not None:
        return convert_fn(pyobj)
    else:
        return _old_py2ri_with_pandas_activated(pyobj)

robjects.conversion.py2ri = _my_py2ri    


_old_ri2py = robjects.conversion.ri2py

def _ggplot2_conversion(robj):

    pyobj = _old_ri2py(robj)

    rcls = pyobj.rclass
    if rcls is robjects.NULL:
       rcls = (None, )

    if 'gg' in rcls:
       pyobj = GGPlot(pyobj)

    return pyobj

robjects.conversion.ri2py = _ggplot2_conversion    


###########################################################
#####                GGPLOT OBJECT                    #####
###########################################################

class GGPlot(robjects.RObject):
    """ A Grammar of Graphics Plot.
    
    GGPlot instances can be added to one an other in order to construct
    the final plot (the method `__add__()` is implemented).

    """
    _rprint = ggplot2._env['print.ggplot']
    _add = ggplot2._env['%+%']
    
    def plot(self, vp=robjects.constants.NULL):
        self._rprint(self, vp=vp)

    def __add__(self, obj):
        res = self._add(self, obj)
        if res.rclass[0] != 'gg':
            raise ValueError("Added object did not give a ggplot result "
                            + "(get class '%s')." % res.rclass[0])
        return self.__class__(res)

    def __radd__(self, obj):
        return self.__add__(obj)

    def _repr_png_(self, width=700, height=500): 
        # Hack with a temp file (use buffer later?)
        fn = tempfile.NamedTemporaryFile(mode='wb', suffix='.png',
                                         delete=False)
        fn.close()
        grdevices.png(fn.name, width=width, height=height)
        self.plot()
        grdevices.dev_off()
        import io
        with io.OpenWrapper(fn.name, mode='rb') as data:
           res = data.read()
        return res

    def _repr_svg_(self, width=6, height=4): 
        # Hack with a temp file (use buffer later?)
        fn = tempfile.NamedTemporaryFile(mode='wb', suffix='.svg',
                                         delete=False)
        fn.close()
        grdevices.svg(fn.name, width=width, height=height)
        self.plot()
        grdevices.dev_off()
        import io
        with io.OpenWrapper(fn.name, mode='rb') as data:
           res = data.read().decode('utf-8')
        return res

    def svg(width=6, height=4, self=plot):
        """ Build an Ipython "Image" (requires iPython). """
        return Image(self._repr_svg_(width=width, height=height), embed=True)

    def png(width=700, height=500, self=plot):
        """ Build an Ipython "Image" (requires iPython). """
        return Image(self._repr_png_(width=width, height=height), embed=True)


###########################################################
#####         FROM THE R PACKAGE IMPORT *             #####
###########################################################

def _inject_into_module_namespace(key, value):
    globals()[key] = value

def _inject_ggplot_functions(ggplot_package):
    for key, value in ggplot_package.__dict__.iteritems():
        if isinstance(value, robjects.functions.SignatureTranslatedFunction):
            _inject_into_module_namespace(key, value)

_inject_ggplot_functions(ggplot2)


###########################################################
#####              PATCHES AND HACKS                  #####
###########################################################

# aes_string doesn't seem to accept positional arguments. I don't know why. 
# Here is an ad-hoc solution:
_old_aes_string = aes_string
def aes_string(x, y=None, **kwds): 
    if y is None:
        return _old_aes_string(x=x, **kwds)
    else:
        return _old_aes_string(x=x, y=y, **kwds)

# aes by itself is basically unusable in Python. Also, yhat's ggplot thing 
# uses aes with the interface of aes_string. So let's just do this:
aes = aes_string 

# if you close the plot normally, you get a segmentation fault. To avoid this
# you have to call grdevices.dev_off(). This is a pain to type and easy to 
# forget, so to make it easier I just make dev_off() available in the module.
dev_off = grdevices.dev_off

