import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search
from models.form import Form
from models.reserve import Reserve

class Doc():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 保留條件、condition
    def search_doctor(self, doctor, depart, names):
        try:
            ## 保留搜尋條件、condition
            reserved = Reserve().doc_reserved(doctor, depart, names)
            ## 取得醫師、科別、醫療機構名稱的condition
            doctor_condition = Search().search_doctor(doctor)
            depart_condition = Search().search_depart(depart)
            name_condition = Search().search_name(names)
            ## 串接所有condition
            conditions = [depart_condition, name_condition, doctor_condition]
            sql_where = Form().form_sqlwhere(conditions)
            return Select().select_info(sql_where, reserved)
        except BaseException as e:
            print('search_doctor Exception' + e)
            return  render_template('search.html')

class Select():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得符合使用者選擇條件之醫師
    def select_info(self, sql_where, reserved):
        try:
            ## SELECT醫師資訊：醫師姓名、醫療機構名稱(縮寫)、科別名稱、相關評論數
            sqlstr = "SELECT s.doctor, h.abbreviation, d.name, s.reviews FROM hospitals h JOIN doctor_subj s ON h.id = s.hospital_id JOIN depart d ON s.depart_id = d.id " + sql_where
            doc_info = self.cursor.execute(sqlstr).fetchall()
            ## 若無資料顯示錯誤訊息
            if doc_info == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return Select().select_data(doc_info, sql_where, reserved)
        except BaseException as e:
            print('select_normal Exception' + e)
            return  render_template('search.html')

    ## 取得指標資訊
    def select_data(self, doc_info, sql_where, reserved):
        try:
            ## SELECT七個主觀指標值
            sqlstr = "SELECT s.subj1, s.subj2, s.subj3, s.subj4, s.subj5, s.subj6, s.subj7 FROM hospitals h JOIN doctor_subj s ON h.id = s.hospital_id JOIN depart d ON s.depart_id = d.id " +sql_where
            value = self.cursor.execute(sqlstr).fetchall()
            ## 將醫師資訊、指標值包裝成zip
            z_data = zip(doc_info, value)
            return Result().get_column_name(z_data, sql_where, reserved)
        except BaseException as e:
            print('select_data Exception' + e)
            return  render_template('search.html')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()
    ## 取得欄位名稱
    def get_column_name(self, z_data, sql_where, reserved):
        try:
            getColumns = ['doctor', 's1', 's2', 's3', 's4', 's5', 's6', 's7']
            ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)
            columns = []
            for c in getColumns:
                sqlstr = ("SELECT abbreviation FROM column_name WHERE name = '{}'").format(c)
                column = self.cursor.execute(sqlstr).fetchone()[0]
                columns.append(column)
            ## 供前端使用之參數：選取的指標數量，-1是因為扣掉第一欄的醫師資訊
            col_len = len(columns) -1
            return render_template('doctorResult.html', z_data=z_data, columns=columns, col_len=col_len, reserved=reserved)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return  render_template('search.html')