import sqlite3
from flask import Flask, request, render_template, flash, redirect
from models.search import Search

class Doc():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def search_doctor(self, doctor, depart, name):
        try:
            reserved = Search().doc_reserved(doctor, depart, name)
            sql_where = ''
            depart_condition = Search().search_depart(depart)
            listName = []
            listName.append(name)
            name_condition = Search().search_name(listName)
            doctor_condition = Search().search_doctor(doctor)
            conditions = [depart_condition, name_condition, doctor_condition]
            ## 若沒有條件則移除
            while '' in conditions:
                conditions.remove('')
            for condition in conditions:
                if condition.find('抱歉') != -1:  # 若為錯誤訊息，以alert提示#
                    return render_template('search.html', alert=condition)
                else:
                    condition = '(' + condition + ')'  # 若不為錯誤訊息則在條件句前後加上括號-->之後放在SQL中才不會出錯#
                    ## 將所有condition相接，若不為最後一個condition則加上'AND'
                    if condition != ('(' + conditions[-1] + ')'):
                        sql_where += condition + "AND "
                    else:
                        sql_where += condition
            if sql_where != '':
                sql_where = 'WHERE ' + sql_where
            return Select().select_normal(sql_where, reserved)
        except BaseException as e:
            print('search_doctor Exception' + e)
            return  render_template('search.hml')

class Select():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def select_normal(self, sql_where, reserved):
        try:
            sqlstr = "SELECT s.doctor, h.abbreviation, d.name, s.reviews FROM hospitals h JOIN doctor_subj s ON h.id = s.hospital_id JOIN depart d ON s.depart_id = d.id " + sql_where
            normal = self.cursor.execute(sqlstr).fetchall()

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
            sqlstr = "SELECT s.subj1, s.subj2, s.subj3, s.subj4, s.subj5, s.subj6, s.subj7 FROM hospitals h JOIN doctor_subj s ON h.id = s.hospital_id JOIN depart d ON s.depart_id = d.id " +sql_where
            value = self.cursor.execute(sqlstr).fetchall()
            z_data = zip(normal, value)
            return Result().get_column_name(z_data, sql_where, reserved)
        except BaseException as e:
            print('select_data Exception' + e)
            return  render_template('search.hml')

class Result():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    def get_column_name(self, z_data, sql_where, reserved):
        try:
            getColumns = ['doc', 's1', 's2', 's3', 's4', 's5', 's6', 's7']
            columns = []
            for c in getColumns:
                columns.append(self.cursor.execute("SELECT abbreviation FROM column_name WHERE name = '{}'".format(c)).fetchone()[0])
            col_len = len(columns) -1
            return render_template('doctorResult.html', z_data=z_data, columns=columns, col_len=col_len, reserved=reserved)
        except BaseException as e:
            print('get_column_name Exception' + e)
            return  render_template('search.hml')