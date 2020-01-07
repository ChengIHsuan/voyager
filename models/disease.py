import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search
from models.form import Form
from models.reserve import Reserve
from models.selectData import SelectData


class Disease():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 保留搜尋條件、condition
    def search_all(self, disease_id, county, township, types, names, star, indexes):
        try:
            ## 保留搜尋條件
            reserved = Reserve().disease_reserved(disease_id, county, township, names, types, star)
            ## 取得地區、名稱、層級、星等的condition
            area_condition = Search().search_area(county, township)
            name_condition = Search().search_name(names)
            type_condition = Search().search_type(types)
            star_condition = Search().search_star(star)
            ## 串接所有condition
            conditions = [area_condition, name_condition, type_condition, star_condition]
            sql_where = Form().form_sqlwhere(conditions)
            return Select().exclude_none_data(indexes, sql_where, reserved)
        except BaseException as e:
            print('search_all Exception' + e)
            return  render_template('search.html')

class Select():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 排除所選指標皆為-1之資料
    def exclude_none_data(self, indexes, sql_where, reserved):
        try:
            ## 產生所有指標不能皆為-1之條件
            str = ''
            for index in indexes:
                if index != indexes[-1]:
                    str += '(m.v_{} != -1) OR '.format(index)
                else:
                    str += '(m.v_{} != -1)'.format(index)
            ## 將condition加上所有指標不能皆為-1之條件
            sql_where += ' AND (' + str + ')'
            return Select().default_star(indexes, sql_where, reserved)
        except BaseException as e:
            print('exclude_none_data Exception' + e)
            return render_template('search.html')

    ## 分母大於30之醫療機構按照星等排序，小於30不排序
    def default_star(self, indexes, sql_where, reserved):
        try:
            print(indexes)
            print(sql_where)
            deno_substr = ""
            for index in indexes:
                # 截取merge_data分母數字
                deno = ("substr(d_" + index + ", instr(d_" + index + ", '：') + 1, length(d_" + index + ") - instr(d_" + index + ", '：') - 1)")
                if index == indexes[-1]:
                    deno_substr += deno
                else:
                    deno_substr += (deno + ",")
            # 把所選的指標的分母按星等排序
            sqlstr = "SELECT h.id," + deno_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id order by cast(fr.star as float) DESC"
            deno_all = self.cursor.execute(sqlstr).fetchall()

            # 把醫院id存成list之後比對用
            hos_id = []
            # 存該醫院是否大於30
            boolean = []
            for k in range(len(deno_all)):
                i = 0
                hos_id.append(deno_all[k][0])
                for r in range(len(indexes)):
                    # 把沒分母的改成0
                    if deno_all[k][r + 1] == "（此指標無確切就醫人數":
                        new_deno = 0
                    else:
                        # 把資料全部轉成整數
                        new_deno = int(deno_all[k][r + 1])
                    if new_deno < 30:
                        i = i + 1
                if i == len(indexes):
                    boolean.append("False")
                else:
                    boolean.append("True")

            # 合併醫院id跟true false
            new_bool = []
            for ab in zip(hos_id, boolean):
                new_bool.append(ab)

            # 存只有true的
            True_only = []
            # 存只有false的
            False_only = []
            for k in range(len(new_bool)):
                if new_bool[k][1] == "True":
                    True_only.append(new_bool[k])
                else:
                    False_only.append(new_bool[k])

            # 合併成一個list
            True_only.extend(False_only)
            return Select().select_info(indexes, sql_where, reserved, True_only)
        except BaseException as e:
            print('default_star Exception' + e)
            return render_template('search.html')

    ## 取得符合使用者選擇條件之醫療機構資訊
    def select_info(self, indexes, sql_where, reserved, True_only):
        try:
            ## SELECT醫療機構資訊：名稱、分數＆星等、正向評論數、負向評論數、電話與地址
            sqlstr = "SELECT  h.abbreviation, CAST(fr.star AS FLOAT), fr.positive,  fr.negative, h.phone, h.address , h.id FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where
            org_info = self.cursor.execute(sqlstr).fetchall()
            # 把分母排好的順序跟醫療機構資訊對醫院id
            hosp_info = []
            for seq in True_only:
                for info in org_info:
                    if seq[0] == info[6]:
                        hosp_info.append(info)
            ## 若未找到任何資料，出現錯誤訊息，若有則進入else
            if hosp_info == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return Select().select_data(hosp_info, indexes, sql_where, reserved)
        except BaseException as e:
            print('select_info Exception' + e)
            return render_template('search.html')

    ## 取得使用者選擇的指標資訊
    def select_data(self, hosp_info, indexes, sql_where, reserved):
        try:
            ## 用共用程式取得指標資訊，首參數用來分辨資訊(v為指標值、d為就醫人數、l為指標值等級)
            value = SelectData().disease_data('v', indexes, sql_where, hosp_info)
            deno = SelectData().disease_data('d', indexes, sql_where, hosp_info)
            level = SelectData().disease_data('l', indexes, sql_where, hosp_info)
            ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(hosp_info, value, deno, level)
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
            return render_template('search.html')

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
            ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
            return render_template('diseaseResult.html', reserved=reserved, ck_len=ck_len, columns=columns, z_data=z_data, sql_where=sql_where, tmp_indexes=tmp_indexes, z_indexes=z_indexes)
        except BaseException as e:
            print('table Exception' + e)
            return render_template('search.html')