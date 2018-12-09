from flask import Flask, request, render_template, flash
from database import db_session, init_db
from models.search import Search, Select, CheckBox ##import search.py裡面的class Search()

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

##在地區搜尋介面取得使用者輸入的值/search_area
@app.route('/', methods=['GET'])
def renderSearch():
    return render_template('hospital.html')

@app.route('/search', methods=['POST'])
def panduan():
    if request.method == 'POST':
        if 'choose' in request.form:
            items = request.values.getlist('item')
            sql_where = request.form.get('sqlstr')
            return Select().select_normal(sql_where, items)
        elif 'searchArea' in request.form:
            #從前端hospital.html的unputbox的name抓使用者輸入的值
            county = request.form.get("county")
            township = request.form.get("township")
            if county.find('台') != -1:
                county = county.replace('台', '臺')
            return CheckBox().print_ckbox(Search().search_area(county, township))
        elif 'searchDisease' in request.form:
            disease = request.form.get('disease')
            return Select().select_disease(Search().search_disease(disease))
        elif 'searchType' in request.form:
            types = request.values.getlist('type')
            return CheckBox().print_ckbox(Search().search_type(types))
        elif 'searchCategory' in request.form:
            keyword1 = request.form.get('keyword1')
            keyword2 = request.form.get('keyword2')
            keyword3 = request.form.get('keyword3')
            keywords = [keyword1, keyword2, keyword3]
            return CheckBox().category_ckbox(Search().search_category(keywords))
        elif 'searchName' in request.form:
            name1 = request.form.get('name1')
            name2 = request.form.get('name2')
            name3 = request.form.get('name3')
            enter_names = [name1, name2, name3]
            return CheckBox().print_ckbox(Search().search_name(enter_names))
        elif 'searchAll' in request.form:
            ## 地區
            county = request.form.get("county")
            township = request.form.get("township")
            if county.find('台') != -1:
                county = county.replace('台', '臺')
            ## 特殊疾病
            disease = request.form.get('disease')
            ## 醫院層級
            types = request.values.getlist('type')
            ## 分類主題
            keyword1 = request.form.get('keyword1')
            keyword2 = request.form.get('keyword2')
            keyword3 = request.form.get('keyword3')
            keywords = [keyword1, keyword2, keyword3]
            ## 醫院名稱
            name1 = request.form.get('name1')
            name2 = request.form.get('name2')
            name3 = request.form.get('name3')
            names = [name1, name2, name3]
            return Search().search_all(county, township, disease, types, keywords, names)

##啟動
if __name__ == '__main__':
    app.jinja_env.auto_reloaded = True  ##jinja2 重新讀取template
    app.run('0.0.0.0', debug=True)
    # app.run(debug=True)