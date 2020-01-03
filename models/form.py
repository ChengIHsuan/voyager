import sqlite3
from flask import render_template


class Form():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def form_sqlwhere(self, conditions):
        sql_where = ''
        ## 若沒有條件則移除
        while '' in conditions:
            conditions.remove('')
        for condition in conditions:
            if condition.find('抱歉') != -1:  # 若為錯誤訊息，以alert提示#
                return render_template('search.html', alert=condition)
            else:
                condition = '(' + condition + ')'  # 若不為錯誤訊息則在條件句前後加上括號-->避免之後放在SQL中出錯#
                ## 將所有condition相接，若不為最後一個condition則加上'AND'
                if condition != ('(' + conditions[-1] + ')'):
                    sql_where += condition + "AND "
                else:
                    sql_where += condition
        if sql_where != '':
            sql_where = 'WHERE ' + sql_where
        return sql_where







