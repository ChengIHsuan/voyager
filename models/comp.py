import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search

class Comp():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def comp_hosp(self, county, township, names, types, star):
        try:
            reserved = Search().hosp_reserved(county, township, names, types, star)
            sql_where = ''
            ## 取得地區、名稱、層級、星等的condition
            area_condition = Search().search_area(county, township)
            name_condition = Search().search_name(names)
            type_condition = Search().search_type(types)
            reviews_condition = Search().search_star(star)
            conditions = [area_condition, name_condition, type_condition, reviews_condition]

            ## 若沒有條件則移除
            while '' in conditions:
                conditions.remove('')
            for condition in conditions:
                if condition.find('抱歉') != -1:     #若為錯誤訊息，以alert提示#
                    return render_template('search.html', alert=condition)
                else:
                    condition = '(' + condition + ')'  #若不為錯誤訊息則在條件句前後加上括號-->之後放在SQL中才不會出錯#
                    ## 將所有condition相接，若不為最後一個condition則加上'AND'
                    if condition != ( '(' + conditions[-1] + ')' ):
                        sql_where += condition + "AND "
                    else:
                        sql_where += condition
            if sql_where != '':
                sql_where = 'WHERE ' + sql_where
            return Select().select_normal(sql_where, reserved)
        except BaseException as e:
            print('search_all Exception' + e)
            return  render_template('search.hml')

class Select():
    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def select_normal(self, sql_where, reserved):
        try:
            ## select醫療機構資訊'：名稱、分數＆星等、正向評論數、負向評論數、電話與地址並存入normal[]
            sqlstr = "SELECT  h.abbreviation, cast(fr.star as float), fr.positive,  fr.negative, h.phone, h.address , h.id FROM hosp_subj s JOIN hospitals h ON s.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where
            normal = self.cursor.execute(sqlstr).fetchall()  ## normal = [ (名稱, GOOGLE星等, 正向評論數, 負向評論數, 電話, 地址), ......]

            ## 若未找到任何資料，出現錯誤訊息，若有則進入else
            if normal == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return Select().select_data(normal, sql_where, reserved)
        except BaseException as e:
            print('select_normal Exception' + e)
            return  render_template('search.hml')

    def select_data(self, normal, sql_where, reserved):
        try:
            ## 取得data指標值
            sqlstr = "SELECT cast(s.reviews as float), s.subj1, s.subj2, s.subj3, s.subj4, s.subj5, s.subj6, s.subj7 FROM hosp_subj s JOIN hospitals h ON s.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where
            value = self.cursor.execute(sqlstr).fetchall()  ## value = [(hospital_id, 評論數, 指標1之指標值, 指標2之指標值, 指標3之指標值, ......), ......]
            ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(normal, value)
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
            return Result().table(z_data, z_col, reserved)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return render_template('search.html')

    ## 將搜尋結果寫進表格
    def table(self, z_data, z_col, reserved):
        try:
            ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
            return render_template('hospComparison.html', reserved=reserved, z_col=z_col, z_data=z_data)
        except BaseException as e:
            print('table Exception' + e)
            return render_template('search.html')