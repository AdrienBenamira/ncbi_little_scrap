import numpy as np
import xlwt
from xlwt import Workbook
import requests
import json
import os
from utils import config
from utils.scrapping import *
import time
import scholarly
import pandas as pd

config = config()

df1 = pd.read_csv(config.path_excel)
df = df1.fillna("")
wb = Workbook()
# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Chercheurs infos')
for index_key, key in enumerate(df.keys()):
    sheet1.write(0, index_key, key)
    for index_line, line in enumerate(df[key]):
        sheet1.write(index_line+1, index_key, line)
offset = len(df.keys())

sheet1.write(0, offset+1, 'Date papier 1')
sheet1.write(0, offset+2, 'Date papier 2')
sheet1.write(0, offset+3, 'Estmation ville adresse 1')
sheet1.write(0, offset+4, 'Estmation ville adresse 2')
sheet1.write(0, offset+5, 'Estmation mail adresse 1')
sheet1.write(0, offset+6, 'Estmation mail adresse 2')
sheet1.write(0, offset+7, 'Adresse d après papier 1')
sheet1.write(0, offset+8, 'Adresse d après papier 2')

compteur_adresse_manquante = 0
for index_df in range(len(df)):
    print()
    print(index_df, len(df), index_df/len(df))
    print(df["Prénom"][index_df], df["Nom"][index_df])

    if index_df == 10:
        wb.save(config.name_path_results_excel)


    name = df["Nom"][index_df]
    surname = df["Prénom"][index_df]
    ville = df["Ville"][index_df]
    try:
        name_surname =name + " "+ surname
    except Exception:
        print("PAS DE PRENOM")
        sheet1.write(index_df + 1, offset + 1,"PAS DE PRENOM !!")
        compteur_adresse_manquante +=1
        continue
    uni = df["Organisation_Etablissement"][index_df]
    dico_a_remplir = get_info_surname(name, uni, config.base_donne, config.threshold_paper)
    if len(list(dico_a_remplir.keys()))==0:
        dico_a_remplir = get_info_surname(name, surname, config.base_donne, config.threshold_paper)
    if len(list(dico_a_remplir.keys()))==0:
        compteur_adresse_manquante +=1
        print("RIEN DANS LA BASE DE DONNE, TODO : regarder celle européenne")
        sheet1.write(index_df + 1, offset + 1,"RIEN DANS LA BASE DE DONNE, TODO : regarder celle européenne")
    for idx_key, val_key in enumerate(sorted(dico_a_remplir.keys())):
        collaborateur = dico_a_remplir[val_key]["collaborateur"]
        min_global = 100000
        flag_goon = True
        adresse_finale_chercheur = ""
        for idx_key2, val_key2 in enumerate(sorted(collaborateur.keys())):
            nom_ref_3 = name
            prenom_ref = surname
            nom_a_tester_1 = val_key2.split(" ")
            nom_a_tester_2 = [x for x in nom_a_tester_1 if len(x)!=0]
            nom_a_tester_3 = nom_a_tester_2[0]
            distance1 = sum([1 for x, y in zip(nom_ref_3, nom_a_tester_3) if x.lower() != y.lower()])
            distance2 = sum([1 for x, y in zip(prenom_ref, nom_a_tester_3) if x.lower() != y.lower()])
            if min(distance1, distance2)<=min_global:
                min_global = min(distance1, distance2)
                adresse_finale_chercheur = collaborateur[val_key2]
                nom_a_tester_3_keep = nom_a_tester_3

        print(min_global,nom_ref_3, nom_a_tester_3_keep)
        if min_global > config.threshold_nom:
            flag_goon = False

        if flag_goon:
            #get mail
            adresse_finale_chercheur2_1 = adresse_finale_chercheur.split(" ")
            adresse_finale_chercheur2 = [x for x in adresse_finale_chercheur2_1 if len(x)>1]
            mail_list = [x for x in adresse_finale_chercheur2 if "@" in x]
            if len(mail_list)>0:
                mail = mail_list[0]
            else:
                mail = ''
            #get adresse
            min_global_adresse= 100000
            flag_ville = False
            for infos in adresse_finale_chercheur2:
                infos2 = infos
                if ',' in infos:
                    infos2 = infos.replace(',', '')
                #print(adresse_finale_chercheur2, infos2)
                distance2_ville = sum([1 for x, y in zip(ville, infos2) if x.lower() != y.lower()])
                if distance2_ville<=min_global_adresse:
                    min_global_adresse = distance2_ville
                    if min_global_adresse <= config.threshold_ville:
                        if len(infos2)==len(ville):
                            flag_ville = True
                            ville_estmate = infos2




            sheet1.write(index_df + 1, offset + 7 + idx_key ,adresse_finale_chercheur)
            sheet1.write(index_df + 1, offset + 1 + idx_key, dico_a_remplir[val_key]["date_sortie"])
            if flag_ville:
                sheet1.write(index_df + 1, offset + 3 + idx_key, ville_estmate)
            else:
                sheet1.write(index_df + 1, offset + 3 + idx_key, "ville différente")
            sheet1.write(index_df + 1, offset + 5 + idx_key, mail)


print("NOMBRE D'ADRESSE MANQUANTES: " + str(compteur_adresse_manquante))

wb.save(config.name_path_results_excel)
