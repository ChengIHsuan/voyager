from flask import Flask, request, render_template, flash
from database import db_session, init_db
from models.sort import Sort
from models.disease import Disease
from models.subj import Subj
from models.hospital import Hosp
from models.search import Search

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

@app.route('/diseaseResult', methods=['GET'])
def renderDisease():
    return  render_template('diseaseResult.html')

@app.route('/diseaseResult', methods=['POST'])
def panduanDisease():
    if request.method == 'POST':
        if 'btnSearchDisease' in request.form:
            ## 特殊疾病
            disease = request.form.get('disease')
            ## 特疾病指標
            indexes = request.values.getlist('ckIndex')
            ## 醫療機構名稱
            name1 = request.form.get('diseaseName1')
            name2 = request.form.get('diseaseName2')
            name3 = request.form.get('diseaseName3')
            names = [name1, name2, name3]
            ## 地區
            county = request.form.get('diseaseCounty')
            township = request.form.get("diseaseTownship")
            ## 醫院層級
            types = request.values.getlist('diseaseType')
            ##Google星等
            star = request.form.get("diseaseStar")
            if star == None:
                star = ''
            ## 爛番茄
            # return render_template('diseaseResult.html')
            return Disease().search_all(disease, county, township, types, names, star, indexes)
        elif 'reSort' in request.form:
            selected_index = request.form.get('selected_index')
            indexes = request.form.get('tmp_indexes')
            sql_where = str(request.form.get('tmp_sqlstr')).replace('//', ' ')
            reserved = request.form.get('tmp_reserved')
            return Sort().reSort(selected_index, sql_where, indexes, reserved)

@app.route('/subjResult', methods=['GET'])
def renderSubj():
    return render_template('subjResult.html')

@app.route('/subjResult', methods=['POST'])
def panduanSubj():
    if request.method == 'POST':
        print('hi')
        if 'btnSearchDepart' in request.form:
            ## 科別
            depart = request.form.get('depart')
            ## 主觀指標
            subjectives = request.values.getlist('subjective')
            ## 地區
            county = request.form.get('departCounty')
            township = request.form.get("departTownship")
            ## 醫院層級
            types = request.values.getlist('departType')
            ## 醫療機構名稱
            name1 = request.form.get('departName1')
            name2 = request.form.get('departName2')
            name3 = request.form.get('departName3')
            names = [name1, name2, name3]
            # return "{}//{}//{}//{}".format(depart, subjective, county, township)
            return Subj().search_subj(depart, subjectives, county, township, types, names)

@app.route('/hospResult', methods=['GET'])
def renderHosp():
    return render_template('hospResult.html')

@app.route('/hospResult', methods=['POST'])
def panduanHosp():
    if request.method == 'POST':
        if 'btnSearchHosp' in request.form:
            ## 地區
            county = request.form.get('hospCounty')
            township = request.form.get("hospTownship")
            ## 醫療機構名稱
            name1 = request.form.get('hospName1')
            name2 = request.form.get('hospName2')
            name3 = request.form.get('hospName3')
            names = [name1, name2, name3]
            ## 醫院層級
            types = request.values.getlist('hospType')
            ##Google星等
            star = request.form.get("hospStar")
            if star == None:
                star = ''
            return Hosp().search_hosp(county, township, names, types, star)

@app.route('/hospObjResult', methods=['GET'])
def renderHospObj():
    return render_template('hospObjResult.html')

@app.route('/hospObjResult', methods=['POST'])
def panduanHospObj():
    if request.method == 'POST':
        for id in range(8071):
            if ('btnObj'+str(id)) in request.form:
                normal = Search().search_hosp(id)
                return render_template('hospObjResult.html', normal=normal)
            if ('btnSubj'+str(id)) in request.form:
                normal = Search().search_hosp(id)
                return render_template('hospSubjResult.html', normal=normal)
            if ('btnSearch'+str(id)) in request.form:
                indexes = request.values.getlist('ckIndex')
                return Hosp().search_obj(id, indexes)

@app.route('/hospSubjResult', methods=['GET'])
def renderHospSubj():

    return render_template('hospSubjResult.html')

@app.route('/hospSubjResult', methods=['POST'])
def panduanHospSubj():
    if request.method == 'POST':
        for id in range(8071):
            if ('btnSubj'+str(id)) in request.form:
                normal = Search().search_hosp(id)
                return render_template('hospSubjResult.html', normal=normal)
            if ('btnObj'+str(id)) in request.form:
                normal = Search().search_hosp(id)
                return render_template('hospObjResult.html', normal=normal)
            if ('btnSearch'+str(id)) in request.form:
                subjectives = request.values.getlist('subjective')
                return Hosp().search_subj(id, subjectives)

##啟動
if __name__ == '__main__':
    app.jinja_env.auto_reloaded = True  ##jinja2 重新讀取template
    app.run('0.0.0.0', debug=False)
    # app.run(debug=False)