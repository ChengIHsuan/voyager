from flask import Flask, request, render_template, flash
from database import db_session, init_db
from models.selectData import SelectData
from models.sort import Sort
from models.disease import Disease
from models.depart import Subj
from models.hospital import Hosp
from models.comp import Comp
from models.doctor import Doc

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

##【首頁】
@app.route('/', methods=['GET', 'POST'])
def renderHome():
    return render_template('home.html')

##【搜尋頁】
@app.route('/search', methods=['GET', 'POST'])
def renderSearch():
    return render_template('search.html')

##【找疾病】
@app.route('/diseaseResult', methods=['GET', 'POST'])
def diseaseResult():
    if request.method == 'POST':
        if 'btnSearchDisease' in request.form:
            ## 特殊疾病
            disease_id = request.form.get('disease')
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
            ## Google星等
            star = request.form.get("diseaseStar")
            if star == None:
                star = ''
            ## 爛番茄
            return Disease().search_all(disease_id, county, township, types, names, star, indexes)
        ## 重新排序
        elif 'reSort' in request.form:
            selected_index = request.form.get('selected_index')
            indexes = request.form.get('tmp_indexes')
            sql_where = str(request.form.get('tmp_sqlstr')).replace('//', ' ')
            reserved = request.form.get('tmp_reserved')
            return Sort().reSort(selected_index, sql_where, indexes, reserved)

##【找科別】
@app.route('/departResult', methods=['GET'])
def renderSubj():
    return render_template('departResult.html')

@app.route('/departResult', methods=['POST'])
def departResult():
    if request.method == 'POST':
        if 'btnSearchDepart' in request.form:
            ## 科別
            depart_id = request.form.get('depart')
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
            return Subj().search_depart(depart_id, subjectives, county, township, types, names)

##【找醫療機構】
@app.route('/hospResult', methods=['GET'])
def renderHosp():
    return render_template('hospResult.html')

@app.route('/hospResult', methods=['POST'])
def hospResult():
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
            ## Google星等
            star = request.form.get("hospStar")
            if star == None:
                star = ''
            return Hosp().search_hosp(county, township, names, types, star)

##【找醫療機構-->醫療機構客觀指標】
@app.route('/hospObjResult', methods=['GET'])
def renderHospObj():
    return render_template('hospObjResult.html')

@app.route('/hospObjResult', methods=['POST'])
def hospObjResult():
    if request.method == 'POST':
        for id in range(8071):
            ## 按鈕【客觀指標】
            if ('btnObj'+str(id)) in request.form:
                hosp_info = SelectData().hosp_info(id)
                return render_template('hospObjResult.html', hosp_info=hosp_info)
            ## 按鈕【主觀指標】
            if ('btnSubj'+str(id)) in request.form:
                hosp_info = SelectData().hosp_info(id)
                return render_template('hospSubjResult.html', hosp_info=hosp_info)
            ## 按鈕【搜尋】
            if ('btnSearch'+str(id)) in request.form:
                indexes = request.values.getlist('ckIndex')
                return Hosp().search_obj(id, indexes)

##【找醫療機構-->醫療機構主觀指標】
@app.route('/hospSubjResult', methods=['GET'])
def renderHospSubj():
    return render_template('hospSubjResult.html')

@app.route('/hospSubjResult', methods=['POST'])
def hospSubjResult():
    if request.method == 'POST':
        for id in range(8071):
            ## 按鈕【主觀指標】
            if ('btnSubj'+str(id)) in request.form:
                hosp_info = SelectData().hosp_info(id)
                return render_template('hospSubjResult.html', hosp_info=hosp_info)
            ## 按鈕【客觀指標】
            if ('btnObj'+str(id)) in request.form:
                hosp_info = SelectData().hosp_info(id)
                return render_template('hospObjResult.html', hosp_info=hosp_info)
            ## 按鈕【搜尋】
            if ('btnSearch'+str(id)) in request.form:
                subjectives = request.values.getlist('subjective')
                return Hosp().search_subj(id, subjectives)

##【找醫療機構-->比較各家醫療機構】
@app.route('/hospComparison', methods=['GET'])
def renderHospComp():
    return render_template('hospComparison.html')

@app.route('/hospComparison', methods=['POST'])
def hospComparison():
    if request.method == 'POST':
        if 'btnHospComp' in request.form:
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
            ## Google星等
            star = request.form.get("hospStar")
            if star == None:
                star = ''
            return Comp().comp_hosp(county, township, names, types, star)
        elif 'btnSearchHosp' in request.form:
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
            ## Google星等
            star = request.form.get("hospStar")
            if star == None:
                star = ''
            return Hosp().search_hosp(county, township, names, types, star)

##【找醫師】
@app.route('/doctorResult', methods=['GET', 'POST'])
def doctorResult():
    if request.method == 'POST':
        if 'btnSearchDoc' in request.form:
            ## 醫師名字
            doctor = request.form.get('doctor')
            ## 醫師科別
            depart = request.form.get('docDepart')
            ## 醫療機構名稱
            name = request.form.get('docName')
            ## 方法Search().search_name參數型態為list
            names = [name]
        return Doc().search_doctor(doctor, depart, names)

##啟動
if __name__ == '__main__':
    app.jinja_env.auto_reloaded = True  ##jinja2 重新讀取template
    ## 推上網站使用
    app.run('0.0.0.0', debug=False)
    ## 於PyCharm測試使用
    # app.run(debug=False)