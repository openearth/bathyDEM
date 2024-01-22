from bathydem import data
from urllib import request
import pandas as pd
import ee, os


# if credentials not saved, run using the following:
# ee.Authenticate(auth_mode='gcloud')

region = 'wadden'
composite = 6  # in months
window = 3      # in months

opath = os.path.join(
    r'D:\bathydem',
    region,
    'data')
if not os.path.exists(opath):
    os.makedirs(opath)

##########################################################################
df = pd.read_csv(r"..\use-cases\bbox.csv")
bb = df[df.name == region]

xx, XX = bb.minx.values[0],bb.maxx.values[0]
yy, YY = bb.miny.values[0],bb.maxy.values[0]
bounds = ee.Geometry.Rectangle([
    xx, yy, XX, YY])

import geemap
Map = geemap.Map(center=((yy+YY)/2, (xx+XX)/2), zoom=11)
Map.addLayer(bounds); Map

bathydem = data.data()
ts = '2019-10-01'
te = '2020-01-01'

i = ee.Date(ts)

def exporttiles(tile, image):
    tx = int(float(ee.Feature(tile).get('tx').getInfo()))
    ty = int(float(ee.Feature(tile).get('ty').getInfo()))
    zoom = int(float(ee.Feature(tile).get('zoom').getInfo()))
    
    if os.path.exists(
        os.path.join(
        opath, 
        f'{region}-bathydem-intertidal-{tx}x-{ty}y-{zoom}z-{istr}-c{composite}-w{window}.tiff'
    )):
        return
    else:
        url = image.clip(tile).getDownloadURL({
            'scale': 10,
            'region': ee.Feature(tile).geometry(),
            'filePerBand': False,
            'format': 'GEO_TIFF'        
        })
        try:
            r = request.urlretrieve(
                url, 
                os.path.join(
                opath,
                f'{region}-bathydem-intertidal-{tx}x-{ty}y-{zoom}z-{istr}-c{composite}-w{window}.tiff')
            )   
            return
        except:
            print(f'error for {istr}')
            return    

def exportimg(image):
    if os.path.exists(
        os.path.join(
        opath,
        f'{region}-bathydem-intertidal-{istr}.tiff'
        )
    ):
        return
    
    else:
        url = image.getDownloadURL({
            'scale': 10,
            'region': bounds,
            'filePerBand': False,
            'format': 'GEO_TIFF'        
        })
        try:
            r = request.urlretrieve(
                url, 
                os.path.join(
                opath,
                f'{region}-bathydem-intertidal-{istr}.tiff')
            )   
            return
        
        except:
            print(f'error for {istr}')
            return



#with tiling
while i.format('YYYY-MM-dd').getInfo() != te:
    
    istr = (i.format('YYYY-MM-dd').getInfo())
    print(istr)
    img = bathydem.intertidal(
        timeperiod = ee.Filter.date(
        i, i.advance(composite, 'month')),
        bounds = bounds,
        filterMaskedFraction = 0.9,
        scale = 10,
        waterindex = 'mndwi',
        applyCloudMask = False,
        )
    tiles = bathydem.exportAsTiles(bounds, 11)
    tsize = tiles.size().getInfo()
    print(f'total tiles: {tsize}')

    for t in range(tsize):
        tile = tiles.toList(tsize).get(t)
        exporttiles(tile, img)
    
    i = i.advance(window, 'month')