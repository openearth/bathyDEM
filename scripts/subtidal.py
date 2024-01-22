from eepackages.applications import bathymetry
from urllib import request
import pandas as pd
import ee, os
from bathydem import data

ee.Initialize()

region = 'tuvalu'
composite = 12  # in months
window = 3      # in months

opath = os.path.join(
    r'D:\bathydem',
    region,
    'data', 'subtidal')
if not os.path.exists(opath):
    os.makedirs(opath)

##########################################################################
df = pd.read_csv(r"..\use-cases\bbox.csv")
bb = df[df.name == region]

xx, XX = bb.minx.values[0], bb.maxx.values[0]
yy, YY = bb.miny.values[0], bb.maxy.values[0]
bounds = ee.Geometry.Rectangle([
    xx, yy, XX, YY])

import geemap
Map = geemap.Map(center=((yy+YY)/2, (xx+XX)/2), zoom=10);
Map.addLayer(bounds); Map

ts = '2020-07-01'
te = '2022-10-01'

i = ee.Date(ts)

def exporttiles(tile, image):
    tx = int(float(ee.Feature(tile).get('tx').getInfo()))
    ty = int(float(ee.Feature(tile).get('ty').getInfo()))
    zoom = int(float(ee.Feature(tile).get('zoom').getInfo()))
    
    if os.path.exists(
        os.path.join(
        opath, 
        f'{region}-bathydem-subtidal-{tx}x-{ty}y-{zoom}z-{istr}.tiff'
    )):
        return
    else:
        url = image.clip(tile).getDownloadURL({
            'scale': scale,
            'region': ee.Feature(tile).geometry(),
            'filePerBand': False,
            'format': 'GEO_TIFF'        
        })
        try:
            r = request.urlretrieve(
                url, 
                os.path.join(
                opath,
                f'{region}-bathydem-subtidal-{tx}x-{ty}y-{zoom}z-{istr}.tiff')
            )   
            return
        except:
            print(f'error for {istr}')
            return    

def exportimg(image):
    if os.path.exists(
        os.path.join(
        opath,
        f'{region}-bathydem-subtidal-{istr}.tiff'
        )
    ):
        return
    
    else:
        url = image.getDownloadURL({
            'scale': scale,
            'region': bounds,
            'filePerBand': False,
            'format': 'GEO_TIFF'        
        })
        try:
            r = request.urlretrieve(
                url, 
                os.path.join(
                opath,
                f'{region}-bathydem-subtidal-{istr}.tiff')
            )   
            return
        
        except:
            print(f'error for {istr}')
            return

sdb = bathymetry.Bathymetry()
scale = 10
bathydem = data.data()

#without tiling
while i.format('YYYY-MM-dd').getInfo() != te:
    
    istr = (i.format('YYYY-MM-dd').getInfo())
    print(istr)
    img = sdb.compute_inverse_depth(
        bounds = bounds,
        start = istr,
        stop = i.advance(composite, 'month'),
        scale = scale,
        missions = ['S2', 'L9', 'L8'],
        filter_masked = True,
        skip_neighborhood_search = False,
    ).clip(bounds)
    
    tiles = bathydem.exportAsTiles(bounds, 12)
    tsize = tiles.size().getInfo()

    for t in range(tsize):
        tile = tiles.toList(tsize).get(t)
        exporttiles(tile, img)
    # print(img.bandNames().getInfo())
    # exportimg(img)
    
    i = i.advance(window, 'month')