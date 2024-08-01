from fiona.drvsupport import supported_drivers
import geopandas as gpd
from os import path

from myModules import myExcept

################################################################################################
def readKmlFile(kmlFile, excludePoint=True):
    try:
        supported_drivers['KML'] = 'rw'
        gdf = gpd.read_file(path.abspath(kmlFile), driver='KML')
        if excludePoint:
            gdf = getGdfPolygonsLines(gdf)
    except:
        gdf = None
        myExcept.printExceptionTrace(limit=0)
    return gdf 

################################################################################################
def getGdfPolygonsLines(gdf):
    # return gdf[gdf['geometry'].apply(lambda x: isinstance(x, Polygon))]
    return gdf[(gdf.geometry.geom_type == 'Polygon') | (gdf.geometry.geom_type == 'LineString')]


