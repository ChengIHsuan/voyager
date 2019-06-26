import sqlite3

class Search():

    def __init__(self):
        db = sqlite3.connect('voyager.db')
        self.cursor = db.cursor()

    ## 醫療機構
    def search_hosp(self, hospital_id):
        try:
            sqlstr = "SELECT h.id, h.abbreviation, h.type, cast(fr.star as float), fr.reviews, h.address, h.phone FROM hospitals h JOIN final_reviews fr ON h.id = fr.hospital_id WHERE h.id={}".format(
                hospital_id)
            normal = self.cursor.execute(sqlstr).fetchone()
            return normal
        except:
            return "抱歉，操作失敗。[H]"

    ## 科別
    def search_depart(self, depart):
        try:
            if depart != '0' :
                sql_where = "s.depart_id = {}".format(depart)
                return sql_where
            else:
                return ''
        except:
            return "抱歉，操作失敗。[Dpt]"

    ## 地區搜尋
    def search_area(self, county, township):
        try:
            areaStr = {
                '0': ['', ''],
                '1': ['', '安樂區', '信義區', '中正區', '暖暖區', '仁愛區', '七堵區', '中山區', '基隆市'],
                '2': ['', '大安區', '中正區', '中山區', '北投區', '內湖區', '士林區', '文山區', '松山區', '信義區', '大同區', '萬華區', '南港區', '臺北市'],
                '3': ['', '板橋區', '三峽區', '新莊區', '汐止區', '中和區', '新店區', '三重區', '永和區', '土城區', '瑞芳區', '金山區', '樹林區', '淡水區', '林口區', '蘆洲區', '泰山區', '五股區', '鶯歌區', '深坑區', '貢寮區', '平溪區', '三芝區', '石碇區', '萬里區', '雙溪區', '八里區', '坪林區', '烏來區', '石門區', '新北市'],
                '4': ['', '龜山區', '桃園區', '平鎮區', '龍潭區', '中壢區', '新屋區', '大園區', '楊梅區', '八德區', '大溪區', '觀音區', '蘆竹區', '復興區', '桃園市'],
                '5': ['', '竹北市', '湖口鄉', '竹東鎮', '新豐鄉', '新埔鎮', '關西鎮', '穹林鄉', '五峰鄉', '寶山鄉', '北埔鄉', '橫山鄉', '峨眉鄉', '尖石鄉', '新竹縣'],
                '6': ['', '東區', '北區', '香山區', '新竹市'],
                '7': ['', '頭份市', '苗栗市', '苑裡鎮', '大湖鄉', '竹南鎮', '通霄鎮', '公館鄉', '三灣鄉', '後龍鎮', '泰安鄉', '三義鄉', '卓蘭鎮', '銅鑼鄉', '頭屋鄉', '南庄鄉', '西湖鄉', '造橋鄉', '獅潭鄉', '苗栗縣'],
                '8': ['', '北區', '西屯區', '南區', '梧棲區', '豐原區', '西區', '潭子區', '南屯區', '沙鹿區', '大里區', '大甲區', '太平區', '大雅區', '霧峰區', '烏日區', '中區', '東勢區', '北屯區', '東區', '后里區', '清水區', '龍井區', '大肚區', '和平區', '新社區', '外埔區', '石岡區', '大安區', '神岡區', '臺中市'],
                '9': ['', '彰化市', '埔心鄉', '鹿港鎮', '員林鎮', '田中鎮', '北斗鎮', '和美鎮', '二林鎮', '溪湖鎮', '伸港鄉', '大村鄉', '福興鄉', '花壇鄉', '永靖鄉', '溪州鄉', '芬園鄉', '芳苑鄉', '埔鹽鄉', '秀水鄉', '田尾鄉', '大城鄉', '埤頭鄉', '竹塘鄉', '線西鄉', '二水鄉', '社頭鄉', '彰化縣'],
                '10': ['', '埔里鎮', '草屯鎮', '南投市', '竹山鎮', '鹿谷鄉', '水里鄉', '仁愛鄉', '集集鎮', '魚池鄉', '名間鄉', '國姓鄉', '中寮鄉', '信義鄉', '南投縣'],
                '11': ['', '虎尾鎮', '斗六市', '北港鎮', '西螺鎮', '土庫鎮', '麥寮鄉', '斗南鎮', '褒忠鄉', '大埤鄉', '林內鄉', '崙背鄉', '口湖鄉', '古坑鄉', '刺桐鄉', '臺西鄉', '二崙鄉', '東勢鄉', '元長鄉', '四湖鄉', '水林鄉', '雲林縣'],
                '12': ['', '東區', '西區', '嘉義市'],
                '13': ['', '大林鎮', '朴子市', '竹崎鄉', '民雄鄉', '溪口鄉', '新港鄉', '東石鄉', '六腳鄉', '鹿草鄉', '水上鄉', '義竹鄉', '太保市', '阿里山鄉', '中埔鄉', '布袋鎮', '番路鄉', '梅山鄉', '嘉義縣'],
                '14': ['', '北區', '永康區', '南區', '麻豆區', '柳營區', '西區', '東區', '安南區', '仁德區', '中區', '新營區', '佳里區', '中西區', '關廟區', '新化區', '善化區', '白河區', '安平區', '新市區', '後壁區', '七股區', '北門區', '鹽水區', '安定區', '下營區', '學甲區', '大內區', '官田區', '東山區', '將軍區', '玉井區', '西港區', '歸仁區', '龍崎區', '左鎮區', '南化區', '山上區', '楠西區', '六甲區', '臺南市'],
                '15': ['', '三民區', '左營區', '鳥松區', '苓雅區', '前金區', '鼓山區', '小港區', '燕巢區', '楠梓區', '鳳山區', '林園區', '岡山區', '旗津區', '前鎮區', '新興區', '旗山區', '橋頭區', '阿蓮區', '路竹區', '美濃區', '大寮區', '鹽埕區', '六龜區', '茄萣區', '大社區', '梓官區', '那瑪夏區', '仁武區', '內門區', '甲仙區', '杉林區', '桃源區', '大樹區', '湖內區', '永安區', '茂林區', '彌陀區', '田寮區', '高雄市'],
                '16': ['', '東港鎮', '屏東市', '枋寮鄉', '恆春鎮', '內埔鄉', '高樹鄉', '潮州鎮', '春日鄉', '長治鄉', '林邊鄉', '三地鄉', '牡丹鄉', '獅子鄉', '鹽埔鄉', '新埤鄉', '琉球鄉', '滿州鄉', '萬丹鄉', '九如鄉', '瑪家鄉', '車城鄉', '來義鄉', '新園鄉', '佳冬鄉', '萬巒鄉', '枋山鄉', '里港鄉', '泰武鄉', '麟洛鄉', '崁頂鄉', '霧臺鄉', '南州鄉', '竹田鄉', '屏東縣'],
                '17': ['', '臺東市', '關山鎮', '成功鎮', '鹿野鄉', '太麻里', '蘭嶼鄉', '東河鄉', '長濱鄉', '池上鄉', '達仁鄉', '金峰鄉', '綠島鄉', '海端鄉', '卑南鄉', '大武鄉', '延平鄉', '臺東縣'],
                '18': ['', '花蓮市', '新城鄉', '豐濱鄉', '玉里鎮', '鳳林鎮', '壽豐鄉', '吉安鄉', '瑞穗鄉', '光復鄉', '秀林鄉', '卓溪鄉', '富里鄉', '萬榮鄉', '花蓮縣'],
                '19': ['', '宜蘭市', '羅東鎮', '礁溪鄉', '蘇澳鎮', '員山鄉', '壯圍鄉', '冬山鄉', '南澳鄉', '五結鄉', '三星鄉', '大同鄉', '頭城鎮', '宜蘭縣'],
                '20': ['', '馬公市', '湖西鎮', '七美鄉', '白沙鄉', '望安鄉', '西嶼鄉', '澎湖縣'],
                '21': ['', '金湖鎮', '金寧鎮', '金城鎮', '烈嶼鄉', '金沙鎮', '金門縣'],
                '22': ['', '南竿鄉', '北竿鄉', '東引鄉', '莒光鄉', '連江縣']
            }
            if county != '0':  #使用者有選縣市#
                area = (areaStr.get(str(county))[-1]) + (areaStr.get(str(county))[int(township)])
            else:
                area = ''
            ## 依照使用者在前端輸入的條件寫成SQL字串中的condition
            sql_where = "h.area LIKE '%" + area + "%'"
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
                '10': "腹膜透析",
                '11': "慢性腎臟病"
            }
            return getStr.get(disease)
        except:
            return "抱歉，操作失敗。[D]"

    ## 醫院層級
    def search_type(self, types):
        try:
            ## 建立一個tuple，使前端取回的type值可以對應正確的醫療層級
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
            ## 移除陣列中的空字串，即使用者未輸入之txtbox
            while '' in names:
                names.remove('')
            ## 建立一個SQL語法中condition的開頭字串
            sql_where = ''
            ## 寫入condition字串中，對應全名或是縮寫
            for name in names:
                ## 檢查使用者輸入之名稱是否存在
                validate = self.cursor.execute("SELECT h.id FROM hospitals h WHERE h.name LIKE '%{}%' OR h.abbreviation LIKE '%{}%'".format(name, name)).fetchall()
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

    ## 星等
    def search_star(self, star):
        try:
            sql_where = ''
            if star != '':
                sql_where += "fr.star >= " + star + " AND fr.star != 'N/A' "
            return sql_where
        except:
            return "抱歉，操作失敗。[S]"

    def search_doctor(self, doctor):
        try:
            if doctor != '':
                sql_where = "s.doctor LIKE '%{}%' ".format(doctor)
                return sql_where
            else:
                return ''
        except:
            return "抱歉，操作失敗。[Doc]"

    ## 醫療機構保留條件
    def hosp_reserved(self, county, township, names, types, star):
        try:
            ## reserved = [縣市, 鄉鎮市區, 名稱1, 名稱2, 名稱3, 醫學中心, 區域醫院, 地區醫院, 診所, 星等]
            reserved = [county, township]
            for name in names:
                reserved.append(name)
            ## 醫療層級預設皆為false，若使用者有勾選擇改為true
            for f in range(4):  #共有4個醫療層級#
                reserved.append('false')
            for type in types:
                i = (int(type) + 4)  #層級value為1~4，對應保留條件陣列中5~8位置#
                reserved[i] = 'true'
            while star == '':  #即使用者沒有選擇星等#
                star = 0
            reserved.append(star)
            return reserved
        except:
            return "抱歉，操作失敗。[HR]"

    ## 疾病保留條件
    def disease_reserved(self, disease, county, township, names, types, star):
        try:
            ## reserved = [特殊疾病, 縣市, 鄉鎮市區, 名稱1, 名稱2, 名稱3, 醫學中心, 區域醫院, 地區醫院, 診所, 星等]
            reserved = [disease, county, township]
            for name in names:
                reserved.append(name)
            ## 醫療層級預設皆為false，若使用者有勾選擇改為true
            for f in range(4):  #共有4個醫療層級#
                reserved.append('false')
            for type in types:
                i = (int(type) + 5)  #層級value為1~4，對應保留條件陣列中6~9位置#
                reserved[i] = 'true'
            while star == '':  #即使用者沒有選擇星等#
                star = 0
            reserved.append(star)
            return reserved
        except:
            return "抱歉，操作失敗。[DR]"

    ## 科別保留條件
    def subj_reserved(self, depart, county, township, types, names):
        try:
            ## reserved = [科別, 縣市, 鄉鎮市區, 醫學中心, 區域醫院, 地區醫院, 診所, 名稱1, 名稱2, 名稱3,]
            reserved = [depart, county, township]
            ## 醫療層級預設皆為false，若使用者有勾選擇改為true
            for f in range(4):  #共有4個醫療層級#
                reserved.append('false')
            for type in types:
                i = (int(type) + 2)  #層級value為1~4，對應保留條件陣列中3~6位置#
                reserved[i] = 'true'
            for name in names:
                reserved.append(name)
            return reserved
        except:
            return "抱歉，操作失敗。[SR]"

    def doc_reserved(self, doctor, depart, name):
        try:
            ## reserved = [科別, 縣市, 鄉鎮市區, 醫學中心, 區域醫院, 地區醫院, 診所, 名稱1, 名稱2, 名稱3,]
            reserved = [doctor, depart, name]
            return reserved
        except:
            return "抱歉，操作失敗。[CR]"

