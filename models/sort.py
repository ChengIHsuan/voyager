import sqlite3
from flask import Flask, request, render_template, flash , redirect

class Sort():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def reSort(self, selected_index, sql_where, item, search_filter):
        try:
            items = item.split("//")
            del items[-1]
            index_value = self.cursor.execute("select name from column_name where abbreviation = '" + selected_index + "'").fetchone()[0]
            index_level = index_value.replace('m.v_', 'm.l_')
            orderby = (" order by " + index_level + " DESC , " + index_value + " DESC")
            return Sort().add_sql_where(sql_where, items, search_filter, orderby)
        except:
            alert = "請選擇排序指標"
            return render_template("hospital.html", alert=alert)

    ## 加上所選標皆不為-1之條件
    def add_sql_where(self, sql_where, items, search_filter, orderby):
        str = ''
        for item in items:
            if item != items[-1]:
                str += '(' + item + '!= -1) OR '
            else:
                str += '(' + item + '!= -1)'
        ## 將condition改回，並加上指標皆不為-1之條件
        sql_where = sql_where.replace("//", " ") + ' AND (' + str + ')'
        return Sort().select_normal(sql_where, items, search_filter, orderby)

    def select_normal(self, sql_where, items, search_filter, orderby):
        sqlstr = "SELECT h.abbreviation,  cast(fr.star as float), fr.positive,  fr.negative, h.phone, h.address FROM hospitals h JOIN final_reviews fr ON h.id = fr.hospital_id join merge_data m ON h.id = m.hospital_id" + sql_where + orderby
        normal = self.cursor.execute(sqlstr).fetchall()
        ## 若未找到任何資料，出現錯誤訊息，若有則進入else
        if normal == []:
            flash('抱歉，找不到您要的資料訊息。')
            return render_template("hospital.html")
        else:
            return Sort().select_data2(normal, items, sql_where, search_filter, orderby)

    def select_data2(self, normal, items, sql_where, search_filter, orderby):
        deno_substr = 'm.hospital_id'
        level_substr = 'm.hospital_id'
        value_substr = 'm.hospital_id'
        for r in range(len(items)):
            value_substr += (', ' + items[r])
            level = items[r].replace('m.v_', 'm.l_')
            level_substr += (', ' + level)
            deno = items[r].replace('m.v_', 'm.m_')
            deno_substr += (', ' + deno)
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
        return Result().get_column_name(items, search_filter, sql_where, z_data)

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得欄位名稱
    def get_column_name(self, items, search_filter, sql_where, z_data):
        ## 先取得欄位的原始名字(m.m_?)，「醫院機構資訊」為固定欄位，直接手動新增
        getColumns = ['醫療機構資訊']
        for r in range(len(items)):
            getColumns.append(items[r])
        ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)
        columns = []
        for c in getColumns:
            columns.append(self.cursor.execute("SELECT abbreviation FROM column_name WHERE name = '" + c + "'").fetchone()[0])
        ## 建立full_name[]，存入欄位名稱(縮寫)的完整名字
        full_name = ['醫療機構資訊']
        for fn in columns:
            if fn != '醫療機構資訊':
                full_name.append(self.cursor.execute("SELECT name FROM indexes WHERE abbreviation = '" + fn + "'").fetchone()[0])
        ## 將欄位名稱、欄位詳細說明包裝成zip
        z_col = zip(columns, full_name)
        ## 選取的指標數量，-1是因為扣掉第一欄的醫療機構資訊
        ck_len = len(columns) - 1
        indexes = columns[1:]
        return Result().table(z_data, z_col, ck_len, search_filter, indexes, sql_where, items)

    ## 將搜尋結果寫進表格
    def table(self, z_data, z_col, ck_len, search_filter, indexes, sql_where, items):
        tmp_items = ''
        for r in range(len(items)):
            tmp_items += items[r] + '//'
        sql_where = sql_where.replace(' ', '//')
        tmp_filter = search_filter.replace(' ', '//')
        ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
        return render_template('hospital.html', scroll = 'results', ck_len=ck_len, z_col=z_col, z_data=z_data, search_filter=search_filter, tmp_filter=tmp_filter, indexes=indexes, sql_where=sql_where, tmp_items=tmp_items)