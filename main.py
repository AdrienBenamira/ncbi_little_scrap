import numpy as np
import xlwt
from xlwt import Workbook
import requests
import json
import os
from utils import config
from utils.scrapping import *
import time

from joblib import dump, load
#import scholarly
import pandas as pd

from allennlp.modules.elmo import Elmo, batch_to_ids

options_file = "https://allennlp.s3.amazonaws.com/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_options.json"
weight_file = "https://allennlp.s3.amazonaws.com/models/elmo/2x4096_512_2048cnn_2xhighway/elmo_2x4096_512_2048cnn_2xhighway_weights.hdf5"

# Compute two different representation for each token.
# Each representation is a linear weighted combination for the
# 3 layers in ELMo (i.e., charcnn, the outputs of the two BiLSTM))
elmo = Elmo(options_file, weight_file, 1, dropout=0)

def embed(sent, elmo):
    character_ids = batch_to_ids(sent)
    embeddings = elmo(character_ids)
    return embeddings["elmo_representations"][0].mean(1).detach().numpy()



def main_1(config):
    start = time.time()
    clf = load(config.machine_learning_path)

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
    wb = Workbook()
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

    sheet5 = wb.add_sheet('MAMAN postprocessing')
    sheet5.write(0, 0, 'Name and Surname')
    sheet5.write(0, 1, 'Name')
    sheet5.write(0, 2, 'Surname')
    sheet5.write(0, 3, 'Mail dapres papier 1')
    sheet5.write(0, 4, 'Mail dapres papier 2')
    sheet5.write(0, 5, 'Poste')
    sheet5.write(0, 6, 'Label')
    sheet5.write(0, 7, 'Date dapres papier 1')
    sheet5.write(0, 8, 'Date dapres papier 2')
    sheet5.write(0, 9, 'ATTENTION A VERIFIER adresse 1')
    sheet5.write(0, 10, 'ATTENTION A VERIFIER adresse 2')
    sheet5.write(0, 11, 'Adresse dapres papier 1')
    sheet5.write(0, 12, 'Adresse dapres papier 2')



    offset_sheet3 = 0
    offset_sheet4 = 0
    offset_sheet5 = 0

    compteur_del_label = 1
    compteur_adresse_manquante = 1
    all_index_fiche = len(file_contents.split(str(config.mot_clef_coupure)))-1
    print("NOMBRE DE FICHES : " + str(all_index_fiche))
    all_labels_to_filter = []
    for index_fiche in range(all_index_fiche):
        fiche = fiche_chercheur_i(config, file_contents, index_fiche)
        print()
        print("AVANCEMENT", index_fiche, all_index_fiche, 100*index_fiche/all_index_fiche)
        if index_fiche == 15:
            wb.save(config.name_path_results)
        if len(fiche) !=0:
            flag_copy = True
            flag_copy_postprocessing_maman = True
            (name_surname, name, surname, poste) = get_name_surname_both_poste(fiche)
            print(name_surname, name, surname, poste)
            #démarrage filtrage label TODO : a mettre dans une fonction à part
            labels_all = get_labels(config, fiche)
            print(labels_all)
            df_a_tester = pd.DataFrame({"text": [labels_all]})
            df_2 = clean_up(df_a_tester)
            list_test = [x.split(" ") for x in df_2["clean_text"]]
            elmo_test = embed(list_test, elmo)
            elmo_test_new =elmo_test
            preds_test = clf.predict(elmo_test_new)
            sub = pd.DataFrame({'text':df_2['clean_text'], 'label':preds_test})
            print("LABEL CLEAN : ")
            print(sub)
            print()
            if sub["label"][0]==1:
                #print(sub["text"][0], len(sub["text"][0]))
                if sub["text"][0]!="":
                    flag_copy = False
                else:
                    flag_copy_postprocessing_maman= False
            """
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
            """
            #démarrage filtrage poste TODO : a mettre dans une fonction à part
            poste_uuper = poste.upper()
            print("POSTE ", poste_uuper)
            for poste_del in liste_final_poste:
                #print(poste_del, poste_uuper, poste_del in poste_uuper)
                if poste_del in poste_uuper:
                    flag_copy = False

            # LES CHERCHEURS QUI NOUS INTERESSENT :
            if config.postprocessing_maman:
                if not flag_copy_postprocessing_maman:
                    flag_copy = False

            print("A GARDER : ", flag_copy)
            if not flag_copy:
                compteur_del_label +=1

            if flag_copy:
                #for l in labels_all_liste_split2:
                all_labels_to_filter.append(df_2['clean_text'])
                copy_paste_list = {}
                mail1=""
                mail2=""
                offset_sheet3 +=1
                sheet3.write(offset_sheet3 + 1, 0, name_surname)
                sheet3.write(offset_sheet3 + 1, 1, name)
                sheet3.write(offset_sheet3 + 1, 2, surname)
                sheet3.write(offset_sheet3 + 1, 5, poste)
                sheet3.write(offset_sheet3 + 1, 6,labels_all)
                copy_paste_list["name_surname"] = name_surname
                copy_paste_list["name"] = name
                copy_paste_list["surname"] = surname
                copy_paste_list["poste"] = poste
                copy_paste_list["labels_all"] = labels_all


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
                            mail_clean1 = config.fin_adresse_mail + "."
                            mail_clean2 = config.fin_adresse_mail + ";"

                            mail_final = mail.replace(mail_clean1,config.fin_adresse_mail).replace(mail_clean2, config.fin_adresse_mail)
                    print(min_global, nom_ref_3, nom_a_tester_3_keep, mail_final)
                    sheet3.write(offset_sheet3 + 1, 3 + idx_key,mail_final)
                    sheet3.write(offset_sheet3 + 1, 11 + idx_key,adresse_finale_chercheur)
                    sheet3.write(offset_sheet3 + 1, 7 + idx_key, dico_a_remplir[val_key]["date_sortie"])
                    copy_paste_list[str(idx_key)] = {}
                    copy_paste_list[str(idx_key)]["mail_final"] = mail_final
                    copy_paste_list[str(idx_key)]["adresse_finale_chercheur"] = adresse_finale_chercheur
                    copy_paste_list[str(idx_key)]["date_sortie"] = dico_a_remplir[val_key]["date_sortie"]


                    if idx_key==0:
                        mail1= mail_final
                    else:
                        mail2=mail_final
                    if min_global>1:
                        sheet3.write(offset_sheet3 + 1, 9 + idx_key, "PB NOM! "+ str(nom_a_tester_3_keep))
                        copy_paste_list[str(idx_key)]["PB_nom"] =  "PB NOM! "+ str(nom_a_tester_3_keep)
                    else:
                        copy_paste_list[str(idx_key)]["PB_nom"] =  " "



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
                            if len(liste_pour_prenom_2)>0:
                                sheet4.write(offset_sheet4, 2, liste_pour_prenom_2[1])
                            sheet4.write(offset_sheet4, 3+idx_key,mail)
                            sheet4.write(offset_sheet4, 9+idx_key,collaborateur[val_key2])
                            sheet4.write(offset_sheet4, 5+idx_key,pays_keep)
                            sheet4.write(offset_sheet4, 7+idx_key,dico_a_remplir[val_key]["date_sortie"])


                if config.postprocessing_maman:
                    valid = False
                    if config.fin_adresse_mail in mail1 or config.fin_adresse_mail in mail2:
                        valid = True
                    if valid:
                        offset_sheet5 +=1
                        sheet5.write(offset_sheet5 + 1, 0, copy_paste_list["name_surname"])
                        sheet5.write(offset_sheet5 + 1, 1, copy_paste_list["name"])
                        sheet5.write(offset_sheet5 + 1, 2, copy_paste_list["surname"])
                        if "0" in copy_paste_list.keys():
                            sheet5.write(offset_sheet5 + 1, 3, copy_paste_list["0"]["mail_final"])
                            sheet5.write(offset_sheet5 + 1, 7, copy_paste_list["0"]["date_sortie"])
                            sheet5.write(offset_sheet5 + 1, 9, copy_paste_list["0"]["adresse_finale_chercheur"])
                        if "1" in copy_paste_list.keys():
                            sheet5.write(offset_sheet5 + 1, 4, copy_paste_list["1"]["mail_final"])
                            sheet5.write(offset_sheet5 + 1, 8, copy_paste_list["1"]["date_sortie"])
                            sheet5.write(offset_sheet5 + 1, 10, copy_paste_list["1"]["adresse_finale_chercheur"])
                        sheet5.write(offset_sheet5 + 1, 5, copy_paste_list["poste"])
                        sheet5.write(offset_sheet5 + 1, 6, copy_paste_list["labels_all"])



                print()
                print("NOMBRE DE CHERCHEURS DE L'UNIVERSITE : ", offset_sheet3)
                print("NOMBRE DE Collaborateurs DE L'UNIVERSITE : ", offset_sheet4)
                print("NOMBRE DE CHERCHEURS apres traitement maman : ", offset_sheet5)
                print()

    values, counts = np.unique(all_labels_to_filter, return_counts=True)
    sheet2 = wb.add_sheet('Labels')
    sheet2.write(0, 0, 'Name label')
    sheet2.write(0, 1, 'Number count')
    for index_val, val in enumerate(values):
        cou = counts[index_val]
        sheet2.write(index_val+1, 0, val)
        sheet2.write(index_val+1, 1, int(cou))
    wb.save(config.name_path_results)
    print()
    print()
    print("NOMBRE DE FICHES SUPPRIMEES: " + str(compteur_del_label))
    print()
    print("NOMBRE D'ADRESSE MANQUANTES: " + str(compteur_adresse_manquante))
    print()
    print()
    print("FIN, TIME : ", time.time() - start)

if __name__ == "__main__":
    # execute only if run as a script

    config = config()
    main_1(config)
