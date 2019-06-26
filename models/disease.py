import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search

class Disease():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 綜合搜尋
    def search_all(self, disease, county, township, types, names, star, indexes):
        try:
            ## 保留搜尋條件
            reserved = Search().disease_reserved(disease, county, township, names, types, star)
            reserved.append(Search().search_disease(disease))
            sql_where = ''
            ## 取得地區、名稱、層級、星等的condition
            area_condition = Search().search_area(county, township)
            name_condition = Search().search_name(names)
            type_condition = Search().search_type(types)
            reviews_condition = Search().search_star(star)
            conditions = [area_condition, name_condition, type_condition, reviews_condition]
            while '' in conditions: #若沒有條件則移除#
                conditions.remove('')

            ## 判斷condition是否有錯誤訊息
            for condition in conditions:
                if condition.find('抱歉') != -1:  #若為錯誤訊息，以alert提示#
                    return render_template('search.html', alert=condition)
                else:
                    condition = '(' + condition + ')'   #若不為錯誤訊息則在條件句前後加上括號(之後放在SQL中才不會出錯)#
                    ## 將所有condition相接，若不為最後一個condition則加上'AND'
                    if condition != ( '(' + conditions[-1] + ')' ):
                        sql_where += condition + "AND "
                    else:
                        sql_where += condition

            ## sql_where
            if sql_where != '':
                sql_where = 'WHERE ' + sql_where
            return Select().exclude_none_data(indexes, sql_where, reserved)
        except BaseException as e:
            print('search_all Exception' + e)
            return  render_template('search.hml')

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
                    str += '(m.v_' + index + ' != -1) OR '
                else:
                    str += '(m.v_' + index + ' != -1)'
            ## 將condition加上所有指標不能皆為-1之條件
            sql_where += ' AND (' + str + ')'
            return Select().select_normal(indexes, sql_where, reserved)
        except BaseException as e:
            print('exclude_none_data Exception' + e)
            return render_template('search.html')

    ## 取得醫療機構資訊
    def select_normal(self, indexes, sql_where, reserved):
        try:
            deno_substr = ""
            for r in range(len(indexes)):
                # 截取merge_data分母數字
                deno = ("substr(d_" + indexes[r] + ", instr(d_" + indexes[r] + ", '：') + 1, length(d_" + indexes[
                    r] + ") - instr(d_" + indexes[r] + ", '：') - 1)")
                if indexes[r] == indexes[-1]:
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
                    boolean.append("None")
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

            ## select醫療機構資訊'：名稱、分數＆星等、正向評論數、負向評論數、電話與地址並存入normal[]
            sqlstr = "SELECT  h.abbreviation, cast(fr.star as float), fr.positive,  fr.negative, h.phone, h.address , h.id FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where + " order by cast(fr.star as float) DESC"
            f = self.cursor.execute(sqlstr).fetchall()  ## normal = [ (名稱, GOOGLE星等, 正向評論數, 負向評論數, 電話, 地址), ......]
            # 把分母排好的順序跟醫療機構資訊對醫院id
            normal = []
            for k in range(len(True_only)):
                for n in range(len(f)):
                    if True_only[k][0] == f[n][6]:
                        normal.append(f[n])
            ## 若未找到任何資料，出現錯誤訊息，若有則進入else
            if normal == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return Select().select_data(normal, indexes, sql_where, reserved)
        except BaseException as e:
            print('select_normal Exception' + e)
            return render_template('search.html')

    ## 取得使用者勾選的資訊
    def select_data(self, normal, indexes, sql_where, reserved):
        try:
            value_substr = 'm.hospital_id'
            deno_substr = 'm.hospital_id'
            level_substr = 'm.hospital_id'
            for r in range(len(indexes)):
               value_substr += (', ' + 'm.v_' + indexes[r])
               level_substr += (', ' + 'm.l_' + indexes[r])
               deno_substr += (', ' + 'm.d_' + indexes[r])
            ## 取得data指標值
            sqlstr = "SELECT " + value_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where + " order by cast(fr.star as float) DESC"
            g = self.cursor.execute(sqlstr).fetchall()  ## l_value = [(hospital_id, 指標1之指標值, 指標2之指標值, 指標3之指標值, ......), ......]
            l_value = []
            for k in range(len(normal)):
                for n in range(len(g)):
                    if normal[k][6] == g[n][0]:
                        l_value.append(g[n])

            ## 取得data分母(就醫人數)
            sqlstr = "SELECT " + deno_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where + " order by cast(fr.star as float) DESC"
            z = self.cursor.execute(sqlstr).fetchall()
            l_deno = []
            for k in range(len(normal)):
                for n in range(len(z)):
                    if normal[k][6] == z[n][0]:
                        l_deno.append(z[n])

            ## 取得data指標值等級
            sqlstr = "SELECT " + level_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where + " order by cast(fr.star as float) DESC"
            y = self.cursor.execute(sqlstr).fetchall()
            l_level = []
            for k in range(len(normal)):
                for n in range(len(y)):
                    if normal[k][6] == y[n][0]:
                        l_level.append(y[n])

            ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(normal, l_value, l_deno, l_level)
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
            ## 先取得欄位的原始名字(m.v_?)，「醫院機構資訊」為固定欄位，直接手動新增
            getColumns=['醫療機構資訊']
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
            return render_template('search.html')

    ## 將搜尋結果寫進表格
    def table(self, z_data, columns, ck_len, indexes, sql_where, sort_indexes, reserved):
        try:
            tmp_indexes = ''
            for r in range(len(indexes)):
                tmp_indexes += indexes[r] + '//'
            sql_where = sql_where.replace(' ', '//')
            z_indexes = zip(indexes, sort_indexes)
            ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
            return render_template('diseaseResult.html', reserved=reserved, ck_len=ck_len, columns=columns, z_data=z_data, sql_where=sql_where, tmp_indexes=tmp_indexes, z_indexes=z_indexes)
        except BaseException as e:
            print('table Exception' + e)
            return render_template('search.html')