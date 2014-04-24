from rpy2 import robjects
from rpy2.robjects import pandas2ri

grdevices = robjects.packages.importr('grDevices')
ggplot2 = robjects.packages.importr('ggplot2') 
