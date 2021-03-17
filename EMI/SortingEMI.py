# Dans ce script, nous allons trier un jeux de données fourni: "exemple.dat"
import numpy as np
import pandas as pd
from matplotlib import pyplot
from scipy import stats
from pathlib import Path
# Lire le fichier de données
filename = Path('./data/exemple.dat') # Changer le fichier a lire et le trajet ICI
data = pd.read_csv(filename, delimiter='\t', header=0, index_col=False)
nbInit = len(data.index)
print('Initial number of values: {}'.format(nbInit))
# Montrer les histograms initiaux:
hist = data.hist(column=['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]'])
pyplot.show()
# Supprimer les données non-physique (négatives) en utilisant la méthode "ge" (greater or equal) de pandas:
data = data[data[['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]']].ge(0).all(1)]
nbInit = len(data.index)
print('Number of physical values: {}'.format(nbInit))
# Montrer les histogrammes de chaque paramètre:
hist = data.hist(column=['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]'])
pyplot.show()
# On voit que les histograms ont des ranges beaucoup trop large. C'est du a la présence d'outliers.
# On peut les détecter simplement par mesure statistique (écart par rapport a la moyenne - z-score) par exemple
data = data[(np.abs(stats.zscore(data[['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]']]))<3).all(axis=1)]
nbInit = len(data.index)
print('Number of in-range values: {}'.format(nbInit))
# Vérifier visuellement que les données fausses soient bien enlevées:
hist = data.hist(column=['Cond.1[mS/m]','Inph.1[ppt]','Cond.2[mS/m]','Inph.2[ppt]','Cond.3[mS/m]','Inph.3[ppt]'])
pyplot.show()
# Sauver les données au format csv pour QGIS (séparateur=tabulation):
filenameSave = filename.parents[0] / (filename.stem + '_sorted' + filename.suffix)
data.to_csv(filenameSave, sep='\t', index=False)
print('File saved successfully with the changes !')