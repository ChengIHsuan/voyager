import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search

class Hosp():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def search_obj(self, hospital_id, indexes):
        try:
            normal = Search().search_hosp(hospital_id)

            value_substr = ''
            deno_substr = ''
            level_substr = ''
            for index in indexes:
                value_substr += ('m.v_' + index + ', ')
                deno_substr += ('m.d_' + index + ', ')
                level_substr += ('m.l_' +index + ', ')
            value_substr = value_substr[:-2]
            deno_substr = deno_substr[:-2]
            level_substr = level_substr[:-2]
            l_value = self.cursor.execute("SELECT {} FROM merge_data m WHERE m.hospital_id = {}".format(value_substr, hospital_id)).fetchone()
            l_deno = self.cursor.execute("SELECT {} FROM merge_data m WHERE m.hospital_id = {}".format(deno_substr, hospital_id)).fetchone()
            l_level = self.cursor.execute("SELECT {} FROM merge_data m WHERE m.hospital_id = {}".format(level_substr, hospital_id)).fetchone()
            z_data = zip(l_value, l_deno, l_level)

            columns = []
            for i in indexes:
                columns.append(self.cursor.execute("SELECT abbreviation, PorN, description FROM column_name WHERE name = '{}' ".format(i)).fetchall()[0])

            col_len = len(columns)
            return render_template('hospObjResult.html', scroll='indexes', normal=normal, z_data=z_data, columns=columns, col_len=col_len)
        except:
            alert = "抱歉，找不到您要的資料訊息。"
            normal = Search().search_hosp(hospital_id)
            return render_template('hospObjResult.html', normal=normal, alert=alert)


    def search_subj(self, hospital_id, subjectives):
        try:
            normal = Search().search_hosp(hospital_id)
            substr = 'depart_id'
            for subjective in subjectives:
                substr += (', subj' + subjective)
            sqlstr = "SELECT {} FROM dept_subj WHERE hospital_id = {}".format(substr, hospital_id)
            subj_data = self.cursor.execute(sqlstr).fetchall()
            del subj_data[-1]
            depart = []
            for i in subj_data:
                depart.append(self.cursor.execute("SELECT name FROM depart WHERE id = {}".format(i[0])).fetchone()[0])
            z_data = zip(depart, subj_data)

            columns = ['科別']
            for s in subjectives:
                columns.append(self.cursor.execute("SELECT abbreviation FROM column_name WHERE name = '{}' ".format('s'+s)).fetchone()[0])

            col_len = len(columns)-1
            return render_template('hospSubjResult.html', scroll='results', normal=normal, z_data=z_data, columns=columns, col_len=col_len)
        except:
            alert = "抱歉，找不到您要的資料訊息。"
            normal = Search().search_hosp(hospital_id)
            return render_template('hospSubjResult.html', normal=normal, alert=alert)

    def search_hosp(self, county, township, names, types, star):
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
            sqlstr = "SELECT h.abbreviation, h.type, cast(fr.star as float), fr.reviews, h.phone, h.address, h.id FROM hospitals h JOIN final_reviews fr ON h.id = fr.hospital_id  " + sql_where
            normal = self.cursor.execute(sqlstr).fetchall()  ## normal = [ (名稱, GOOGLE星等, 正向評論數, 負向評論數, 電話, 地址), ......]

            if normal == []:
                alert = "抱歉，找不到您要的資料訊息。"
                return render_template("search.html", alert=alert)
            else:
                return render_template("hospResult.html", normal=normal, reserved=reserved)
        except BaseException as e:
            print('selct_normal Exception' + e)
            return  render_template('search.hml')


