# Dans ce script, nous allons trier un jeux de données fourni: "exemple.dat"
import numpy as np
import math as mt
import pandas as pd
from matplotlib import pyplot
try:
    geoPandasImport = True
    import geopandas as gpd
    from osgeo import gdal
except:
    geoPandasImport = False
from scipy import stats
from pathlib import Path
# Lire le fichier de données
filename = Path("./EMI/data/EMI_Colonster_TP_Geophy.dat") # Changer le fichier a lire et le trajet ICI
data = pd.read_csv(filename, delimiter='\t', header=0, index_col=False)
if geoPandasImport:
    geoData = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.Longitude, data.Latitude, data.Altitude), crs='epsg:4326')
    geoData = geoData.to_crs('epsg:31370') # Convert to Lambert 72
else:
    geoData = data
nbInit = len(geoData.index)
print('Initial number of values: {}'.format(nbInit))
# Montrer les histograms initiaux:
hist = geoData.hist(column=['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]'])
pyplot.show(block=False)
# Supprimer les données non-physique (négatives) en utilisant la méthode "ge" (greater or equal) de pandas:
geoData = geoData[geoData[['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]']].ge(0).all(1)]
nbInit = len(geoData.index)
print('Number of physical values: {}'.format(nbInit))
# Montrer les histogrammes de chaque paramètre:
hist = geoData.hist(column=['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]'])
pyplot.show(block=False)
# On voit que les histograms ont des ranges beaucoup trop large. C'est du a la présence d'outliers.
# On peut les détecter simplement par mesure statistique (écart par rapport a la moyenne - z-score) par exemple
geoData = geoData[(np.abs(stats.zscore(geoData[['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]']]))<3).all(axis=1)]
nbInit = len(geoData.index)
print('Number of in-range values: {}'.format(nbInit))
# Vérifier visuellement que les données fausses soient bien enlevées:
hist = geoData.hist(column=['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]'])
pyplot.show()
# Sauver les données au format csv pour QGIS (séparateur=tabulation):
filenameSave = filename.parents[0] / (filename.stem + '_sorted' + filename.suffix)
geoData.to_csv(filenameSave, sep='\t', index=False)
if geoPandasImport:
    filenameSaveSHP = filename.parents[0] / (filename.stem + '_sorted.shp')
    geoData.to_file(filenameSaveSHP)
    bounds = np.round(geoData.total_bounds)
    deltaX = round(bounds[2] - bounds[0])
    deltaY = round(bounds[3] - bounds[1])
    delta = 2.5
    width = mt.ceil(deltaX/delta)
    height = mt.ceil(deltaY/delta)
    midPointX = (bounds[2] + bounds[0])/2
    midPointY = (bounds[3] + bounds[1])/2
    bounds = [midPointX-width/2*delta, 
              midPointY-height/2*delta,
              midPointX+width/2*delta,
              midPointY+height/2*delta]

    raster = gdal.Grid(str('./EMI/data/Interpolated.tif'), 
                       str(filenameSaveSHP),
                       format="GTiff",
                       algorithm='invdist',
                       width=width,
                       height=height,
                       outputBounds=bounds,
                       zfield='Cond.3[mS/')
    raster.FlushCache()
print('File saved successfully with the changes !')