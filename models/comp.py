import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search
from models.reserve import Reserve
from models.form import Form

class Comp():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def comp_hosp(self, county, township, names, types, star):
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
            return  render_template('search.hml')

class Select():
    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def select_info(self, sql_where, reserved):
        try:
            ## select醫療機構資訊'：名稱、分數＆星等、正向評論數、負向評論數、電話、地址、醫療機構ID
            sqlstr = "SELECT  h.abbreviation, cast(fr.star as float), fr.positive,  fr.negative, h.phone, h.address , h.id FROM hosp_subj s JOIN hospitals h ON s.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where
            hosp_info = self.cursor.execute(sqlstr).fetchall()
            ## 若未找到任何資料，出現錯誤訊息，若有則進入else
            if hosp_info == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return Select().select_data(hosp_info, sql_where, reserved)
        except BaseException as e:
            print('select_normal Exception' + e)
            return  render_template('search.hml')

    def select_data(self, hosp_info, sql_where, reserved):
        try:
            ## 取得主觀指標值
            sqlstr = "SELECT cast(s.reviews as float), s.subj1, s.subj2, s.subj3, s.subj4, s.subj5, s.subj6, s.subj7 FROM hosp_subj s JOIN hospitals h ON s.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where
            value = self.cursor.execute(sqlstr).fetchall()  ## value = [(hospital_id, 評論數, 指標1之指標值, 指標2之指標值, 指標3之指標值, ......), ......]
            ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(hosp_info, value)
            return Result().get_column_name(z_data, sql_where, reserved)
        except BaseException as e:
            print('select_data Exception' + e)
            return  render_template('search.hml')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得欄位名稱
    def get_column_name(self, z_data, sql_where, reserved):
        try:
            ## 先取得欄位的原始名字(m.v_?)，「醫院機構資訊」為固定欄位，直接手動新增
            getColumns=['醫療機構資訊', 's1', 's2', 's3', 's4', 's5', 's6', 's7']
            ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)
            columns = []
            full_name = []  ## 建立full_name[]，存入欄位名稱(縮寫)的完整名字、指標解釋
            for c in getColumns:
                columns.append(self.cursor.execute("SELECT abbreviation FROM column_name WHERE name = '" + str(c) + "'").fetchone()[0])
                full_name.append(self.cursor.execute("SELECT description FROM column_name WHERE name = '" + str(c) + "'").fetchone()[0])
            ## 將欄位名稱、欄位詳細說明包裝成zip
            z_col = zip(columns, full_name)
            return render_template('hospComparison.html', reserved=reserved, z_col=z_col, z_data=z_data)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return render_template('search.html')