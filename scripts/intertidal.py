from bathydem import data

import pandas as pd
import ee

region = 'tuvalu'
df = pd.read_csv(r"D:\bathydem\bathyDEM\use-cases\bbox.csv")
bb = df[df.name == region]
xx, XX = bb.minx.values[0],bb.maxx.values[0]
yy, YY = bb.miny.values[0],bb.maxy.values[0]
bounds = ee.Geometry.Rectangle([
    bb.minx.values[0],bb.miny.values[0],
    bb.maxx.values[0],bb.maxy.values[0]])

bathydem = data.data()
img = bathydem.intertidal(
    timeperiod = ee.Filter.date('2021-01-01', '2022-01-01'),
    bounds = bounds,
    scale = 30)

import geemap
Map = geemap.Map(center=((yy+YY)/2, (xx+XX)/2), zoom=7);
Map.addLayer(img)

img.unitScale(0.1, 0.9).getDownloadURL({'name': f'test_{region}', 'scale': 30,
                    'region': bounds, 'filePerBand': False,
                    'format': 'GEO_TIFF'})
