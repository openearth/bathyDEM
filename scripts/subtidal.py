project_name = 'tuvalu'

## bbox
df = pd.read_csv('..//use-cases//bbox.csv')
coords = df[df.name == 'project_name']

yy, YY = coords.miny.values[0], coords.maxy.values[0]
xx, XX = coords.maxy.values[0], coords.maxx.values[0]

#import geopandas as gpd
#from shapely.geometry import Polygon
import datetime
import pandas as pd
#polygeom = Polygon([(xx,yy), (xx,YY), (XX,YY), (XX,yy), (xx,yy)])
#poly = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygeom])

import geemap, ee

from eepackages.applications.bathymetry import Bathymetry
from eepackages import tiler
from dateutil.relativedelta import *

#%%
Map = geemap.Map(center=((yy+YY)/2, (xx+XX)/2), zoom=11)

# make rolling mean of 3 months for every month
start = '2018-10-01' # October 2018, start of ICE-SAT2
end = '2019-01-01' #'2022-07-01'

interval = 1 # composite interval [months]
length = 24 # composite length [months]

# image timeframes
def startstopdate(start_date, stop_date, compo_int, compo_len):
    sdate = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    edate = datetime.datetime.strptime(stop_date,'%Y-%m-%d')
    window_length = int((edate.year-sdate.year)*12+(edate.month-sdate.month))
    startrangedates = pd.date_range(start_date, freq='%sMS'%(compo_int), periods=int((window_length/compo_int))).strftime('%Y-%m-%d').tolist()
    endrangedates = pd.date_range((sdate+relativedelta(months=compo_len)).strftime('%Y-%m-%d'), freq='%sMS'%(compo_int), periods=int((window_length/compo_int))).strftime('%Y-%m-%d').tolist()
    return startrangedates, endrangedates

tstart, tend = startstopdate(
    start, end, interval, length)

# %%
sdb = Bathymetry()
scale = 30
image_list = []
bounds = ee.Geometry.Polygon([(xx,yy), (xx,YY), (XX,YY), (XX,yy), (xx,yy)])

img = sdb.compute_inverse_depth(
    bounds=bounds,
    start=tstart[1],
    stop=tend[1],
    scale=scale,
    missions=['S2', 'L8'],
    filter_masked=True,
    skip_neighborhood_search=False,
)#.clip(bounds)


'''
for ts, te in zip(tstart, tend):
    image = sdb.compute_inverse_depth(
        bounds=bounds,
        start=ts,
        stop=te,
        scale=scale,
        missions=['S2','L9', 'L8'],
        filter_masked=True,
        skip_neighborhood_search=False,
    )#.clip(bounds)
    
    image_list.append(image)
    
    datename = f'{ts}_{te}'
    print(datename)
    print(image.getDownloadURL({
    'name': f'{project_name}_{datename}',
    'scale': scale,
    'region': bounds,
    'filePerBand': False
    }))
    print(image)
'''
# %%
