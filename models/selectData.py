import sqlite3

class SelectData():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 【首頁 / 找醫療機構 / 醫療機構主客觀指標】頁面醫療機構資訊
    def hosp_info(self, hospital_id):
        try:
            sqlstr = "SELECT h.id, h.abbreviation, h.type, CAST(fr.star AS FLOAT), fr.reviews, h.address, h.phone FROM hospitals h JOIN final_reviews fr ON h.id = fr.hospital_id WHERE h.id={}".format(
                hospital_id)
            hosp_info = self.cursor.execute(sqlstr).fetchone()
            return hosp_info
        except:
            return "抱歉，操作失敗。[H]"

    ## 取得使用者選擇指標之資訊，以type分辨資訊(v為指標值、d為就醫人數、l為指標值等級)
    def disease_data(self, type, indexes, sql_where, hosp_info):
        ## substr為需SELECT之欄位，substr = '醫院ID,  選擇指標1資訊, 選擇指標2資訊, 選擇指標3資訊...'
        substr = 'm.hospital_id'
        for index in indexes:
            substr += (', m.{}_{}').format(type, index)
        ## data為符合條件之資料(未依預設排序方式排序)
        sqlstr = ("SELECT {} FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id {}").format(substr,sql_where)
        data = self.cursor.execute(sqlstr).fetchall()
        ## 調整資料順序(hosp_info中資料已按照星等排序，且就醫人數未達30不排序)
        list_data = []
        for info in hosp_info:
            for d in data:
                if info[6] == d[0]:
                    list_data.append(d)
        return list_data


    def reSort_data(self, type, indexes, sql_where):
        ## substr為需SELECT之欄位，substr = '醫院ID,  選擇指標1資訊, 選擇指標2資訊, 選擇指標3資訊...'
        substr = 'm.hospital_id'
        for index in indexes:
            substr += (', m.{}_{}').format(type, index)
        ## data為符合條件之資料(未依預設排序方式排序)
        sqlstr = ("SELECT {} FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id {}").format(
            substr, sql_where)
        data = self.cursor.execute(sqlstr).fetchall()
        return data


    def depart_data(self, indexes, sql_where):
        substr = 's.hospital_id'
        for index in indexes:
            substr += (', s.subj{}').format(index)
        ## 取得data指標值
        sqlstr = ("SELECT {} FROM dept_subj s LEFT JOIN hospitals h ON s.hospital_id = h.id {}").format(substr, sql_where)
        data = self.cursor.execute(sqlstr).fetchall()
        return data


    def hosp_obj_data(self, type, indexes, hospital_id):
        substr = ''
        for index in indexes:
            if index != indexes[-1]:
                substr += ('m.{}_{}, ').format(type, index)
            else:
                substr += ('m.{}_{}').format(type, index)
        sqlstr = ("SELECT {} FROM merge_data m WHERE m.hospital_id = {}").format(substr, hospital_id)
        data = self.cursor.execute(sqlstr).fetchone()
        return data


    def hosp_subj_data(self, subjectives, hospital_id):
        substr = 'd.name'
        for subjective in subjectives:
            substr += (', ds.subj{}').format(subjective)
        sqlstr = ("SELECT {} FROM dept_subj ds LEFT JOIN depart d ON ds.depart_id = d.id WHERE hospital_id = {}").format(substr, hospital_id)
        data = self.cursor.execute(sqlstr).fetchall()
        return data