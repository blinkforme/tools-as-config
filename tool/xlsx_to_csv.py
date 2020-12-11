import pandas as pd
import os
import xlrd

from ResConfig import ResConfig

res_path = "/Users/peterpuppy/code/fish-tool/resource/abbey_os_2_2"

config = ResConfig(res_path=res_path)
excels = config.get_all_excels()

for excel_path in excels:

    sheet_name = xlrd.open_workbook(excel_path).sheets()[0].name

    target_csv_path = os.path.split(excel_path)[0] + "/" + sheet_name + ".csv"
    print(target_csv_path)
    try:

        data_xls = pd.read_excel(excel_path, 0, index_col=None)

        # print os.path.split(excel_path)
        data_xls.to_csv(target_csv_path, encoding='utf-8', index=False)

        os.remove(excel_path)
    except Exception, e:
        print "fuck"
        print target_csv_path
        print e
