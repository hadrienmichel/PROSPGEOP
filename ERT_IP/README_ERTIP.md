# Aquisition de données sur le terrain
Il existe de nombreux appareils permettant l'aquisition de données de résistivité électrique et/ou de chargeabilité. Au laboratoire de Géophysique appliquée de l'Université de Liège, nous avons un [ABEM Terrameter LS (page en anglais)](https://www.guidelinegeo.com/product/abem-terrameter-ls-2/). En pratique, l'aquisition de données est relativement similaire quel que soit l'appareil.

Dans un premier temps, on enfonce les électrodes dans le sol suffisamment pour obtenir un bon contact entre l'électrode et le sol. Ces électrodes sont connectées à un cable multi-brin qui est lui-même connecté au résistivimètre. Ensuite, le résistivimètre va injecter du courant sur un jeux de deux électrodes (A et B) et mesurer le potentiel généré sur deux autres éléctrodes (M et N). Cette opération est répétée un grand nombre de fois afin de couvrir plusieurs positions horizontalement et verticalement. La mesure de chargeabilité se fait directement après la mesure de résistivité. En effet, après avoir charger le sol lors de la mesure de résistivité, ce dernier vas se décharger progressivement, créant un potentiel décroissant (exponentielle) sur les électrodes de mesure. Pour plus de détails, se réfèrer au cours théorique et aux rappels.

# Analyse des données

## 1) Analyses des données brutes:
Il est de bonne pratique de réaliser des histogrammes des données pour avoir une première idée de la qualité des données ainsi que du contenu du jeu de données. Pour ce faire, nous allons charger le jeu de données comme base de données *pandas* dans python et réaliser des histogrammes de la résistance mesurée ainsi que de la chargeabilité. Le script suivant vous permet de faire cette manipulation pour un fichier `.dat` contenant des données au format RES2DINV (voir ci-dessous). 

```python
import pandas as pd
import numpy as np
from matplotlib import pyplot
# Importer le jeu de données via pandas:
#   Si le jeux de données contient ERT et IP et que le jeu contient des estimations d'erreur,
#   les paramètres a entrée sont ceux utilisé ci-dessous.
data = pd.read_csv('./data/B52_Gradient7.dat', delimiter='\t', header=None, skiprows=15, 
    names= ['Nb. Electrodes', 'A(x)','A(y)','B(x)','B(y)','M(x)','M(y)',
    'N(x)','N(y)','R (Ohm)','Res. Error (Ohm)','IP (mV/V)','IP Error (mV/V)'], index_col=False,
    skipfooter=5, engine='python')
# Si le jeux de données contient moins de données, il faut ajuster les paramètres skiprows et names en fonction.
nbInit = len(data.index)
print('Initial number of values: {}'.format(nbInit))
# Montrer les histogrammes:
# 1) Résistance: 
binsR = np.logspace(start=np.log(min(data['R (Ohm)'])), stop=np.log(np.quantile(data['R (Ohm)'],0.9)),num=20)
hist1 = data.hist(column=['R (Ohm)'], bins=binsR, density=True)
# 2) IP:
hist2 = data.hist(column=['IP (mV/V)'], density=True)
pyplot.show()
```

Sur base de l'histogramme, il est déjà possible d'anticiper le nombre et le type d'anomalies qui seront observées dans le modèle inversé.

## 2) Modèles d'erreur:
Les mesures de résistivités électriques sont accompagnées d'erreurs. Ces erreurs peuvent venir de plusieurs sources: précision de la machine, bruit électrique ambiant, etc. Une première estimation de l'erreur est réalisée automatiquement par l'ABEM lors des mesures sur le terrain. Cependant, cette erreur ne représente qu'une (faible) partie de l'erreur totale. 

La meilleure manière de calculer l'erreur attenante à une mesure est d'utiliser le théorème de réciprocité. En théorie, la résistivité mesurée lors d'une injection sur le dipole AB et une mesure sur le dipole MN devrait être équivalente à celle obtenue lors d'une injection sur le dipole MN et une mesure sur le dipole AB. Ainsi, en répètant la mesure en inversant les dipoles d'injection et de mesure, on peut obtenir une estimation de l'erreur sur la mesure. Pour plus de détails, se référer aux rappels théoriques du cours.

# Inversion des données
L'inversion des données est réalisée a l'aide d'un code d'inversion non linéaire. Il existe plusieurs codes permettant de téaliser cette tâche: RES2DINV, BERT, E4D, CRTOMO, RESIPy, etc. Dans le cadre de ces travaux pratiques, nous allons utiliser le logiciel commercial RES2DINV. Télécharger l'archive contenant l'exécutable d'installation au lien suivant: [https://www.geotomosoft.com/Res2dinvx64_Setup.zip](https://www.geotomosoft.com/Res2dinvx64_Setup.zip). Ensuite, décompresser l'archive et installer le logiciel en suivant la procédure d'installation.

Lors du lancement de RES2DINV, une fenêtre s'affiche pour demander une clef de licence. Nous allons ici utiliser la version de démonstration de RES2DINV et n'avons donc pas besoin de license. 

RES2DINV prend en entrer un fichier de données `.dat`. Dans le cadre de ce tutoriel, nous allons utiliser le fichier [`Hod_DD.dat`](./data/HOD_DD.dat) pour faire les différentes manipulations. 

## 1) Charger les données
Avant de charger les données dans RES2DINV, nous allons définir le modèle utilisé comme étant le modèle raffiné: `Inversion` &rarr; `Model Discretization` &rarr; `Use model refinement`. Là, cocher la sélection `Use model cells with widths of half the unit space` (Utiliser des cellules de largeur égale à la moitié de l'espacement d'electrodes). Cette option permet d'obtenir un modèle plus détaillé pour l'inversion.
Pour charger les données dans RES2DINV, sélectionner `File` &rarr; `Read data file`. Une fenêtre s'ouvre et vous demande de sélectionner le fichier à inverser. 
Une fois le fichier ouvert, les caractéristiques du fichier s'affichent dans la fenêtre principale et un message vous signale que la lecture du fichier s'est bien déroulée.

## 2) Trier les données
Pour trier les données, sélectionner `Edit` &rarr; `Exterminate bad data points`. Une nouvelle fenêtre s'ouvre (*Fig.1*). Dans cette fenêtre est affichée une version simplifiée de la pseudosection. Chaque point représente l'écart par rapport a la moyenne pour une pseudo profondeur donnée. L'idée est que, comme la géologie n'est pas chaotique, les données géophysiques ne le soient pas non plus. Il faut donc détecter les valeurs qui sortent clairement de la tendance. Dans le cas du jeu de données présenté en exemple, il n'y a pas de données particulièrement problématiques.

![Exemple de fichier de données brut](./pictures/Exterminate.png)  
*Figure 1: Fenêtre de sélection des mauvais points de données*

Après avoir sélectionné les mauvais points, sélectionner `Exit` &rarr; `Quit edit window`. Si aucun point n'est enlevé, le jeu de données est conservé en mémoire tel quel. Dans le cas inverse, il est demandé de sauver le fichier pour pouvoir l'utiliser dans l'inversion. Il est recommandé d'utiliser un nom explicitant clairement l'objet du fichier (par exemple, `Hod_DDN6_ExterminateBadPoints.dat`, indiquant clairement l'action réalisée sur le jeu de données). Si le jeu de données est modifié, il est nécessaire de la recharger avant de procéder à la suite.

## 3) Réaliser l'inversion
Il est possible de changer beaucoup de paramètres d'inversion dans RES2DINV. Dans le cadre de cette introduction nous n'allons pas les voir. Ils sont cependant décrits complètement dans le [manuel de RES2DINV](https://www.geotomosoft.com/r2dimanu.zip).

Pour réaliser une inversion avec les paramètres par défaut, sélectionner `Inversion` &rarr; `Carry out inversion`.

Le programme va vous demander un emplacement pour sauvergader les résultats de l'inversion dans un fichier `.INV`.

L'inversion va alors se lancer. Dans la fenêtre, un graphique avec la pseudosection va s'afficher en haut et la progression des calculs nécéssaire à l'inversion s'affiche en bas (*Fig.2*).

![Début de l'inversion](./pictures/BeginInversion.png)  
*Figure 2: Démarrage de l'inversion*

A la fin de l'inversion (maximum 4 itérations dans la version démo de RES2DINV), la pseudo section mesurée, la pseudo section simulée ainsi que le résultat de l'inversion sont affichées (*Fig.3*). 

![Fin de l'inversion](./pictures/EndInversion.png)  
*Figure 3: Résultats de l'inversion*

## 4) Afficher les résultats
Pour afficher les résultats détaillés, sélectionner `Display` &rarr; `Show inversion results`. 

Une nouvelle fenêtre s'ouvre. Dans cette fenêtre, vous pouvez charger un fichier d'inversion (`File` &rarr; `Read file with inversion results`), export the model for visualization in other softwares (`File` &rarr; `Model export`) ou afficher le modèle inverse (`Display sections` &rarr; `Model display`). Pour cette dernière option, il est possible de choisir les sections à afficher. Par défaut, le programme affiche la pseudo section réelle et calculée, aisni que le résultat de l'inversion pour la résistivité électrique. Si le jeu de données inversé contient également des données de chargeabilité, il faut choisir ce qui est montré via l'option `Model display` &rarr; `Choose resistivity or IP display`.

Avant l'affichage, il est demandé de rentrer les différents paramètres d'affichage. Les paramètres par défaut sont en général suffisants.

# Interprétation des résultats
La première chose à regarder avant d'analyser le résultat est à quel point le résultat de l'inversion permet de reproduire les données mesurées sur le terrain. Une valeur unique est donnée pour cela: l'erreur absolue à l'itération courante (en %). De manière générale, cette erreur doit être la plus petite possible, sans cependant aller trop bas (une valeur raisonable se situe aux environs de 5%). 

Si on observe que les données ne peuvent pas être raisonablement reproduites après les 4 itérations de la version démo, il est possible que du bruit soit toujours présent dans le jeu de données. Il est possible d'alors utiliser la fonctionnalité `Edit Data` &rarr; `RMS error statistics` pour analyser l'impact de données individuelles. Une nouvelle fenêtre s'ouvre (*Fig.4*) alors et il est possible de sélectionner le seuil d'erreur individuel acceptable à l'aide des flêches gauche et droite du clavier.

![Statistiques sur les RMS](./pictures/RMSErrorRemove.jpeg)  
*Figure 4: Filtarge des données par RMS individuel*

Si des données sont enlevées, il faut sauvegarder le jeu de données et recommencer l'inversion. 

Une fois le fit des données assuré, il faut interpréter l'image résultante de l'inversion. Pour interpréter les données, il est bon de se remémorer les différents éléments vus lors de la partie pétrophysique du cours. Ainsi, au vu du context du profil (position, géologie, etc.) il est possible d'émètre des hypothèses sur la composition du sous-sol sur base de l'image.

## Artefacts d'inversion, sensibilité et profondeur d'investigation

Lors d'une inversion, certains éléments peuvent apparaitre dans l'image finale mais ne pas être représentatifs de la réalité. Il s'agit d'artefacts d'inversions. Ces artefacts peuvent prendre plusieurs formes: object dont l'étendue est prolongée dans l'une ou l'autre direction, couche très fine résistive en surface, etc.

Il faut donc être prudent lors de l'interprétation de résultats d'inversion. Il existe néanmoins plusieurs outils permettant de déterminer si un objet visible dans le profil fait partie d'une zone sensible ou non.

Deux de ces outils sont vus au cours de ces travaux pratiques:

### 1) Sensibilité
La matrice de sensibilité est calculée en même temps que l'inversion (il s'agit d'une matrice nécéssaire au calcul de l'inversion). On peut l'afficher en sélectionnant `Display section` &rarr; `Sensitivity displays` &rarr; `Display blocks sensitivity`. La sensibilité de l'inversion s'affiche (*Fig.5*).

![Sensibilité](./pictures/Sensitivity.png)  
*Figure 5: Sensibilité normalisée de l'inversion*

### 2) Profondeur d'investigation
La profondeur d'investigation peut être estimée a l'aide de l'index de profondeur d'investigation (*Depth of investigation, DOI*). Pour calculer ce dernier, il faut revenir dans l'écran d'inversion et selectionner `Inversion` &rarr; `Calculate region of investigation index`. Les paramètres par défaut qui sont proposés sont adéquats pour la majorité des cas. L'inversion dans ce cas-ci prend plus de temps et sera sauvée dans 2 fichiers `.INV` qui sont référencés dans un fichier `.txt`.

Pour afficher le DOI, il faut aller dans la fenêtre d'affichage et charger les deux fichiers du DOI: `File` &rarr; `Read DOI files` &rarr; `Read DOI pair of inversion files`. Ensuite, sélectionner `Display sections` &rarr; `Display region of investigation`. Le DOI s'affiche (*Fig. 6*).

![DOI](./pictures/DOI.png)  
*Figure 6: Profondeur d'investigation*

# Visualisation des données
Pour visualiser des résultats d'inversion plus complexes, nous allons utiliser un logiciel de visualitation 3D appelé [Paraview](https://www.paraview.org/). Ce logiciel permet de simplement visualiser un bloc modèle 3D et de réaliser des manipulations de base dessus.

Les fichiers représentant les modèles d'inversions sont donnés sous le format `.vtk`. Ces fichiers contiennent la géométrie ainsi que les valeurs obtenues pour le modèle inverse. Il est donc possible d'analyser le "mesh" d'inversion en même temps que le résultat.

Dans un premier temps, nous allons charger un modèle dans la fenêtre de Paraview. Pour ce faire, il suffit de glisser le fichier `.vtk` dans la zone `Pipline Browser`. Une fois le fichier chargé, les propriétés de l'objet vont s'afficher en dessous dans le volet `Properties`. Cliquer sur `Apply` pour afficher le modèle.

Pour manipuler l'objet, il suffit de cliquer sur la fenêtre et de faire tourner le mesh. Il peut cependant parfois être dificile d'avoir une orientation spécifique. Pour cela, différentes options sont présentes dans la barre d'outils `Camera Controls` (voir *Fig. 7*).

![Importer dans paraview et bouger l'objet](./pictures/ParaviewOpenView.gif)  
*Figure 7: Import dans paraview et mouvements*

Il est possible de changer le type de données visualisé (Inversion en résistivité, IP ou sensibilité par exemple). Pour faire cela, il faut utiliser la boite à outils `Active Variable Controls`. Une fois une donnée sélectionnée, il est possible de changer l'échelle de visualisation qui lui est appliquée. Un exemple est montré en Figure 8 
Dans le volet de droite, il est possible de changer l'échelle de couleurs (*Fig. 8*).

![Changer l'echelle de couleur dans paraview](./pictures/ParaviewColorScale.gif)  
*Figure 8: Changer l'échelle de couleur dans paraview*

Ensuite, il est possible de faire des manipulations plus avancées de type "Clip", "Slice" et "Threshold". Ces manipulations vont permettre d'observer l'intérieur du modèle.

![Clip et Threshold dans paraview](./pictures/ParaviewClipThreshold.gif)  
*Figure 9: Clip et Threshold dans paraview*

# A vous de jouer!