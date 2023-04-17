project_name = 'tuvalu'

## bbox
import pandas as pd

df = pd.read_csv('..//use-cases//bbox.csv')
coords = df[df.name == 'project_name']

yy, YY = coords.miny.values[0], coords.maxy.values[0]
xx, XX = coords.maxy.values[0], coords.maxx.values[0]

import datetime, geemap, ee

from eepackages import tiler
from dateutil.relativedelta import *

Map = geemap.Map(center=((yy+YY)/2, (xx+XX)/2), zoom=11)

import hydrafloods as hf
import ee, geemap
from eepackages import assets

ee.Initialize()

start = "2020-10-01"
end = "2022-10-01"
region = ee.Geometry.Rectangle([xx,yy,XX,YY])

assetsLoc = 'users/robynsimingwee/ee-react/'

def getNDWI(img):
    ndwi = img.addBands(
        img.normalizedDifference(['green', 'swir']).select('nd').rename('mndwi')
        )
    return ndwi

col = assets.getMostlyCleanImages(
    assets.getImages(
    region,
    {   'resample': False,
        'scale': 30,
        'missions': ['L4', 'L5', 'L8', 'L9', 'S2'],
        'cloudMask': True,
        'filter': ee.Filter.date(start, end),
        'filterMaskedFraction': 0.9,
    }
    ),
    region,
    {
    'percentile': 90,
    'qualityBand': 'blue'
    }
).map(lambda f: f.clip(region)).map(getNDWI)

print(col.size().getInfo())

def applyOtsu(img):
    return hf.edge_otsu(
        img,
        region=region,
        band='mndwi',
        thresh_no_data=-0.2,
        # edge_buffer=300,
        invert=True
    )

def getInunFreq(collection):
    sum = collection.sum()
    count = collection.count()
    freq = sum.divide(count)

    return freq

frequency = getInunFreq(col.map(applyOtsu))
Map.addLayer(frequency); Map


water_viz = {
    "min":0,
    "max":1,
    "palette":"silver,navy",
    "region":region,
    "dimensions":2000
}





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
