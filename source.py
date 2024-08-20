#!pip install skyfield
#!pip install timezonefinder
#!pip install geopy

# 匯入日期及時間套件
from datetime import datetime
#匯入地理編碼套件
from geopy import Nominatim
#匯入時區轉換套件
from timezonefinder import TimezoneFinder
from pytz import timezone, utc
# 匯入星空資料套件 
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos, stellarium
from skyfield.projections import build_stereographic_projection
from matplotlib.collections import LineCollection
import numpy as np
import matplotlib.pyplot as plt

#設定中文字
plt.rcParams['font.family'] = 'Microsoft JhengHei'
plt.rcParams['font.size'] = 15
plt.rcParams['axes.unicode_minus'] = False

#建立星座簡稱及中文對照表
constellation_names_chinese = {
    'And': '仙女座',
    'Ant': '唧筒座',
    'Aps': '天燕座',
    'Aql': '天鷹座',
    'Aqr': '寶瓶座',
    'Ara': '天壇座',
    'Ari': '白羊座',
    'Aur': '御夫座',
    'Boo': '牧夫座',
    'CMa': '大犬座',
    'CMi': '小犬座',
    'CVn': '獵犬座',
    'Cae': '雕具座',
    'Cam': '鹿豹座',
    'Cap': '魔羯座',
    'Car': '船底座',
    'Cas': '仙后座',
    'Cen': '半人馬座',
    'Cep': '仙王座',
    'Cet': '鯨魚座',
    'Cha': '蝘蜓座',
    'Cir': '圓規座',
    'Cnc': '巨蟹座',
    'Col': '天鴿座',
    'Com': '后髮座',
    'CrA': '南冕座',
    'CrB': '北冕座',
    'Crt': '巨爵座',
    'Cru': '南十字座',
    'Crv': '烏鴉座',
    'Cyg': '天鵝座',
    'Del': '海豚座',
    'Dor': '劍魚座',
    'Dra': '天龍座',
    'Equ': '小馬座',
    'Eri': '波江座',
    'For': '天爐座',
    'Gem': '雙子座',
    'Gru': '天鶴座',
    'Her': '武仙座',
    'Hor': '時鐘座',
    'Hya': '長蛇座',
    'Hyi': '水蛇座',
    'Ind': '印第安座',
    'LMi': '小獅座',
    'Lac': '蠍虎座',
    'Leo': '獅子座',
    'Lep': '天兔座',
    'Lib': '天秤座',
    'Lup': '豺狼座',
    'Lyn': '天貓座',
    'Lyr': '天琴座',
    'Men': '山案座',
    'Mic': '顯微鏡座',
    'Mon': '麒麟座',
    'Mus': '蒼蠅座',
    'Nor': '矩尺座',
    'Oct': '南極座',
    'Oph': '蛇夫座',
    'Ori': '獵戶座',
    'Pav': '孔雀座',
    'Peg': '飛馬座',
    'Per': '英仙座',
    'Phe': '鳳凰座',
    'Pic': '繪架座',
    'PsA': '南魚座',
    'Psc': '雙魚座',
    'Pup': '船尾座',
    'Pyx': '羅盤座',
    'Ret': '網罟座',
    'Scl': '玉夫座',
    'Sco': '天蝎座',
    'Sct': '盾牌座',
    'Ser': '巨蛇座',
    'Sex': '六分儀座',
    'Sge': '天箭座',
    'Sgr': '人馬座',
    'Tau': '金牛座',
    'Tel': '望遠鏡座',
    'TrA': '南三角座',
    'Tri': '三角座',
    'Tuc': '杜鵑座',
    'UMa': '大熊座',
    'UMi': '小熊座',
    'Vel': '船帆座',
    'Vir': '室女座',
    'Vol': '飛魚座',
    'Vul': '狐狸座'
}

# 自訂函數1:取得資料集
def load_data():
    # 導入de440.bsp資料集，取得星球的位置及相對距離
    eph = load('de440.bsp')
    # 導入hipparcos資料集，取得星球的位置及星等
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    # 導入stellarium資料集，取得星座名稱及範圍
    url = 'https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern_st/constellationship.fab'
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
    return eph, stars, constellations

# 自訂函數2:取得目標地資訊
def collect_celestial_data(location, when, altitude, azimuth, eph, stars, constellations):
    locator = Nominatim(user_agent='StarChartApp', timeout=10)
    #利用Geopy將目的地名稱轉為經緯度
    location = locator.geocode(location)
    lat, long = location.latitude, location.longitude
    #取得目標地當地時間，
    #將輸入的時間轉為datetime格式
    dt = datetime.strptime(when, '%Y-%m-%d %H:%M')
    #取得目標地之時區
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=long, lat=lat)
    #藉由目標地時區將輸入之時間轉為UTC標準時間
    local = timezone(timezone_str)
    utc_dt = local.localize(dt, is_dst=None).astimezone(utc)
    # 將UTC時間轉為skyfield可以處理的時間格式
    t = load.timescale().from_datetime(utc_dt)
    #利用wgs84建立觀察者經緯度
    observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=long).at(t)
    #建立太陽及地球之絕對位置
    sun = eph['sun']
    earth = eph['earth']
    #建立星座之範圍
    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]
    #帶入觀察者之仰角及方位角
    position = observer.from_altaz(alt_degrees=altitude, az_degrees=azimuth)
    '''利用輸入的高度角及方位角，對應到天球上的赤經(Right Ascension)及
    赤緯(Declination)，並假想一顆此赤經赤緯度的星球center_object，
    '''
    ra, dec, distance = position.radec()
    center_object = Star(ra=ra, dec=dec)
    '''以地球為中心，將center_object投影到地球上，作為center
    並以center為中心，將周圍其他星體利用stereographic將天球上的天體
    轉換至二維座標'''
    center = earth.at(t).observe(center_object)
    projection = build_stereographic_projection(center)
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)
    
    #取得星座名稱(英文簡寫版)
    constellations_at_location = {}
    for name, stars_in_constellation in constellations:
        constellation_stars = set()
        for star1, star2 in stars_in_constellation:
            if star1 in stars.index and star2 in stars.index:
                constellation_stars.add(star1)
                constellation_stars.add(star2)
        if constellation_stars:
            constellations_at_location[name] = constellation_stars

    return stars, edges_star1, edges_star2, constellations_at_location

# 自訂函數3:建立星座圖
def create_star_chart(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines, draw_constellation_names):
    stars, edges_star1, edges_star2, constellations_at_location = collect_celestial_data(location, when, altitude, azimuth, eph, stars, constellations)
    #設定最低星等
    limiting_magnitude = 10
    #定義星球選取標準(亮度低於10等星)
    bright_stars = (stars.magnitude <= limiting_magnitude)
    magnitude = stars['magnitude'][bright_stars]
    #設定輸出星球數量
    max_star_size = 200
    #輸出之星球依照視星等做大小變化
    marker_size = max_star_size * 10 ** (magnitude / -2.5)
    #設定畫布
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
    plt.subplots_adjust(left=0, right=1, top=0.98, bottom=0)
    #若是星座連線選項被勾選則執行
    if draw_lines:
        xy1 = stars[['x', 'y']].loc[edges_star1].values
        xy2 = stars[['x', 'y']].loc[edges_star2].values
        lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)
        ax.add_collection(LineCollection(lines_xy, colors='#ffff', linewidths=0.15))
    #繪製散布圖
    ax.scatter(stars['x'][bright_stars], stars['y'][bright_stars], s=marker_size, color='white', marker='.', linewidths=0, zorder=2)
    #若是星座名稱選項被勾選則執行
    if draw_constellation_names:
        for constellation_name, constellation_stars in constellations_at_location.items():
            chinese_name = constellation_names_chinese.get(constellation_name, constellation_name)
            constellation_x = np.mean(stars.loc[list(constellation_stars)]['x'])
            constellation_y = np.mean(stars.loc[list(constellation_stars)]['y'])
            ax.text(constellation_x, constellation_y, chinese_name, color='yellow', fontsize=8, ha='center', va='center')

    ax.set_aspect('equal')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    plt.axis('off')
    when_datetime = datetime.strptime(when, '%Y-%m-%d %H:%M')
    #設定圖片標題
    ax.set_title(f"{location}, {when_datetime.strftime('%Y-%m-%d %H:%M')}", loc='right',
             color='white', fontsize=10)
    plt.savefig(filename, facecolor='black', dpi=500)
    plt.close()
    
# 自訂函數4:閏年判斷  
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)