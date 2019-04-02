import sqlite3
from flask import Flask, request, render_template, flash, redirect

class Search():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 地點
    def search_area(self, county, township):
        try:
            area = county + township
            ## 依照使用者在前端輸入的條件寫成SQL字串中的condition
            sql_where = "h.area LIKE '%" + area + "%'"
            ## 驗證使用者是否輸入不存在的條件
            validate = self.cursor.execute("SELECT h.id FROM hospitals h WHERE " + sql_where).fetchall()
            if validate == []:
                return "抱歉，找不到您要的「{}{}」相關資訊。".format(county, township)
            else:
                return sql_where
        except:
            return "抱歉，操作失敗。[A]"

    ## 特殊疾病
    def search_disease(self, disease):
        try:
            ## 取得各疾病名稱
            getStr = {
                '1': "氣喘",
                '2': "急性心肌梗塞",
                '3': "糖尿病",
                '4': "人工膝關節手術",
                '5': "腦中風",
                '6': "鼻竇炎",
                '7': "子宮肌瘤手術",
                '8': "消化性潰瘍",
                '9': "血液透析",
                '10': "腹膜透析"
            }
            return getStr.get(disease)
        except:
            return "抱歉，操作失敗。[D]"

    ## 醫院層級
    def search_type(self, types):
        try:
            ## 建立一個tuple，使前端取回的type值可以對應正確的醫院層級
            getStr = {
                '1': "醫學中心",
                '2': "區域醫院",
                '3': "地區醫院",
                '4': "診所"
            }
            ## 建立一個SQL語法中condition的開頭字串
            sql_where = ''
            ## 對應正確的醫院層級後寫入condition字串中
            for type in types:
                ## 判斷若非陣列最後一個元素則加"OR"
                if type != types[-1]:
                    sql_where += "h.type = '" + getStr.get(type) + "' OR "
                else:
                    sql_where += "h.type = '" + getStr.get(type) + "'"
            return sql_where
        except:
            return "抱歉，操作失敗。[T]"

    ## 醫院名稱
    def search_name(self, names):
        try:
            ## 建立一個SQL語法中condition的開頭字串
            sql_where = ''
            ## 寫入condition字串中，對應全名或是縮寫
            for name in names:
                ## 檢查使用者輸入之名稱是否存在
                validate = self.cursor.execute("SELECT h.id FROM hospitals h WHERE h.name LIKE '%" + name + "%' OR h.abbreviation LIKE '%" + name + "%'").fetchall()
                if validate == []:
                    return "抱歉，找不到您要的「{}」相關資訊。".format(name)
                else:
                    ## 判斷若非陣列最後一個元素則加"OR"
                    if name != names[-1]:
                        sql_where += ("h.name LIKE '%" + name + "%' OR h.abbreviation LIKE '%" + name + "%' OR ")
                    else:
                        sql_where += ("h.name LIKE '%" + name + "%' OR h.abbreviation LIKE '%" + name + "%'")
            return sql_where
        except:
            return "抱歉，操作失敗。[N]"

    ## 評價結果
    def search_reviews(self, star):
        try:
            sql_where = ''
            if star != '':
                sql_where += "fr.star >= " + star + " AND fr.star != 'N/A' "
            # if positive != '':
            #     sql_where += "fr.positive >= " + positive + " AND fr.positive != 'N/A' AND "
            # if negative != '':
            #     sql_where += "fr.negative <= " + negative+ " AND "
            # sql_where = sql_where[:-4]
            return sql_where
        except:
            return "抱歉，操作失敗。[R]"

    ## 查詢條件
    def search_filter(self, county, township, disease, types, names, star):
        try:
            search_filter = "查詢條件："

            ## 特疾搜尋
            diseaseStr = {
                '1': "氣喘",
                '2': "急性心肌梗塞",
                '3': "糖尿病",
                '4': "人工膝關節手術",
                '5': "腦中風",
                '6': "鼻竇炎",
                '7': "子宮肌瘤手術",
                '8': "消化性潰瘍",
                '9': "血液透析",
                '10': "腹膜透析"
            }
            search_filter += diseaseStr.get(disease) + ', '
            ## 地點搜尋
            if county + township != '':
                search_filter += (county + township) + ', '
                ## 名稱搜尋
                for name in names:
                    search_filter += name + ', '
            ## 層級搜尋
            for type in types:
                getStr = {
                    '1': "醫學中心",
                    '2': "區域醫院",
                    '3': "地區醫院",
                    '4': "診所"
                }
                search_filter += getStr.get(type) + ', '
            ## 評價結果
            if star != '':
                search_filter += star + "星以上, "

            ## 判斷是否有查詢條件
            ## 因為每個條件皆是以", "做結尾，因此不取查詢條件最後兩個位子
            if search_filter != "查詢條件：":
                search_filter = search_filter[:-2]
            else:
                search_filter = "無查詢條件。"
            return search_filter
        except:
            return "抱歉，操作失敗。[F]"

    ## 綜合搜尋
    def search_all(self, county, township, disease, types, names, star, indexes):
        try:
            ## 取得查詢條件
            search_filter = Search().search_filter(county, township, disease, types, names, star)
            ##########
            sql_where = ''
            ## 取得地區、名稱、層級、星等的condition
            area_condition = Search().search_area(county, township)
            name_condition = Search().search_name(names)
            type_condition = Search().search_type(types)
            reviews_condition = Search().search_reviews(star)

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
            return Select().add_sql_where(indexes, sql_where, search_filter)
        except BaseException as e:
            print('search_all Exception' + e)
            return  render_template('search.hml')

class Select():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 加上所選標皆不為-1之條件
    def add_sql_where(self, indexes, sql_where, search_filter):
        try:
            str = ''
            for index in indexes:
                if index != indexes[-1]:
                    str += '(m.v_' + index + ' != -1) OR '
                else:
                    str += '(m.v_' + index + ' != -1)'
            ## 將condition改回，並加上指標皆不為-1之條件
            sql_where += ' AND (' + str + ')'
            return Select().select_normal(indexes, sql_where, search_filter)
        except BaseException as e:
            print('add_sql_where Exception' + e)
            return render_template('search.html')

    ## 取得醫療機構資訊
    def select_normal(self, indexes, sql_where, search_filter):
        try:
            ## select醫療機構資訊'：名稱、分數＆星等、正向評論數、負向評論數、電話與地址並存入normal[]
            sqlstr = "SELECT h.abbreviation, cast(fr.star as float), fr.positive,  fr.negative, h.phone, h.address FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where
            normal = self.cursor.execute(sqlstr).fetchall()  ## normal = [ (名稱, GOOGLE星等, 正向評論數, 負向評論數, 電話, 地址), ......]
            ## 若未找到任何資料，出現錯誤訊息，若有則進入else
            if normal == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return Select().select_data(normal, indexes, sql_where, search_filter)
        except BaseException as e:
            print('select_normal Exception' + e)
            return render_template('search.html')

    ## 取得使用者勾選的資訊
    def select_data(self, normal, indexes, sql_where, search_filter):
        try:
            value_substr = 'm.hospital_id'
            deno_substr = 'm.hospital_id'
            level_substr = 'm.hospital_id'
            for r in range(len(indexes)):
                value_substr += (', ' + 'm.v_' + indexes[r])
                level_substr += (', ' + 'm.l_' + indexes[r])
                deno_substr += (', ' + 'm.m_' + indexes[r])
            ## 取得data指標值
            sqlstr = "SELECT " + value_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where
            l_value = self.cursor.execute(sqlstr).fetchall()  ## l_value = [(hospital_id, 指標1之指標值, 指標2之指標值, 指標3之指標值, ......), ......]
            ## 取得data分母(就醫人數)
            sqlstr = "SELECT " + deno_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where
            l_deno = self.cursor.execute(sqlstr).fetchall()
            ## 取得data指標值等級
            sqlstr = "SELECT " + level_substr + " FROM merge_data m JOIN hospitals h ON m.hospital_id = h.id JOIN final_reviews fr ON h.id = fr.hospital_id " + sql_where
            l_level = self.cursor.execute(sqlstr).fetchall()
            ## 將醫療機構資訊、指標值、就醫人數、指標值等級包裝成zip
            z_data = zip(normal, l_value, l_deno, l_level)
            return Result().get_column_name(indexes, z_data, sql_where, search_filter)
        except BaseException as e:
            print('select_data Exception' + e)
            return render_template('search.html')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 取得欄位名稱
    def get_column_name(self, indexes, z_data, sql_where, search_filter):
        try:
            ## 先取得欄位的原始名字(m.v_?)，「醫院機構資訊」為固定欄位，直接手動新增
            getColumns=['醫療機構資訊']
            for r in range(len(indexes)):
                getColumns.append(indexes[r])
            ## 建立columns[]，存入從資料庫中取得的欄位名稱(縮寫)
            columns = []
            for c in getColumns:
                columns.append(self.cursor.execute("SELECT abbreviation FROM column_name WHERE name = '" + str(c) + "'").fetchone()[0])

            ## 建立full_name[]，存入欄位名稱(縮寫)的完整名字
            full_name = ['醫療機構資訊']
            for fn in columns:
                if fn != '醫療機構資訊':
                    full_name.append(self.cursor.execute("SELECT name FROM indexes WHERE abbreviation = '" + fn + "'").fetchone()[0])

            ## 將欄位名稱、欄位詳細說明包裝成zip
            z_col = zip(columns, full_name)
            ## 選取的指標數量，-1是因為扣掉第一欄的醫療機構資訊
            ck_len = len(columns) - 1
            ## 取得使用者所選指標將放進排序選單中，第一個為醫療機構資訊，所以不取
            sort_indexes = columns[1:]
            return Result().table(z_data, z_col, ck_len, search_filter, indexes, sql_where, sort_indexes)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return render_template('search.html')

    ## 將搜尋結果寫進表格
    def table(self, z_data, z_col, ck_len, search_filter, indexes, sql_where, sort_indexes):
        try:
            tmp_indexes = ''
            for r in range(len(indexes)):
                tmp_indexes += indexes[r] + '//'
            sql_where = sql_where.replace(' ', '//')
            tmp_filter = search_filter.replace(' ', '//')
            z_indexes = zip(indexes, sort_indexes)
            ## render至前端HTML，ck_len為指標的長度，columns為欄位名稱，z為醫院資訊和指標值的zip
            return render_template('result.html', ck_len=ck_len, z_col=z_col, z_data=z_data, search_filter=search_filter, tmp_filter=tmp_filter, sql_where=sql_where, tmp_indexes=tmp_indexes, z_indexes=z_indexes)
        except BaseException as e:
            print('table Exception' + e)
            return render_template('search.html')