# Aquisition de données sur le terrain

Il existe de nombreux appareils permettant l'aquisition de données de gravimétrie. A l'heure actuelle, les instruments terrestres portables modernes comprennent des systèmes automatisés de nivellement et d'enregistrement de données mais leurs capteurs sont toujours essentiellement basés sur les variations d'une masse au bout un ressort qui découlent d'une modification de l'accélération gravitationnelle. Parfois les changements de la longueur du ressort sont tellement faibles qu'ils nécessitent une certaine forme d'amplification. les anomalies mesurées sont généralement entre 0.1 et 0.00001 Gal et s'expriment donc le plus souvent en mGal. Pour rappel 1 Gal équivaut à 1 cm/s<sup>2</sup>.

# Les corrections

Le premier traitement de données à appliquer aux données de gravimétrie est l'éliminations des effets connus causés par des caractéristiques prévisibles qui ne font pas partie de la cible et influencent fortement les données brutes. Une fois toutes les corrections utiles appliquées et la suppression de tous les effets connus, l'anomalie restante est alors interprétée en termes de variations de densité sous la surface. Une réflexion préalable est nécessaire pour comprendre si ces corrections impliquent une addition ou une soustraction de l'anomalie. 

## La latitude

La gravité est plus forte aux pôles qu'à l'équateur et ce même s'ils sont plus proches du centre de la Terre. Ceci est dû à la force centrifuge opposée à l'équateur. La gravité augmente donc plus vous vous déplacez au nord de votre station de référence. La correction à appliquer est de 0.0081 sin(2a) mGal/10m (où a est la latitude)

## L'air libre 

Cette correction s'intéresse à l'élévation et permet la prise en compte de la dépendence à 1/r<sup>2</sup>. Une correction approximative à appliquer est de 0.03086 mGal/m.

## La correction de Bouguer

Cette correction corrige la valeur de la correction de l'air libre pour prendre en compte la masse de matériau entre l'élévation de référence et celle de la mesure. La correction à appliquer est 0.04191 * 10<sup>-3</sup> $\rho$  mGal/m, où $\rho$ est en première approximation évaluée à 2670 kg/m<sup>3</sup> (densité du quartz) ou par échantillonage.

## La topographie

Cette correction tient compte de la masse supplémentaire au-dessus (ex: collines), ou du déficit de masse (ex: vallées) en-dessous de l'altitude d'une mesure.

## L'effet des marées terrestres

Pour prendre en compte l'effet des marées, la mesure est répétée à différents moments sur la même station (de base) afin de mesurer la dérive. La formule à appliquer est la suivante:

![Eq_Deriv](./pictures/equation_derive.PNG)

# La modélisation directe


