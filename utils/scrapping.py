import numpy as np
import xlwt
from xlwt import Workbook
import requests
import json
import os

def fiche_chercheur_i(config, file_contents, index):
    print()
    return file_contents.split(config.mot_clef_coupure)[index]

def get_name_surname_both_poste(fiche):
    index_name_surname = 0
    fiche_liste = fiche.split('\n')
    fiche_liste_nettoye = [e for e in fiche_liste if e !='']
    """
    if len(fiche.split('\n')[index_name_surname])==0:
        liste_first_line = fiche.split('\n')[index_name_surname+1].split("-")
    else:
        liste_first_line = fiche.split('\n')[index_name_surname].split("-")
    """
    liste_first_line = fiche_liste_nettoye[0].split("-")

    name_surname = liste_first_line[0]

    index_name = -1

    if len(name_surname.split(" ")[index_name])!=0:
        name = name_surname.split(" ")[index_name]
    else:
        name = name_surname.split(" ")[index_name-1]
    surname = " "
    liste_name_split = name_surname.split(" ")
    for j in range(len(liste_name_split)-2):
        surname += liste_name_split[j]
        surname += " "
    poste = ''
    for j in range(1,len(liste_first_line)):
        poste += liste_first_line[j]
        poste += " "
    return (name_surname, name, surname, poste)

def get_labels(config, fiche):
    labels_start = fiche.split("Profile labels:")
    if len(labels_start)!=1:
        labels_end = labels_start[1].split(config.balise_split_end_label)
        labels_all = labels_end[0]
    else:
        labels_all = ""
    return labels_all

def get_info_surname(surname, base_donne, threshold_paper):
    name_api = surname.replace(' ', "+")
    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db="+base_donne+"&term="+name_api+"&retmode=json")
    try:
        idx_to_test = response.json()["esearchresult"]["idlist"]
        name = response.json()["esearchresult"]["querytranslation"]
    except Exception:
        return {}
    compteur =0
    dico_surname = {}
    if response.status_code != 200:
        print("API down")
    if len(idx_to_test)!=0:
        for index_idx_to, idx_to in enumerate(idx_to_test):
            if compteur < threshold_paper:
                print("-"*20 + " ID publication " +idx_to + "-"*20)
                flag_start = True
                try:
                    response2 = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db="+base_donne+"&id=" + str(idx_to))
                except Exception:
                    flag_start = False
                    pass
                if response2.status_code != 200:
                    print("API down")
                a_parser = response2.content.decode('utf8')
                if "names std" not in a_parser:
                    flag_start = False
                    print("ok1")
                if "name ml" not in a_parser:
                    flag_start = False
                    print("ok2")
                if "from journal" not in a_parser:
                    flag_start = False
                    print("ok3")
                if "affil str" not in a_parser:
                    flag_start = False
                    print("ok4")
                if "date std" not in a_parser:
                    flag_start = False
                    print("ok5")
                if flag_start:
                    compteur +=1
                    dico_surname[idx_to] = {}
                    titre_publie = a_parser.split("cit")[1].split("title {")[1].split("}")[0]
                    nom_finale_publie = titre_publie.replace("name", "").replace('"', "")
                    dico_surname[idx_to]["nom_publication"] = nom_finale_publie
                    date = a_parser.split("date std")[1].split("year")[1].split("month")[0].replace(',', '')
                    try:
                        month = ""
                        month = a_parser.split("date std")[1].split("month")[1].split("}")[0].replace(',', '')
                    except Exception:
                        pass

                    date_sortie = date.replace(' ', '') + month.replace(' ', '')
                    dico_surname[idx_to]["date_sortie"] = date_sortie

                    dico_surname[idx_to]["collaborateur"] = {}

                    start_adresse_std = a_parser.split("names std")[1]
                    start_1chercheur = start_adresse_std.split("name ml")
                    start_1chercheur[-1] = start_1chercheur[-1].split("from journal")[0]


                    for fiche_cher in start_1chercheur:
                        if "affil str" in fiche_cher:
                            name_chercheur = fiche_cher.split("affil str")[0].replace(',','')
                            adresse = fiche_cher.split("affil str")[1].replace("},", "").replace("}", "").replace("{","")
                            if "name consortium" in adresse:
                                adresse = adresse.split("name consortium")[0]
                            final_nom_chercheur = name_chercheur.replace('"', '')
                            dico_surname[idx_to]["collaborateur"][final_nom_chercheur] = adresse.replace('"', '')
    return dico_surname
