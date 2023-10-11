import sys
sys.path.insert(0,'/Users/xuzigong/xu/git/time_converter')
from time_converter import Time
from pytest import approx, raises
import datetime as dt
import numpy as np
lunarday = 1
a = Time((1, dt.time(0,0)), 'ce4lst').to('dt')
print(a)
print('last one')

ce4lst = Time((3, dt.time(8, 30)), 'ce4lst').to('dt')

print(ce4lst)
print('first one')