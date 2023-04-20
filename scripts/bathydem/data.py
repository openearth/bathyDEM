import ee
from eepackages import tiler, assets
import hydrafloods as hf


ee.Initialize()

class data:
    '''
    The getdata class allows a user to get bathymetry dataset for a given time period.
    
    For inter-tidal data, inundation frequency is derived using the otsu thresholding method on either NDWI or MNDWI images.

    For sub-tidal data, the bathymetry proxy is currently derived reflectance values that undergoes a dark pixel correction. Therefore, the values are not always between 0 - 1 for all images. Sub-tidal data is currently 
    acquired using the sdb (compute_inverse_depth method) from eepackages/bathymetry (Donchyts, 2018)

    
    '''

    def __init__(self):
        self.__help__ = '''
        bathydem uses openly-available satellite imagery to derive coastal bathymetry. bathydem uses two primary methods: (1) intertidal and (2) subtidal bathymetry.
        '''
        self.__version__ = "bathydem v0.1"
    
    def export(self):
        # should have function to export individual images if possible
        pass
        
    def intertidal(
            self,
            timeperiod,
            bounds,
            scale: int = 30,
            missions: list = ['L4', 'L5', 'L8', 'L9', 'S2'],
            waterindex: str = 'mndwi',
            cloudMask: bool = True,
            clip: bool = True,
            filterMaskedFraction: float = 0.9,
            maxPixels: int = 999999999999,
            ):
        
        self.images = assets.getMostlyCleanImages(
            assets.getImages(
            bounds,
            {
            'resample': False,
            'scale': scale,
            'missions': missions,
            'cloudMask': cloudMask,
            'filter': timeperiod,
            'filterMaskedFraction': filterMaskedFraction,
            'maxPixels': maxPixels
            }),
            bounds,
            {
            'percentile': 98,
            'qualityBand': 'blue'
            })
        
        def ndwi(image: ee.Image):
            return image.addBands(
                image.normalizedDifference(['green', 'nir']).select('nd').rename('ndwi'))
        
        def mndwi(image: ee.Image):
            return image.addBands(
                image.normalizedDifference(['green', 'swir']).select('nd').rename('mndwi'))
        
        def applyOtsu(image, bounds, waterindex):
            return hf.edge_otsu(
                image,
                region = bounds,
                band = waterindex,
                thresh_no_data = -0.2,
                # edge_buffer=300,
                invert = True
                )
            
        if clip == True:
            self.images = self.images.map(lambda f: f.clip(bounds))

        if waterindex == 'ndwi':
            self.waterindex = self.images.map(ndwi)
        elif waterindex == 'mndwi':
            self.waterindex = self.images.map(mndwi)

        self.otsu = self.waterindex.map(
            lambda f: applyOtsu(f, bounds, waterindex))

        sum = self.otsu.sum()
        count = self.otsu.count()
        frequency = sum.divide(count)

        return frequency
        


        

# ff = data.intertidal(ee.Filter.date('2021-01-01', '2022-01-01'))
# ff.intertidal.scale()
import pandas as pd
region = 'bangladesh'
df = pd.read_csv(r"D:\bathydem\bathyDEM\use-cases\bbox.csv")
bb = df[df.name == region]
xx, XX = bb.minx.values[0],bb.maxx.values[0]
yy, YY = bb.miny.values[0],bb.maxy.values[0]
bounds = ee.Geometry.Rectangle([
    bb.minx.values[0],bb.miny.values[0],
    bb.maxx.values[0],bb.maxy.values[0]])

bathydem = data()
img = bathydem.intertidal(
    timeperiod = ee.Filter.date('2021-01-01', '2022-01-01'),
    bounds = bounds,
    scale = 1000)

import geemap
Map = geemap.Map(center=((yy+YY)/2, (xx+XX)/2), zoom=7);
Map.addLayer(img)