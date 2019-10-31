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
from main import main_1
import glob



config = config()

path = config.folder_all_files

all_files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.csv' in file:
            all_files.append(os.path.join(r, file))


for path in all_files:
    config.set_("path", path)
    name_file = path.split("/")[-1]
    name_file2 = name_file.split(".txt")[0]
    name_file3 = name_file2.replace("_", " ")
    config.set_("name_path_results", config.folder_all_files_results + name_file3+".xls")
    main_1(config)
