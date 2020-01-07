import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search
from models.reserve import Reserve
from models.form import Form
from models.selectData import SelectData


class Hosp():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 保留搜尋條件、condition
    def search_hosp(self, county, township, names, types, star):
        try:
            ## 保留搜尋條件
            reserved = Reserve().hosp_reserved(county, township, names, types, star)
            ## 取得地區、名稱、層級、星等的condition
            area_condition = Search().search_area(county, township)
            name_condition = Search().search_name(names)
            type_condition = Search().search_type(types)
            reviews_condition = Search().search_star(star)
            ## 串接所有condition
            conditions = [area_condition, name_condition, type_condition, reviews_condition]
            sql_where = Form().form_sqlwhere(conditions)
            return Select().select_info(sql_where, reserved)
        except BaseException as e:
            print('search_all Exception' + e)
            return  render_template('search.html')

    ##【找醫療機構-->客觀指標】頁面資訊
    def search_obj(self, hospital_id, indexes):
        try:
            ## 取得醫療機構資訊
            hosp_info = SelectData().hosp_info(hospital_id)
            ## 用共用程式取得客觀指標資訊，首參數用來分辨資訊(v為指標值、d為就醫人數、l為指標值等級)
            value = SelectData().hosp_obj_data('v', indexes, hospital_id)
            deno = SelectData().hosp_obj_data('d', indexes, hospital_id)
            level = SelectData().hosp_obj_data('l', indexes, hospital_id)
            ## 將指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(value, deno, level)
            return Result().get_obj_column_name(indexes, hosp_info, z_data, hospital_id)
        except:
            alert = "抱歉，找不到您要的資料訊息。"
            hosp_info = Search().search_hosp(hospital_id)
            return render_template('hospObjResult.html', hosp_info=hosp_info, alert=alert)

    ##【找醫療機構-->主觀指標】頁面資訊
    def search_subj(self, hospital_id, subjectives):
        try:
            ## 取得醫療機構資訊
            hosp_info = SelectData().hosp_info(hospital_id)
            ## 取得主觀指標資訊
            data = SelectData().hosp_subj_data(subjectives, hospital_id)
            return Result().get_subj_column_name(subjectives, hosp_info, data, hospital_id)
        except:
            alert = "抱歉，找不到您要的資料訊息。"
            hosp_info = SelectData().hosp_info(hospital_id)
            return render_template('hospSubjResult.html', hosp_info=hosp_info, alert=alert)

class Select():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得符合使用者選擇條件之醫療機構資訊
    def select_info(self, sql_where, reserved):
        try:
            ## SELECT醫療機構資訊：名稱、醫院層級、分數＆星等、評論數、電話、地址、醫療機構ID
            sqlstr = "SELECT h.abbreviation, h.type, cast(fr.star as float), fr.reviews, h.phone, h.address, h.id FROM hospitals h JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where
            hosp_info = self.cursor.execute(sqlstr).fetchall()
            ## 若未找到任何資料，出現錯誤訊息，若有則進入else
            if hosp_info == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return render_template("hospResult.html", hosp_info=hosp_info, reserved=reserved)
        except BaseException as e:
            print('select_info Exception' + e)
            return  render_template('search.html')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ##【找醫療機構-->客觀指標】取得欄位名稱
    def get_obj_column_name(self, indexes, hosp_info, z_data, hospital_id):
        try:
            ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)、正負向指標註記、指標說明
            columns = []
            for index in indexes:
                sqlstr = ("SELECT abbreviation, PorN, description FROM column_name WHERE name = '{}' ".format(index))
                columns.append(self.cursor.execute(sqlstr).fetchall()[0])
            ## 供前端使用之參數：選取的指標數量
            col_len = len(columns)
            return render_template('hospObjResult.html', scroll='indexes', hosp_info=hosp_info, z_data=z_data, columns=columns,col_len=col_len)
        except:
            alert = "抱歉，找不到您要的資料訊息。"
            hosp_info = Search().search_hosp(hospital_id)
            return render_template('hospObjResult.html', hosp_info=hosp_info, alert=alert)

    ##【找醫療機構-->主觀指標】取得欄位名稱
    def get_subj_column_name(self, subjectives, hosp_info, data, hospital_id):
        try:
            ## 建立columns[]並手動加入"科別"，存入從資料庫中取得的欄位名稱(縮寫)
            columns = ['科別']
            for subjective in subjectives:
                sqlstr = ("SELECT abbreviation FROM column_name WHERE name = 's{}' ").format(subjective)
                columns.append(self.cursor.execute(sqlstr).fetchone()[0])
            ## 供前端使用之參數：選取的指標數量，-1是因為扣掉第一欄的科別欄位
            col_len = len(columns) - 1
            return render_template('hospSubjResult.html', scroll='results', hosp_info=hosp_info, data=data, columns=columns,col_len=col_len)
        except:
            alert = "抱歉，找不到您要的資料訊息。"
            hosp_info = hosp_info(hospital_id)
            return render_template('hospSubjResult.html', hosp_info=hosp_info, alert=alert)