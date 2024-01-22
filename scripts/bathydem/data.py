import ee, requests
ee.Initialize()
from eepackages import tiler, assets
import hydrafloods as hf

ee.Authenticate(auth_mode='gcloud')

class data:
    '''
    The Data class allows a user to get bathymetry dataset for a given time period.
    For intertidal data, inundation frequency is derived using the Otsu thresholding method on either NDWI or MNDWI images.
    For subtidal data, the bathymetry proxy is currently derived from reflectance values that undergo a dark pixel correction. 
    Therefore, the values are not always between 0 - 1 for all images. Sub-tidal data is currently acquired using the sdb 
    (compute_inverse_depth method) from eepackages/bathymetry (Donchyts, 2018)
    '''

    def __init__(self):
        self.__help__ = '''
        bathydem uses openly-available satellite imagery to derive coastal bathymetry. bathydem uses two primary methods: (1) intertidal and (2) subtidal bathymetry.
        '''
        self.__version__ = "bathydem v0.1"
    

    def exportAsTiles(
            image, 
            bounds,
            zoomlevel = 11):
        tiles = tiler.get_tiles_for_geometry(
            bounds, zoomlevel)
        
        return tiles

    @staticmethod
    def ndwi(image):
        return image.addBands(
            image.normalizedDifference(['green', 'nir']).select('nd').rename('ndwi'))
        
    @staticmethod
    def mndwi(image):
        return image.addBands(
            image.normalizedDifference(['green', 'swir']).select('nd').rename('mndwi'))
    
    @staticmethod
    def apply_otsu(image, bounds, waterindex):
        return hf.edge_otsu(
            image,
            region=bounds,
            band=waterindex,
            thresh_no_data=-0.2,
            invert=True
        )

    def intertidal(
            self,
            timeperiod,
            bounds,
            scale: int = 30,
            missions: list = ['L4', 'L5', 'L8', 'L9', 'S2'],
            waterindex: str = 'mndwi',
            cloudMask: bool = True,
            applyCloudMask: bool = False,
            clip: bool = True,
            filterMaskedFraction: float = 0.9,
            maxPixels: int = 999999999999,
            ):
        
        self.scale = scale
        self.bounds = bounds
        self.type = 'intertidal'

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
        

        if clip == True:
            self.images = self.images.map(lambda f: f.clip(bounds))

        if waterindex == 'ndwi':
            self.waterindex = self.images.map(self.ndwi)
        elif waterindex == 'mndwi':
            self.waterindex = self.images.map(self.mndwi)

        # test mask
        if applyCloudMask:
                
            self.waterindex = self.waterindex.map(
                lambda f: f.updateMask(f.select('cloud'))
            )
        
        self.otsu = self.waterindex.map(
            lambda f: self.apply_otsu(f, bounds, waterindex))

        sum = self.otsu.sum()
        count = self.otsu.count()
        frequency = sum.divide(count).unmask()

        return frequency

