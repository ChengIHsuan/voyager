import sqlite3
from flask import Flask, request, render_template, flash , redirect

class Sort():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def reSort(self, selected_index, sql_where, tmp_indexes, reserved):
        # try:
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
        print(orderby)
        return Sort().select_normal(sql_where, indexes, orderby, reserved)
        # except:
        #     alert = "請選擇排序指標"
        #     return render_template("diseaseResult.html", alert=alert)

    ## 加上所選標皆不為-1之條件
    # def add_sql_where(self, sql_where, indexes, search_filter, orderby):
    #     print('add')
    #     try:
    #         str = ''
    #         for index in indexes:
    #             if index != indexes[-1]:
    #                 str += '(m.v_' + index + ' != -1) OR '
    #             else:
    #                 str += '(m.v_' + index + ' != -1)'
    #         ## 將condition改回，並加上指標皆不為-1之條件
    #         sql_where += ' AND (' + str + ')'
    #         print(sql_where)
    #         return Sort().select_normal(indexes, sql_where, search_filter, orderby)
    #     except:
    #         alert = "請選擇指標。"
    #         return render_template('diseaseResult.html', alert=alert)

    def select_normal(self, sql_where, indexes, orderby, reserved):
        sqlstr = "SELECT h.abbreviation, cast(fr.star as float), fr.positive, fr.negative, h.phone, h.address FROM hospitals h JOIN final_reviews fr ON h.id = fr.hospital_id join merge_data m ON h.id = m.hospital_id " + sql_where + orderby
        normal = self.cursor.execute(sqlstr).fetchall()
        ## 若未找到任何資料，出現錯誤訊息，若有則進入else
        if normal == []:
            flash('抱歉，找不到您要的資料訊息。')
            return render_template("diseaseResult.html")
        else:
            return Sort().select_data2(normal, indexes, sql_where, orderby, reserved)

    def select_data2(self, normal, indexes, sql_where, orderby, reserved):
        value_substr = 'm.hospital_id'
        deno_substr = 'm.hospital_id'
        level_substr = 'm.hospital_id'
        for r in range(len(indexes)):
            value_substr += (', ' + 'm.v_' + indexes[r])
            level_substr += (', ' + 'm.l_' + indexes[r])
            deno_substr += (', ' + 'm.d_' + indexes[r])
        ## 取得data指標值
        sqlstr = "SELECT " + value_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where + orderby
        l_value = self.cursor.execute(sqlstr).fetchall()
        ## 取得data分母(就醫人數)
        sqlstr = "SELECT " + deno_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where + orderby
        l_deno = self.cursor.execute(sqlstr).fetchall()
        ## 取得data指標值等級
        sqlstr = "SELECT " + level_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where + orderby
        l_level = self.cursor.execute(sqlstr).fetchall()
        ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
        z_data = zip(normal, l_value, l_deno, l_level)
        return Result().get_column_name(indexes, sql_where, z_data, reserved)

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得欄位名稱
    def get_column_name(self, indexes, sql_where, z_data, reserved):
        ## 先取得欄位的原始名字(m.d.?)，「醫院機構資訊」為固定欄位，直接手動新增
        getColumns = ['醫療機構資訊']
        for r in range(len(indexes)):
            getColumns.append(indexes[r])
        ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)
        columns = []
        PorN = []
        for c in getColumns:
            columns.append(self.cursor.execute("SELECT abbreviation FROM column_name WHERE name = '" + c + "'").fetchone()[0])
            PorN.append(self.cursor.execute("SELECT PorN FROM column_name WHERE name = '" + str(c) + "'").fetchone()[0])
        ## 建立full_name[]，存入欄位名稱(縮寫)的完整名字
        full_name = ['醫療機構資訊']
        for fn in columns:
            if fn != '醫療機構資訊':
                full_name.append(self.cursor.execute("SELECT name FROM indexes WHERE abbreviation = '" + fn + "'").fetchone()[0])
        ## 將欄位名稱、欄位詳細說明包裝成zip
        z_col = zip(columns, PorN, full_name)
        ## 選取的指標數量，-1是因為扣掉第一欄的醫療機構資訊
        ck_len = len(columns) - 1
        sort_indexes = columns[1:]
        return Result().table(z_data, z_col, ck_len, indexes, sql_where, sort_indexes, reserved)

    ## 將搜尋結果寫進表格
    def table(self, z_data, z_col, ck_len, indexes, sql_where, sort_indexes, reserved):
        tmp_indexes = ''
        for r in range(len(indexes)):
            tmp_indexes += indexes[r] + '//'
        sql_where = sql_where.replace(' ', '//')
        z_indexes = zip(indexes, sort_indexes)
        reserved = (reserved[1:-1].replace("'", "")).split(', ')
        print(reserved)
        ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
        return render_template('diseaseResult.html', scroll='results', reserved=reserved, ck_len=ck_len, z_col=z_col, z_data=z_data, sql_where=sql_where, tmp_indexes=tmp_indexes, z_indexes=z_indexes)