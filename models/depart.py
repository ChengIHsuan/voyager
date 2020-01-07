import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search
from models.form import Form
from models.reserve import Reserve
from models.selectData import SelectData


class Subj():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 保留搜尋條件、condition
    def search_depart(self, depart_id, indexes, county, township, types, names):
        try:
            ## 保留搜尋條件
            reserved = Reserve().depart_reserved(depart_id, county, township, types, names)
            ## 取得科別、地區、名稱、層級的condition
            depart_condition = Search().search_depart(depart_id)
            area_condition = Search().search_area(county, township)
            name_condition = Search().search_name(names)
            type_condition = Search().search_type(types)
            ## 串接所有condition
            conditions = [depart_condition, area_condition, name_condition, type_condition]
            sql_where = Form().form_sqlwhere(conditions)
            return Select().select_info(indexes, sql_where, reserved)
        except BaseException as e:
            print('search_subj Exception' + e)
            return  render_template('search.html')


class Select():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得醫療機構資訊
    def select_info(self, indexes, sql_where, reserved):
        try:
            ## SELECT醫療機構資訊：名稱、分數＆星等、正向評論數、負向評論數、電話與地址
            sqlstr = "SELECT h.abbreviation, cast(fr.star as float), s.reviews, h.phone, h.address FROM  hospitals h  JOIN final_reviews fr ON h.id = fr.hospital_id  JOIN dept_subj s ON h.id = s.hospital_id " + sql_where
            hosp_info = self.cursor.execute(sqlstr).fetchall()
            ## 若未找到任何資料，出現錯誤訊息，若有則進入else
            if hosp_info == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return Select().select_data(hosp_info, indexes, sql_where, reserved)
        except BaseException as e:
            print('select_info Exception' + e)
            return render_template('search.html')

    ## 取得使用者勾選的資訊
    def select_data(self, hosp_info, indexes, sql_where, reserved):
        try:
            ## 取得客觀指標值資訊
            data = SelectData().depart_data(indexes, sql_where)
            ## 將醫療機構資訊、指標值包裝成zip
            z_data = zip(hosp_info, data)
            return Result().get_column_name(indexes, z_data, sql_where, reserved)
        except BaseException as e:
            print('select_data Exception' + e)
            return render_template('search.html')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得欄位名稱
    def get_column_name(self, indexes, z_data, sql_where, reserved):
        try:
            ## 「醫院機構資訊」為固定欄位，直接手動新增
            getColumns=['醫療機構資訊']
            for index in indexes:
                getColumns.append('s{}'.format(index))
            ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)、正負向指標註記、指標說明
            columns = []
            for c in getColumns:
                column = self.cursor.execute("SELECT abbreviation, PorN, description FROM column_name WHERE name = '{}'".format(str(c))).fetchall()[0]
                columns.append(column)
            ## 供前端使用之參數：選取的指標數量，-1是因為扣掉第一欄的醫療機構資訊
            col_len = len(columns) - 1
            return render_template('departResult.html', reserved=reserved, col_len=col_len, columns=columns, z_data=z_data, sql_where=sql_where)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return render_template('search.html')