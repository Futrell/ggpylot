import numpy as np
import pandas as pd

from ggpylot import *


p = ggplot(mtcars, aes('mpg', 'qsec')) + geom_point(colour='steelblue') \
  + scale_x_continuous(breaks=[10,20,30], labels=["horrible", "ok", "awesome"])
p.plot()
dev_off()

meat_lng = pd.melt(meat, id_vars=['date'])
p = ggplot(aes(x='date', y='value'), data=meat_lng)
x = p + geom_point() + stat_smooth(colour="red") + facet_wrap("variable")
x.plot()
dev_off()

p = ggplot(aes(x='price'), data=diamonds)
x = p + geom_histogram() + facet_wrap("cut")
x.plot()
dev_off()

p = ggplot(aes(x='date', y='beef'), data=meat) + geom_line() + theme_bw() \
	+ stat_smooth()
p.plot()
dev_off()

df = pd.DataFrame({
    'x': ['a', 'b', 'c', 'a'],
    'y': [3, 2, 1, 2],
    'fill': np.random.random(4)
})
p = ggplot(aes(x='x', y='y', fill='fill'), data=df) + geom_tile() \
    + xlab('X Label') \
    + ylab('Y Label') \
    + ggtitle('This is geom_tile!\n')

p.plot()
dev_off()

random_walk1 = pd.DataFrame({
  "x": np.arange(100),
  "y": np.cumsum(np.random.choice([-1, 1], 100))
})
random_walk2 = pd.DataFrame({
  "x": np.arange(100),
  "y": np.cumsum(np.random.choice([-1, 1], 100))
})
p = ggplot(aes(x='x', y='y'), data=random_walk1) + geom_step() + \
    geom_step(aes(x='x', y='y'), data=random_walk2)
p.plot()
dev_off()


p = ggplot(diamonds, aes(x='price'))
x = p + geom_density() + facet_grid("cut", "clarity")
x.plot()
dev_off()

p = ggplot(diamonds, aes(x='price'))
x = p + geom_density() + facet_grid("cut ~ clarity")
x.plot()
dev_off()

p = ggplot(aes(x='wt', y='mpg'), data=mtcars)
x = p + geom_point() + facet_grid('cyl', 'gear', scales='free_y')
x.plot()
dev_off()

p = ggplot(mtcars, aes('mpg', 'wt', colour='factor(cyl)')) + geom_point()
p.plot()
dev_off()

x = p + facet_grid(None, 'cyl', scales='free')
x.plot()
dev_off()

x = p + facet_grid('. ~ cyl', scales='free')
x.plot()
dev_off()

x = p + facet_grid(y='cyl', scales='free') 
x.plot()
dev_off()

x = p + facet_grid('cyl', scales='free') + stat_smooth()
x.plot()
dev_off()

p = ggplot(diamonds, aes('clarity', fill='clarity')) + geom_bar(width=1) + coord_polar(theta='x')
p.plot()
dev_off()

meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
p = ggplot(aes(x='value', colour='variable', fill='variable'), data=meat_lng) + geom_density(alpha=.3)
p.plot()
dev_off()

print("OK")
