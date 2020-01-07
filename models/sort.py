import sqlite3
from flask import Flask, request, render_template, flash , redirect
from models.selectData import SelectData


class Sort():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 判斷正負向指標，產出ORDER BY條件
    def reSort(self, selected_index, sql_where, tmp_indexes, reserved):
        try:
            indexes = tmp_indexes.split("//")
            del indexes[-1]
            ## 判斷正面或是負面指標
            P_or_N = self.cursor.execute("SELECT P_or_N FROM indexes WHERE id = {}".format(selected_index)).fetchone()[0]
            ## 若為正向指標按value降序排列，若為負向指標先按level降序，再按value升序
            if P_or_N == 'P':  #正向指標：value越大越好#
                orderby = (" ORDER BY m.v_{} DESC").format(selected_index)
            elif P_or_N == 'N':  #負向指標：value越小越好#
                orderby = (" ORDER BY m.l_{} DESC, m.v_{} ASC").format(selected_index, selected_index)
            return Sort().select_info(indexes, sql_where, orderby, reserved)
        except BaseException as e:
            print('reSort Exception' + e)
            return  render_template('search.html')

    ## 取得醫療機構資訊
    def select_info(self, indexes, sql_where, orderby, reserved):
        try:
            ## SELECT醫療機構資訊：名稱、分數＆星等、正向評論數、負向評論數、電話與地址
            sqlstr = "SELECT  h.abbreviation, CAST(fr.star AS FLOAT), fr.positive,  fr.negative, h.phone, h.address FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where + orderby
            hosp_info = self.cursor.execute(sqlstr).fetchall()
            return Sort().select_data(hosp_info, indexes, sql_where, orderby, reserved)
        except BaseException as e:
            print('select_info Exception' + e)
            return render_template('search.html')

    ## 取得指標資訊
    def select_data(self, hosp_info, indexes, sql_where, orderby, reserved):
        try:
            ## 用共用程式取得指標資訊，首參數用來分辨資訊(v為指標值、d為就醫人數、l為指標值等級)
            value = SelectData().reSort_data('v', indexes, sql_where + orderby)
            deno = SelectData().reSort_data('d', indexes, sql_where + orderby)
            level = SelectData().reSort_data('l', indexes, sql_where + orderby)
            ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(hosp_info, value, deno, level)
            return Result().get_column_name(indexes, sql_where, z_data, reserved)
        except BaseException as e:
            print('selct_data2 Exception' + e)
            return render_template('search.html')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得欄位名稱
    def get_column_name(self, indexes, sql_where, z_data, reserved):
        try:
            ## 「醫院機構資訊」為固定欄位，直接手動新增
            getColumns = ['醫療機構資訊']
            for index in indexes:
                getColumns.append(index)
            ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)、正負向指標註記(用以判斷排序方式)、指標說明
            columns = []
            ## 建立sort_indexes[]，存入使用者可選擇之排序指標欄位名稱(縮寫)
            sort_indexes = []

            for c in getColumns:
                sqlstr = ("SELECT abbreviation, PorN, description FROM column_name WHERE name = '{}'").format(str(c))
                column = self.cursor.execute(sqlstr).fetchall()[0]
                columns.append(column)
                sort_indexes.append(column[0])

            ## 供前端使用之參數：選取的指標數量，-1是因為扣掉第一欄的醫療機構資訊
            ck_len = len(columns) - 1
            ## sort_indexes第一個為【醫療機構資訊】，不列入排序選項
            del sort_indexes[0]
            return Result().hidden(z_data, columns, ck_len, indexes, sql_where, sort_indexes, reserved)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return  render_template('search.html')

    ## 整理需暫存於前端隱藏欄位資訊
    def hidden(self, z_data, columns, ck_len, indexes, sql_where, sort_indexes, reserved):
        try:
            ## 將使用者選擇指標寫成字串，暫存於前端隱藏欄位，用於重新排序(reSort)
            tmp_indexes = ''
            for index in indexes:
                tmp_indexes += index + '//'
            ## 將使用者選擇條件寫成字串，暫存於前端隱藏欄位，用於重新排序(reSort)
            ## 將空白號替換成//，避免被截斷
            sql_where = sql_where.replace(' ', '//')
            z_indexes = zip(indexes, sort_indexes)
            reserved = (reserved[1:-1].replace("'", "")).split(', ')
            ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
            return render_template('diseaseResult.html', scroll='results', reserved=reserved, ck_len=ck_len, columns=columns, z_data=z_data, sql_where=sql_where, tmp_indexes=tmp_indexes, z_indexes=z_indexes)
        except BaseException as e:
            print('table Exception' + e)
            return  render_template('search.html')