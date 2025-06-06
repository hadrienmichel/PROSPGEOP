# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 13:46:42 2023

@author: tomde
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot

fullFilenamePath = './data/B52_DDN6_TP.ohm'  # Chemin depuis ce code vers le fichier des données
numberOfBarsInHistogram = 20

labelERT = 'R (Ohm)'
labelIP = 'IP (V/V)'

# Importer le jeu de données via pandas:
#
#   - Si le jeux de données contient ERT et IP et que le jeu contient des estimations d'erreur,
#   les paramètres a entrer sont ceux utilisés ci-dessous.
#
#   - Si le jeux de données contient moins de données,
#   il faut ajuster les paramètres skiprows et names en fonction.
#
data = pd.read_csv(
    fullFilenamePath,
    delimiter='\t',
    header=None,
    skiprows=36,  # Doit correspondre au nombre de lignes à skipper au début du fichier de données
    names= [
        'a', 'b', 'm', 'n',
        labelERT, 'Res. Error (Ohm)',
        labelIP, 'IP Error (V/V)'],
    index_col=False,
    skipfooter=0,  # Nombre de lignes vides ou nulles à ignorer en fin de fichier
    engine='python')
nbInit = len(data.index)
print(f'Initial number of values: {nbInit}')
print(data.describe())

# Montrer les histogrammes:

# 1) Résistance:
binsR = np.logspace(
    start=np.log10(min(data[labelERT])),
    stop=np.log10(max(data[labelERT])),
    num=numberOfBarsInHistogram + 1)
hist1 = data.hist(
    column=labelERT,
    bins=binsR,
    density=False)  # Nécéssairement False quand axe x en log
pyplot.xscale('log')

# 2) IP:
hist2 = data.hist(
    column=labelIP,
    bins=numberOfBarsInHistogram,
    density=False)

pyplot.show()
