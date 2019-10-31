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
from compare_2_execel import main_1
import glob



config = config()

path_rigin = config.folder_all_files_csv

all_files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path_rigin):
    for file in f:
        if '.csv' in file:
            all_files.append(os.path.join(r, file))


for path in all_files:
    config.set_("path", path)
    name_file = path.split("/")[-1]
    name_file2 = name_file.split(".xls")[0]
    name_file3 = name_file2.replace("_", " ")
    config.set_("name_path_results", config.folder_all_files_results_xls + name_file3+".xls")
    main_1(config)
