import sqlite3
from flask import Flask, request, render_template, flash, redirect

class Search():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ##科別
    def search_depart(self, depart):
        sql_where = "s.depart_id = {}".format(depart)
        return sql_where

    ##主觀指標
    def search_subjective(self, subjective):
        getStr = {
            '1': "統計數據",
            '2': "醫病關係",
            '3': "事後處理",
            '4': "行政項目",
            '5': "專業人員與器材",
            '6': "檢查及藥物和轉診",
            '7': "不良事件",
            '8': "其他註解"
        }

        return getStr.get(subjective)



    ##地點
    def search_area(self, county, township):
        try:
            area = county + township
            ## 依照使用者在前端輸入的條件寫成SQL字串中的condition
            sql_where = "h.area LIKE '%" + area + "%'"
            ## 驗證使用者是否輸入不存在的條件
            validate = self.cursor.execute("SELECT h.id FROM hospitals h WHERE " + sql_where).fetchall()
            if validate == []:
                return "抱歉，找不到您要的「{}{}」相關資訊。".format(county, township)
            else:
                return sql_where
        except:
            return "抱歉，操作失敗。[A]"

    ## 特殊疾病
    def search_disease(self, disease):
        try:
            ## 取得各疾病名稱
            getStr = {
                '1': "氣喘",
                '2': "急性心肌梗塞",
                '3': "糖尿病",
                '4': "人工膝關節手術",
                '5': "腦中風",
                '6': "鼻竇炎",
                '7': "子宮肌瘤手術",
                '8': "消化性潰瘍",
                '9': "血液透析",
                '10': "腹膜透析"
            }
            return getStr.get(disease)
        except:
            return "抱歉，操作失敗。[D]"

    ## 醫院層級
    def search_type(self, types):
        try:
            ## 建立一個tuple，使前端取回的type值可以對應正確的醫院層級
            getStr = {
                '1': "醫學中心",
                '2': "區域醫院",
                '3': "地區醫院",
                '4': "診所"
            }
            ## 建立一個SQL語法中condition的開頭字串
            sql_where = ''
            ## 對應正確的醫院層級後寫入condition字串中
            for type in types:
                ## 判斷若非陣列最後一個元素則加"OR"
                if type != types[-1]:
                    sql_where += "h.type = '" + getStr.get(type) + "' OR "
                else:
                    sql_where += "h.type = '" + getStr.get(type) + "'"
            return sql_where
        except:
            return "抱歉，操作失敗。[T]"

    ## 醫院名稱
    def search_name(self, names):
        try:
            ## 建立一個SQL語法中condition的開頭字串
            sql_where = ''
            ## 寫入condition字串中，對應全名或是縮寫
            for name in names:
                ## 檢查使用者輸入之名稱是否存在
                validate = self.cursor.execute("SELECT h.id FROM hospitals h WHERE h.name LIKE '%" + name + "%' OR h.abbreviation LIKE '%" + name + "%'").fetchall()
                if validate == []:
                    return "抱歉，找不到您要的「{}」相關資訊。".format(name)
                else:
                    ## 判斷若非陣列最後一個元素則加"OR"
                    if name != names[-1]:
                        sql_where += ("h.name LIKE '%" + name + "%' OR h.abbreviation LIKE '%" + name + "%' OR ")
                    else:
                        sql_where += ("h.name LIKE '%" + name + "%' OR h.abbreviation LIKE '%" + name + "%'")
            return sql_where
        except:
            return "抱歉，操作失敗。[N]"

    ## 評價結果
    def search_reviews(self, star):
        try:
            sql_where = ''
            if star != '':
                sql_where += "fr.star >= " + star + " AND fr.star != 'N/A' "
            # if positive != '':
            #     sql_where += "fr.positive >= " + positive + " AND fr.positive != 'N/A' AND "
            # if negative != '':
            #     sql_where += "fr.negative <= " + negative+ " AND "
            # sql_where = sql_where[:-4]
            return sql_where
        except:
            return "抱歉，操作失敗。[R]"

    ## 查詢條件
    def search_filter(self, county, township, disease, types, names, star):
        try:
            search_filter = "查詢條件："

            ## 特疾搜尋
            diseaseStr = {
                '1': "氣喘",
                '2': "急性心肌梗塞",
                '3': "糖尿病",
                '4': "人工膝關節手術",
                '5': "腦中風",
                '6': "鼻竇炎",
                '7': "子宮肌瘤手術",
                '8': "消化性潰瘍",
                '9': "血液透析",
                '10': "腹膜透析"
            }
            search_filter += diseaseStr.get(disease) + ', '
            ## 地點搜尋
            if county + township != '':
                search_filter += (county + township) + ', '
            ## 名稱搜尋
            for name in names:
                search_filter += name + ', '
            ## 層級搜尋
            for type in types:
                getStr = {
                    '1': "醫學中心",
                    '2': "區域醫院",
                    '3': "地區醫院",
                    '4': "診所"
                }
                search_filter += getStr.get(type) + ', '
            ## 評價結果
            if star != '':
                search_filter += star + "星以上, "


            ## 判斷是否有查詢條件
            ## 因為每個條件皆是以", "做結尾，因此不取查詢條件最後兩個位子
            if search_filter != "查詢條件：":
                search_filter = search_filter[:-2]
            else:
                search_filter = "無查詢條件。"
            return search_filter
        except:
            return "抱歉，操作失敗。[F]"

