import numpy as np
import xlwt
from xlwt import Workbook
import requests
import json
import os
from utils import config
from utils.scrapping import *
import time

#import scholarly

config = config()

with open(config.path) as file:
    file_contents = file.read().replace('\u2028',' ')

with open(config.path_label) as file2:
    file_label = file2.read()

with open(config.path_poste) as file3:
    file_poste = file3.read()

with open(config.path_pays) as file4:
    file_pays = file4.read()

liste_label = file_label.split("\n")
liste_final_label = [x.upper() for x in liste_label if len(x)!=0]

liste_poste = file_poste.split("\n")
liste_final_poste = [x for x in liste_poste if len(x)!=0]

liste_pays = file_pays.split("\n")
liste_final_pays = [x for x in liste_pays if len(x)!=0]

# Workbook is created
wb = Workbook()
# add_sheet is used to create sheet.

sheet3 = wb.add_sheet('Chercheurs uniquement')
sheet3.write(0, 0, 'Name and Surname')
sheet3.write(0, 1, 'Name')
sheet3.write(0, 2, 'Surname')
sheet3.write(0, 3, 'Mail dapres papier 1')
sheet3.write(0, 4, 'Mail dapres papier 2')
sheet3.write(0, 5, 'Poste')
sheet3.write(0, 6, 'Label')
sheet3.write(0, 7, 'Date dapres papier 1')
sheet3.write(0, 8, 'Date dapres papier 2')
sheet3.write(0, 9, 'ATTENTION A VERIFIER adresse 1')
sheet3.write(0, 10, 'ATTENTION A VERIFIER adresse 2')
sheet3.write(0, 11, 'Adresse dapres papier 1')
sheet3.write(0, 12, 'Adresse dapres papier 2')

sheet4 = wb.add_sheet('Collaborateur uniquement')
sheet4.write(0, 0, 'Name and Surname ')
sheet4.write(0, 1, 'Name')
sheet4.write(0, 2, 'Surname')
sheet4.write(0, 3, 'MAIL dapres papier 1')
sheet4.write(0, 4, 'MAIL dapres papier 2')
sheet4.write(0, 5, 'PAYS dapres papier 1')
sheet4.write(0, 6, 'PAYS dapres papier 2')
sheet4.write(0, 7, 'DATE dapres papier 1')
sheet4.write(0, 8, 'DATE dapres papier 2')
sheet4.write(0, 9, 'ADRESSE dapres papier 1')
sheet4.write(0, 10, 'ADRESSE dapres papier 2')


offset_sheet3 = 0
offset_sheet4 = 0

compteur_del_label = 1

compteur_adresse_manquante = 1

all_index_fiche = len(file_contents.split(str(config.mot_clef_coupure)))-1
print("NOMBRE DE FICHES : " + str(all_index_fiche))
all_labels_to_filter = []
for index_fiche in range(all_index_fiche):
    fiche = fiche_chercheur_i(config, file_contents, index_fiche)
    print()
    print(index_fiche, all_index_fiche, index_fiche/all_index_fiche)

    if index_fiche == 15:
        wb.save(config.name_path_results)
    if len(fiche) !=0:
        flag_copy = True
        (name_surname, name, surname, poste) = get_name_surname_both_poste(fiche)
        print(name_surname, name, surname, poste)
        #démarrage filtrage label TODO : a mettre dans une fonction à part
        labels_all = get_labels(config, fiche)
        labels_all_liste_split = labels_all.split('"' )
        labels_all_liste_split2 = [x for x in labels_all_liste_split if len(x) > 2]
        compteur_label_2 = 0
        for l in labels_all_liste_split2:
            for l2 in liste_final_label:
                if l2.upper()== l.upper():
                    compteur_label_2 += 1
        print("LABELS ", labels_all_liste_split2)
        if len(labels_all_liste_split2)!=0:
            if (compteur_label_2 / len(labels_all_liste_split2)) > config.threshold_label:
                flag_copy = False
        #démarrage filtrage poste TODO : a mettre dans une fonction à part
        poste_uuper = poste.upper()
        print("POSTE ", poste_uuper)
        for poste_del in liste_final_poste:
            #print(poste_del, poste_uuper, poste_del in poste_uuper)
            if poste_del in poste_uuper:
                flag_copy = False
        print("A GARDER : ", flag_copy)
        if not flag_copy:
            compteur_del_label +=1
        # LES CHERCHEURS QUI NOUS INTERESSENT :
        if flag_copy:
            for l in labels_all_liste_split2:
                all_labels_to_filter.append(l.upper())

            offset_sheet3 +=1
            sheet3.write(offset_sheet3 + 1, 0, name_surname)
            sheet3.write(offset_sheet3 + 1, 1, name)
            sheet3.write(offset_sheet3 + 1, 2, surname)
            sheet3.write(offset_sheet3 + 1, 5, poste)
            sheet3.write(offset_sheet3 + 1, 6,labels_all)
            time.sleep(config.temps_dodo)
            uni = config.uni
            dico_a_remplir = get_info_surname(name, uni, config.base_donne, config.threshold_paper)
            if len(list(dico_a_remplir.keys()))==0:
                dico_a_remplir = get_info_surname(name, surname, config.base_donne, config.threshold_paper)
            if len(list(dico_a_remplir.keys()))==0:
                compteur_adresse_manquante +=1
                print("RIEN DANS LA BASE DE DONNE, TODO : regarder celle européenne")
                sheet3.write(offset_sheet3 + 1, 11 , "Adresse inconnue dans pubmed")
                sheet3.write(offset_sheet3 + 1, 12 , "Adresse inconnue dans pubmed")
            for idx_key, val_key in enumerate(sorted(dico_a_remplir.keys())):
                collaborateur = dico_a_remplir[val_key]["collaborateur"]
                min_global = 100000
                adresse_finale_chercheur = ""
                for idx_key2, val_key2 in enumerate(sorted(collaborateur.keys())):
                    #savoir si ce collaborateur est ou non notre chercheur
                    nom_ref_3 = name
                    prenom_ref = surname
                    adresse_finale_chercheur2_1 = collaborateur[val_key2].split(" ")
                    adresse_finale_chercheur2 = [x for x in adresse_finale_chercheur2_1 if len(x)>1]
                    mail_list = [x for x in adresse_finale_chercheur2 if "@" in x]
                    if len(mail_list)>0:
                        mail = mail_list[0]
                    else:
                        mail = ''
                    nom_a_tester_1 = val_key2.split(" ")
                    nom_a_tester_2 = [x for x in nom_a_tester_1 if len(x)!=0]
                    nom_a_tester_3 = nom_a_tester_2[0]
                    distance1 = sum([1 for x, y in zip(nom_ref_3, nom_a_tester_3) if x.lower() != y.lower()])
                    diff1 = np.abs(len(nom_ref_3)- len(nom_a_tester_3))+1
                    distance1f = distance1*diff1
                    distance2 = sum([1 for x, y in zip(prenom_ref, nom_a_tester_3) if x.lower() != y.lower()])
                    diff2 = np.abs(len(prenom_ref)- len(nom_a_tester_3))+1
                    distance2f = distance2*diff2
                    if min(distance1f, distance2f)<=min_global:
                        min_global = min(distance1f, distance2f)
                        adresse_finale_chercheur = collaborateur[val_key2]
                        nom_a_tester_3_keep = nom_a_tester_3
                        mail_final = mail
                print(min_global, nom_ref_3, nom_a_tester_3_keep, mail_final)
                sheet3.write(offset_sheet3 + 1, 3 + idx_key,mail_final)
                sheet3.write(offset_sheet3 + 1, 11 + idx_key,adresse_finale_chercheur)
                sheet3.write(offset_sheet3 + 1, 7 + idx_key, dico_a_remplir[val_key]["date_sortie"])
                if min_global>1:
                    sheet3.write(offset_sheet3 + 1, 9 + idx_key, "PB NOM! "+ str(nom_a_tester_3_keep))


                for idx_key2, val_key2 in enumerate(sorted(collaborateur.keys())):
                    #copy paste collaborateur
                    flag_copy_collab = False
                    adresse_finale_chercheur2_1 = collaborateur[val_key2].split(" ")
                    adresse_finale_chercheur2 = [x for x in adresse_finale_chercheur2_1 if len(x)>1]
                    mail_list = [x for x in adresse_finale_chercheur2 if "@" in x]
                    if len(mail_list)>0:
                        mail = mail_list[0]
                    else:
                        mail = ''
                    #detect pays
                    for pays in liste_final_pays:
                        for infos_add in adresse_finale_chercheur2:
                            infos_add2 = infos_add.rstrip("\n")
                            if ',' in infos_add:
                                infos_add2 = infos_add.replace(',', '')
                            if ';' in infos_add:
                                infos_add2 = infos_add.replace(';', '')
                            if '.' in infos_add:
                                infos_add2 = infos_add.replace('.', '')
                            if '\n' in infos_add:
                                infos_add2 = infos_add.replace('\n', '')
                            #print(pays.upper() , infos_add2.upper(), pays.upper() == infos_add2.upper())
                            if pays.upper() in infos_add2.rstrip('\n').upper():
                                pays_keep = pays.upper()
                                flag_copy_collab = True
                                #print(flag_copy_collab)
                    #print(val_key2, adresse_finale_chercheur2, infos_add2, flag_copy_collab)
                    if flag_copy_collab:
                        offset_sheet4 += 1
                        liste_pour_prenom = val_key2.split(' ')
                        liste_pour_prenom_2 = [x for x in liste_pour_prenom if len(x)!=0]

                        sheet4.write(offset_sheet4, 0, val_key2)
                        sheet4.write(offset_sheet4, 1, liste_pour_prenom_2[0])
                        sheet4.write(offset_sheet4, 2, liste_pour_prenom_2[1])
                        sheet4.write(offset_sheet4, 3+idx_key,mail)
                        sheet4.write(offset_sheet4, 9+idx_key,collaborateur[val_key2])
                        sheet4.write(offset_sheet4, 5+idx_key,pays_keep)
                        sheet4.write(offset_sheet4, 7+idx_key,dico_a_remplir[val_key]["date_sortie"])




values, counts = np.unique(all_labels_to_filter, return_counts=True)
sheet2 = wb.add_sheet('Labels')
sheet2.write(0, 0, 'Name label')
sheet2.write(0, 1, 'Number count')
for index_val, val in enumerate(values):
    cou = counts[index_val]
    sheet2.write(index_val+1, 0, val)
    sheet2.write(index_val+1, 1, int(cou))
wb.save(config.name_path_results)

print("NOMBRE DE FICHES SUPPRIMEES: " + str(compteur_del_label))

print("NOMBRE D'ADRESSE MANQUANTES: " + str(compteur_adresse_manquante))



"""
search_query = scholarly.search_author(str(val_key2))
fag_goon_colab =  True
print("RECHERCHE de : ", val_key2)
offset_ligne = 1
while fag_goon_colab:
    try:
        #search_query = scholarly.search_author(val_key2 + " " +dico_a_remplir[val_key]["nom_publication"] )
        authors = next(search_query)
        poste_col = authors.affiliation
        label_col = authors.interests
        email = authors.email
        #filtrage !! if interessant :
        poste_uuper = poste_col.upper()
        print("POSTE ", poste_uuper)
        flag_continue_filtrage = True

        for poste_del in liste_final_poste:
            #print(poste_del, poste_uuper, poste_del in poste_uuper)
            if poste_del in poste_uuper:
                flag_continue_filtrage = False

        if flag_continue_filtrage:
            compteur_label_3 = 0
            for l in label_col:
                for l2 in liste_final_label:
                    if l2.upper()== l.upper():
                        compteur_label_3 += 1
                    else:
                        all_labels_to_filter.append(l.upper())

            print("LABELS ", label_col)
            if len(label_col)!=0:
                if (compteur_label_3 / len(label_col)) > config.threshold_label:
                    flag_continue_filtrage = False

        if flag_continue_filtrage:

            sheet4.write(offset_sheet4, 6+offset_ligne, (poste_col, label_col, email))
            offset_ligne +=1


    except Exception:
        pass
        fag_goon_colab =  False
        poste_col=""
        label_col =""
time.sleep(config.temps_dodo_google)
"""
