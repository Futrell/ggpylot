from rpy2 import robjects
from rpy2.robjects import packages
from rpy2.robjects import pandas2ri

grdevices = packages.importr('grDevices')
ggplot2 = packages.importr('ggplot2') 
