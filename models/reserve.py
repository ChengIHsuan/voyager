import sqlite3
from models.search import Search

class Reserve():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 【找醫療機構】保留條件
    def hosp_reserved(self, county, township, names, types, star):
        try:
            ## reserved = [縣市, 鄉鎮市區, 名稱1, 名稱2, 名稱3, 是否醫學中心, 是否區域醫院, 是否地區醫院, 是否診所, 星等]
            #### 縣市, 鄉鎮市區
            reserved = [county, township]
            #### 名稱1, 名稱2, 名稱3
            for name in names:
                reserved.append(name)
            #### 是否醫學中心, 是否區域醫院, 是否地區醫院, 是否診所(醫療層級預設皆為false，若有勾選擇改為true)
            default_tyype = ['false', 'false', 'false', 'false']
            reserved.extend(default_tyype)
            for type in types:
                i = (int(type) + 4)  #層級value為1~4，對應保留條件陣列中5~8位置#
                reserved[i] = 'true'
            #### 星等
            while star == '':  #即使用者沒有選擇星等#
                star = 0
            reserved.append(star)
            return reserved
        except:
            return "抱歉，操作失敗。[HR]"

    ## 【找疾病】保留條件
    def disease_reserved(self, disease_id, county, township, names, types, star):
        try:
            ## reserved = [特殊疾病, 縣市, 鄉鎮市區, 名稱1, 名稱2, 名稱3, 是否醫學中心, 是否區域醫院, 是否地區醫院, 是否診所, 星等, 疾病名稱]
            #### 特殊疾病, 縣市, 鄉鎮市區
            reserved = [disease_id, county, township]
            #### 名稱1, 名稱2, 名稱3
            for name in names:
                reserved.append(name)
            #### 是否醫學中心, 是否區域醫院, 是否地區醫院, 是否診所(醫療層級預設皆為false，若有勾選擇改為true)
            default_tyype = ['false','false','false','false']
            reserved.extend(default_tyype)
            for type in types:
                i = (int(type) + 5)  #層級value為1~4，對應保留條件陣列中6~9位置#
                reserved[i] = 'true'
            #### 星等
            while star == '':  #即使用者沒有選擇星等#
                star = 0
            reserved.append(star)
            #### 疾病名稱(用於麵包屑)
            reserved.append(Search().disease_breadcrumb(disease_id))
            return reserved
        except:
            return "抱歉，操作失敗。[DR]"

    ## 【找科別】保留條件
    def depart_reserved(self, depart_id, county, township, types, names):
        try:
            print('subj_reserved')
            ## reserved = [科別, 縣市, 鄉鎮市區, 是否醫學中心, 是否區域醫院, 是否地區醫院, 是否診所, 名稱1, 名稱2, 名稱3]
            #### 科別, 縣市, 鄉鎮市區
            reserved = [depart_id, county, township]
            #### 是否醫學中心, 是否區域醫院, 是否地區醫院, 是否診所(醫療層級預設皆為false，若有勾選擇改為true)
            default_tyype = ['false', 'false', 'false', 'false']
            reserved.extend(default_tyype)
            for type in types:
                i = (int(type) + 2)  #層級value為1~4，對應保留條件陣列中3~6位置#
                reserved[i] = 'true'
            #### 名稱1, 名稱2, 名稱3
            for name in names:
                reserved.append(name)
            #### 科別名稱(用於麵包屑)
            print(reserved)
            reserved.append(Search().depart_breadcrumb(depart_id))
            print(reserved)
            return reserved
        except:
            return "抱歉，操作失敗。[SR]"

    ## 【找醫師】保留條件
    def doc_reserved(self, doctor, depart, names):
        try:
            for name in names:
                ## reserved = [醫師, 科別, 醫療機構名稱]
                reserved = [doctor, depart, name]
            print(reserved)
            return reserved
        except:
            return "抱歉，操作失敗。[CR]"