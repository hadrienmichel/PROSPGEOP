'''This script solves the Snell-Descarte model for seismic reflection.
It will need in input (via GUI) a .sgt file that contains the first arrival 
for different sources and receivers. 
The script will first display the first arrival in a distance-time graph where
every source (with direction +/-) is displayed independently.
Then, the user will draw the hodochrones one after the other. When all the 
hodochrones are drawn, the script will compute and show the resulting model.
For the theory behind the model: https://www.ifsttar.fr/fileadmin/user_upload/editions/lcpc/GuideTechnique/GuideTechnique-LCPC-AGAP2.pdf
'''
