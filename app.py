from flask import Flask, request, render_template, flash
from database import db_session, init_db
from models.search import Search, Select ##import search.py裡面的class Search()
from models.sort import Sort
import sqlite3

app = Flask(__name__)
app.secret_key = "mlkmslmpw"

#在接收到第一個request執行
@app.before_first_request
def init():
    init_db()  #初始化db

#正確關閉資料庫
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/', methods=['GET', 'POST'])
def renderHome():
    return render_template('home.html')

##在地區搜尋介面取得使用者輸入的值/search_area
@app.route('/search', methods=['GET', 'POST'])
def renderSearch():
    return render_template('search.html')

@app.route('/result', methods=['GET'])
def renderResult():
    return  render_template('result.html')

@app.route('/result', methods=['POST'])
def panduan():
    if request.method == 'POST':
        if 'btnSearch' in request.form:
            ## 特殊疾病
            disease = request.form.get('disease')
            ## 特疾病指標
            indexes = request.values.getlist('ckIndex')
            ## 醫療機構名稱
            name1 = request.form.get('name1')
            name2 = request.form.get('name2')
            name3 = request.form.get('name3')
            names = [name1, name2, name3]
            ## 移除陣列中的空字串
            while '' in names:
                names.remove('')
            ## 地區
            county = request.form.get("county")
            township = request.form.get("township")
            if township == '鄉鎮市區不拘':
                township = ''
            ## 醫院層級
            types = request.values.getlist('type')
            ##Google星等
            star = request.form.get("star")
            if star == None:
                star = ''
            ## 爛番茄
            # return render_template('result.html')
            return Search().search_all(county, township, disease, types, names, star, indexes)
        elif 'reSort' in request.form:
            selected_index = request.form.get('selected_index')
            indexes = request.form.get('tmp_indexes')
            sql_where = str(request.form.get('tmp_sqlstr')).replace('//', ' ')
            search_filter = str(request.form.get('tmp_filter')).replace('//', ' ')
            return Sort().reSort(selected_index, sql_where, indexes, search_filter)
##啟動
if __name__ == '__main__':
    app.jinja_env.auto_reloaded = True  ##jinja2 重新讀取template
    app.run('0.0.0.0', debug=True)
    # app.run(debug=True)