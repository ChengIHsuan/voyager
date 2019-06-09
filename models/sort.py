import sqlite3
from flask import Flask, request, render_template, flash , redirect

class Sort():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def reSort(self, selected_index, sql_where, tmp_indexes, reserved):
        try:
            indexes = tmp_indexes.split("//")
            del indexes[-1]
            index_value = 'm.v_' + selected_index  ##m.v_100##
            index_level = 'm.l_' + selected_index  ##m.l_100##
            P_or_N = self.cursor.execute("SELECT P_or_N FROM indexes WHERE id = " + selected_index).fetchone()[0]
            ## 判斷正面或是負面指標
            if P_or_N == 'P':  ## 正面指標降序排列
                orderby = (" order by " + index_value + " DESC")
            elif P_or_N == 'N':  ## 負面指標升序排列
                orderby = (" order by " + index_level + " DESC, " + index_value + " ASC")
            return Sort().select_data2(indexes, sql_where, orderby, reserved)
        except BaseException as e:
            print('reSort Exception' + e)
            return  render_template('search.hml')

    def form_substr(self, nvdl, indexes, sql_where, orderby):
        try:
            nvdlStr = {
                'normal': "h.abbreviation, cast(fr.star as float), fr.positive, fr.negative, h.phone, h.address",
                'value': "m.v_",
                'deno': "m.d_",
                'level': "m.l_"
            }

            if nvdl != 'normal':
                substr = 'm.hospital_id'
                for r in range(len(indexes)):
                    substr += (', ' + nvdlStr.get(nvdl) + indexes[r])
            else:
                substr = nvdlStr.get(nvdl)

            sqlstr = "SELECT {} FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id ".format(substr) + sql_where + orderby
            data = self.cursor.execute(sqlstr).fetchall()
            return data
        except BaseException as e:
            print('form_substr Exception' + e)
            return  render_template('search.hml')

    def select_data2(self, indexes, sql_where, orderby, reserved):
        try:
            normal = Sort().form_substr('normal', indexes, sql_where, orderby)
            value = Sort().form_substr('value', indexes, sql_where, orderby)
            deno = Sort().form_substr('deno', indexes, sql_where, orderby)
            level = Sort().form_substr('level', indexes, sql_where, orderby)
            ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(normal, value, deno, level)
            return Result().get_column_name(indexes, sql_where, z_data, reserved)
        except BaseException as e:
            print('selct_data2 Exception' + e)
            return  render_template('search.hml')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得欄位名稱
    def get_column_name(self, indexes, sql_where, z_data, reserved):
        try:
            ## 先取得欄位的原始名字(m.d.?)，「醫院機構資訊」為固定欄位，直接手動新增
            getColumns = ['醫療機構資訊']
            for index in indexes:
                getColumns.append(index)
            ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)
            columns = []
            sort_indexes = []
            for c in getColumns:
                column = self.cursor.execute("SELECT abbreviation, PorN, description FROM column_name WHERE name = '" + str(c) + "'").fetchall()[0]
                columns.append(column)
                sort_indexes.append(column[0])
            ## 選取的指標數量，-1是因為扣掉第一欄的醫療機構資訊
            ck_len = len(columns) - 1
            ## sort_indexes第一個為【醫療機構資訊】，不列入排序選項
            del sort_indexes[0]
            return Result().table(z_data, columns, ck_len, indexes, sql_where, sort_indexes, reserved)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return  render_template('search.hml')

    ## 將搜尋結果寫進表格
    def table(self, z_data, columns, ck_len, indexes, sql_where, sort_indexes, reserved):
        try:
            tmp_indexes = ''
            for r in range(len(indexes)):
                tmp_indexes += indexes[r] + '//'
            sql_where = sql_where.replace(' ', '//')
            z_indexes = zip(indexes, sort_indexes)
            reserved = (reserved[1:-1].replace("'", "")).split(', ')
            ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
            return render_template('diseaseResult.html', scroll='results', reserved=reserved, ck_len=ck_len, columns=columns, z_data=z_data, sql_where=sql_where, tmp_indexes=tmp_indexes, z_indexes=z_indexes)
        except BaseException as e:
            print('table Exception' + e)
            return  render_template('search.hml')