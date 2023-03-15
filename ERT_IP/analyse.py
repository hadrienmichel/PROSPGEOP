# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 13:46:42 2023

@author: tomde
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot
# Importer le jeu de données via pandas:
#   Si le jeux de données contient ERT et IP et que le jeu contient des estimations d'erreur,
#   les paramètres a entrée sont ceux utilisé ci-dessous.
data = pd.read_csv('C:/Users/tomde/dox/Prospection Geophysique/TP.2023/02.ERT/fichiers_tp/B52_DDN6_essai.ohm', 
                   delimiter='\t', header=None, skiprows=36, 
    names= ['a','b','m','n','R (Ohm)','Res. Error (Ohm)','IP (mV/V)','IP Error (mV/V)'], index_col=False,
    skipfooter=0, engine='python')
# Si le jeux de données contient moins de données, il faut ajuster les paramètres skiprows et names en fonction.
nbInit = len(data.index)
print('Initial number of values: {}'.format(nbInit))
print(data.describe())
# Montrer les histogrammes:
# 1) Résistance: 
binsR = np.logspace(start=np.log(min(data['R (Ohm)'])), stop=np.log(np.quantile(data['R (Ohm)'],0.9)),num=20)
hist1 = data.hist(column=['R (Ohm)'], bins=binsR, density=False)
# 2) IP:
hist2 = data.hist(column=['IP (mV/V)'], density=False)
pyplot.show()