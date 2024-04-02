# Dans ce script, nous allons trier un jeux de données fourni: "exemple.dat"
import numpy as np
import math as mt
import pandas as pd
from matplotlib import pyplot
try:
    geoPandasImport = True
    import geopandas as gpd
    from osgeo import gdal
    import verde as vd
    import cartopy.crs as ccrs
    import rasterio
except:
    geoPandasImport = False
from scipy import stats
from pathlib import Path
plt = pyplot
# Lire le fichier de données
filename = Path("D:/Downloads/testData.dat")#"./EMI/data/EMI_Colonster_TP_Geophy.dat") # Changer le fichier a lire et le trajet ICI
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
geoData = geoData[geoData[['Cond.1[mS/m]','Cond.2[mS/m]','Cond.3[mS/m]']].ge(0).all(1)]
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
geoData[::100].to_csv(filenameSave, sep='\t', index=False)  # [::100] takes 1 row out of 100 (downsampling)
if geoPandasImport:
    filenameSaveSHP = filename.parents[0] / (filename.stem + '_sorted.shp')
    geoData.to_file(filenameSaveSHP)
    # bounds = np.round(geoData.total_bounds)
    # deltaX = round(bounds[2] - bounds[0])
    # deltaY = round(bounds[3] - bounds[1])
    # delta = 2.5
    # width = mt.ceil(deltaX/delta)
    # height = mt.ceil(deltaY/delta)
    # midPointX = (bounds[2] + bounds[0])/2
    # midPointY = (bounds[3] + bounds[1])/2
    # bounds = [midPointX-width/2*delta, 
    #           midPointY-height/2*delta,
    #           midPointX+width/2*delta,
    #           midPointY+height/2*delta]

    # raster = gdal.Grid(str('./EMI/data/Interpolated.tif'), 
    #                    str(filenameSaveSHP),
    #                    format="GTiff",
    #                    algorithm='invdist',
    #                    width=width,
    #                    height=height,
    #                    outputBounds=bounds,
    #                    zfield='Cond.3[mS/')
    # raster.FlushCache()

    ## Interpolation using VERDE (Fatiando A Terra)
    reducer = vd.BlockReduce(reduction=np.median, spacing=1) # 1m block-reduction
    coordinates = geoData.get_coordinates().to_numpy()
    coordinates, emiData = reducer.filter((coordinates[:,0], coordinates[:,1]),(geoData['Cond.1[mS/m]'], geoData['Inph.1[ppt]'], geoData['Cond.2[mS/m]'], geoData['Inph.2[ppt]'], geoData['Cond.3[mS/m]'], geoData['Inph.3[ppt]']))
    plt.figure()
    ax = plt.axes(projection=ccrs.epsg(31370))
    ax.set_title(f"{2.5} m Block Reduced Dataset")
    # Plot the bathymetry as colored circles.
    plt.scatter(coordinates[0], coordinates[1], c=emiData[0], s=5)
    plt.colorbar().set_label("Magnetic Anomaly [nT]")
    # Use a utility function to setup the tick labels and land feature
    # vd.datasets.setup_baja_bathymetry_map(ax)
    plt.show()

    coordinatesInit = coordinates
    for i, param in enumerate(['Cond1','Inph1','Cond2','Inph2','Cond3','Inph3']):
        spline = vd.Spline(mindist=5, damping=None)

        spline.fit(coordinatesInit, emiData[i])

        region=vd.pad_region(vd.get_region(coordinatesInit),5)

        grid_full = spline.grid(
            region=region,
            spacing=0.25,
            dims=["easting", "northing"],
            data_names="conductivity1",
        )

        grid = vd.distance_mask(
            coordinatesInit, maxdist=5, grid=grid_full)

        # Plot the grid and the original data points
        plt.figure(figsize=(8, 6))
        ax = plt.axes(projection=ccrs.epsg(31370))
        ax.set_title("Electrical Conductivity gridded with biharmonic spline")
        ax.plot(*coordinatesInit, ".k", markersize=1)
        tmp = grid.conductivity1.plot.pcolormesh(
            ax=ax, cmap="viridis", add_colorbar=False
        )
        plt.colorbar(tmp).set_label("Electrical conductivity [mS/m]")
        plt.show()

        grid = grid.to_array()
        interpEMI = grid.values
        coordinates = grid.coords

        # Define the Lambert 72 projection
        lambert_72 = {'init': 'EPSG:31370'}


        interpEMI = np.flipud(np.squeeze(interpEMI))

        with rasterio.open("D:/Downloads/test"+param+".tiff", #dir+resultsTif, 
                        'w', 
                        driver='GTiff', 
                        height=interpEMI.shape[0], 
                        width=interpEMI.shape[1], 
                        count=1,
                        dtype=interpEMI.dtype, 
                        crs=lambert_72, 
                        transform=rasterio.transform.from_bounds(region[0], region[2], region[1], region[3], interpEMI.shape[1], interpEMI.shape[0])
            ) as dst:
            dst.write(interpEMI, 1)
print('File saved successfully with the changes !')
