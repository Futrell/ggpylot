# Here we establish the conversions from Python objects to R objects and from 
# R objects to Python objects (i.e., R ggplot objects to the GGPlot python
# object, also defined here). 
#
# The conversions here have to be activated by calling activate().
#
import tempfile
from .rpy2interface import robjects, ggplot2, pandas2ri, grdevices

def sequence_to_r_vector(lst, c=robjects.r['c']):
    return c(*lst)

PY2RI_CONVERSIONS = {
    list : sequence_to_r_vector,
    tuple : sequence_to_r_vector,
}

def activate_py2ri():
    pandas2ri.activate()

    old_py2ri_with_pandas_activated = robjects.conversion.py2ri

    def my_py2ri(pyobj):
        convert_fn = PY2RI_CONVERSIONS.get(type(pyobj))
        if convert_fn is not None:
            return convert_fn(pyobj)
        else:
            return old_py2ri_with_pandas_activated(pyobj)

    robjects.conversion.py2ri = my_py2ri

def activate_ri2ro():
    old_ri2ro = robjects.conversion.ri2ro

    def ggplot2_conversion(robj):
        pyobj = old_ri2ro(robj)

        try:
            rcls = pyobj.rclass
        except AttributeError:
            return pyobj
        
        if rcls is not None and 'gg' in rcls:
            pyobj = GGPlot(pyobj)
        return pyobj

    robjects.conversion.ri2ro = ggplot2_conversion

def activate():
    activate_py2ri()
    activate_ri2ro()

###########################################################
#####                GGPLOT OBJECT                    #####
###########################################################

class GGPlot(robjects.RObject):
    """ A Grammar of Graphics Plot

    GGPlot instances can be added to one an other in order to construct the
    final plot. Call the plot() method of the resulting object to see the
    plot.

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

    def __repr_svg_(self, width=6, height=4):
        # Hack with a temp file (use buffer later?)
        fn = tempfile.NamedTemporaryFile(mode='wb', suffix='.svg',
                                         delete=False)
        fn.close()
        grdevices.svg(fn.name, width=width, height=height)
        self.plot()
        grdevices.dev_off()
        import io
        with io.OpenWrapper(fn.name, mode='rb') as data:
           res = data.read().decode('utf-8') # really?
        return res

    # svg images in IPython notebooks interfere with one another. So I'm
    # making this a private method for now.
    def _svg(width=6, height=4, self=plot):
        """ Build an Ipython "Image" (requires iPython). """
        return Image(self._repr_svg_(width=width, height=height), embed=True)

    def png(width=700, height=500, self=plot):
        """ Build an Ipython "Image" (requires iPython). """
        return Image(self._repr_png_(width=width, height=height), embed=True)
