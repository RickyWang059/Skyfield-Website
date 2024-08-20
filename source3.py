# 匯入日期及時間套件
from datetime import datetime
#匯入地理編碼套件
from geopy import Nominatim
#匯入時區轉換套件
from timezonefinder import TimezoneFinder
from pytz import timezone, utc
#匯入現成的星空圖片生成套件
from starplot import MapPlot, Projection, Star
from starplot.styles import PlotStyle, extensions
from starplot.data import constellations

# 自訂函數1:取得目標地資訊
def collect_celestial_data3(location, when):
    locator = Nominatim(user_agent='StarChartApp', timeout=10)
    #利用Geopy將目的地名稱轉為經緯度
    location = locator.geocode(location)
    lat, lon = location.latitude, location.longitude
    #取得目標地當地時間，
    #將輸入的時間轉為datetime格式
    dt = datetime.strptime(when, '%Y-%m-%d %H:%M')
    #取得目標地之時區
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    #藉由目標地時區將輸入之時間轉為UTC標準時間
    local = timezone(timezone_str)
    utc_dt = local.localize(dt, is_dst=None).astimezone(utc)
    return lat, lon, utc_dt

# 自訂函數2:建立星座圖
def create_star_chart3(location, when,filename, constellation_line,
                       constellation_border, ecliptic, celestial_equator, milky_way, planet):
    #取得經緯度、時間
    lat, lon, utc_dt = collect_celestial_data3(location, when)
    #利用現成函數畫圖
    p = MapPlot(
    projection=Projection.ORTHOGRAPHIC,
    lat=lat,
    lon=lon,
    dt=utc_dt,
    ra_min=0,
    ra_max=24,
    dec_min=-90,
    dec_max=90,
    ephemeris= "de440.bsp",
    style=PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
    ),
    resolution=1500,
    )
    p.gridlines(labels=False)
    p.stars(mag=7.86, where_labels=[Star.magnitude < 6])
    p.open_clusters(mag=8, true_size=False, labels=None)
    p.galaxies(mag=8, true_size=False, labels=None)
    p.nebula(mag=8, true_size=True, labels=None)
    #藉由表單勾選項目分別執行
    #星座連線與名稱    
    if constellation_line:
        p.constellations(
            labels=constellations.CONSTELLATIONS_FULL_NAMES,
            style={"label": {"font_size": 9, "font_alpha": 0.8}},
        )
    #星座界線
    if constellation_border:
        p.constellation_borders()
    #黃道
    if ecliptic:
        p.ecliptic()
    #天球赤道
    if celestial_equator:
        p.celestial_equator()
    #銀河
    if milky_way:
        p.milky_way()
    #行星
    if planet:
        p.planets()
    
    p.export(filename, padding=0.3, transparent=True)
        