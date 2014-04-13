""" ggpylot: Python interface to ggplot2 via rpy2. 

Example:

p = ggplot(mtcars, aes('mpg', 'qsec')) + geom_point(colour='steelblue')
p.plot() # a beautiful plot appears
dev_off() # YOU MUST CLOSE THE PLOT WINDOW THIS WAY! Or else!!!

Known issues:
* if you close the plot without calling dev_off(), you'll get a segfault (!).
* ggplot has to be the first function in the chain.
* facet_grid doesn't work (but facet_wrap does).

"""
# TODO
# Figure out facet_grid problems: How to represent formulae?
#   1. 'cyl' not found
#   2. weird closure thing.
#   3. how to do the facet argument of qplot?
# Does qplot work? 
# Figure out how to call dev_off() automatically to avoid segfaults.
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
    """ A Grammar of Graphics Plot
    
    GGPlot instances can be added to one an other in order to construct
    the final plot. Call the plot() method to see the plot. 

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
def aes_string(x, y=None, **kwds): 
    if y is None:
        return ggplot2.aes_string(x=x, **kwds)
    else:
        return ggplot2.aes_string(x=x, y=y, **kwds)

# aes by itself is basically unusable in Python. Also, yhat's ggplot thing 
# uses aes with the interface of aes_string. So let's just do this:
aes = aes_string 

# if you close the plot normally, you get a segmentation fault. To avoid this
# you have to call grdevices.dev_off(). This is a pain to type and easy to 
# forget, so to make it easier I just make dev_off() available in the module.
dev_off = grdevices.dev_off

# facet_grid in R uses formulas, which have no equivalent in Python. So I'll
# adopt the yhat's syntax: the first two arguments to facet_grid are x and y
# corresponding to the formula x ~ y. However unlike yhat's facet_grid, this
# one should be able to take all the arguments that R's does. 
def facet_grid(x=None, y=None, **kwds):
    # ok, we'll have to actually build the R formula
    formula = robjects.Formula("{x} ~ {y}".format(x='.' if x is None else x,
                                                  y='.' if y is None else y))
    return ggplot2.facet_grid(formula, **kwds)



