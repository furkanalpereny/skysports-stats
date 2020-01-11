import pandas
import os


if not os.path.exists("xlsx"): 
    os.makedirs("xlsx")

f = os.listdir("json")

for idx, item in enumerate(f):
    json_folder = "json/" + item
    xlsx_folder = "xlsx/" + item

    if not os.path.exists(xlsx_folder): 
        os.makedirs(xlsx_folder)

    f = os.listdir(json_folder)
    
    for idx, item in enumerate(f):
        json_file = json_folder + "/" + item
        xlsx_file = xlsx_folder + "/" + item.replace("json","xlsx") 
        if not os.path.exists(xlsx_file):
            df = pandas.read_json(json_file)
            df.to_excel(xlsx_file,index=False)