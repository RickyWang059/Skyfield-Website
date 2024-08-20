from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from source import load_data, create_star_chart, is_leap_year
from source2 import create_star_chart2
from source3 import create_star_chart3
from source_eng import create_star_chart4
from database import generate_quiz, initialize_database
from geopy import Nominatim


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 初始化資料庫
# initialize_database()

#建立序言網頁
@app.route('/')
def preface():
    return render_template('preface.html')

#建立主頁面
@app.route('/mainpage')
def mainpage():
    return render_template('chinese/mainpage.html')

#建立英文版主頁面
@app.route('/mainpage_eng')
def mainpage_eng():
    return render_template('english/mainpage_eng.html')

#建立星空頁面
@app.route('/skyfield')
def skyfield():
    return render_template('chinese/skyfield.html')

#建立英文版星空頁面
@app.route('/skyfield_eng')
def skyfield_eng():
    return render_template('english/skyfield_eng.html')

#建立星座頁面
@app.route('/constellation')
def constellation():
    return render_template('chinese/constellation.html')

#建立英文版星座頁面
@app.route('/constellation_eng')
def constellation_eng():
    return render_template('english/constellation_eng.html')

#建立星座起源頁面
@app.route('/history')
def history():
    return render_template('chinese/history.html')

#建立英文版星座起源頁面
@app.route('/history_eng')
def history_eng():
    return render_template('english/history_eng.html')

#建立星圖生成頁面
@app.route('/creater')
def creater():
    return render_template('chinese/creater.html')

#建立英文版星圖生成頁面
@app.route('/creater_eng')
def creater_eng():
    return render_template('english/creater_eng.html')

#建立小測驗頁面
@app.route('/quiz')
def quiz():
    return render_template('chinese/quiz.html')

#建立測驗開始中繼點，會導至題目顯示頁面
@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    questions = generate_quiz()
    session['questions'] = questions
    session['current_question'] = 0
    session['answers'] = []
    return redirect(url_for('show_question'))

#建立題目顯示頁面
@app.route('/question', methods=['GET', 'POST'])
def show_question():
    current_question_index = session.get('current_question', 0)
    questions = session.get('questions', [])
    
    if request.method == 'POST':
        selected_answer = int(request.form.get('answer'))
        session['answers'].append(selected_answer)
        current_question_index += 1
        session['current_question'] = current_question_index

        if current_question_index >= len(questions):
            return redirect(url_for('show_results'))
    
    if current_question_index < len(questions):
        question = questions[current_question_index]
        return render_template('chinese/question_show.html', question=question, question_index=current_question_index + 1)
    else:
        return redirect(url_for('show_results'))

#建立結果產生頁面
@app.route('/results')
def show_results():
    questions = session.get('questions', [])
    answers = session.get('answers', [])
    results = []
    for i, (q, a) in enumerate(zip(questions, answers)):
        options = [{'text': q[j], 'is_correct': j - 2 == q[6]} for j in range(2, 6)]
        results.append({
            'index': i + 1,
            'question': q[1],
            'answer': a,
            'correct_answer': q[6],
            'options': options
        })
    return render_template('chinese/result_show.html', results=results, total_questions=len(questions), correct_answers=sum(1 for q, a in zip(questions, answers) if a == q[6]), incorrect_answers=sum(1 for q, a in zip(questions, answers) if a != q[6]), score=sum(1 for q, a in zip(questions, answers) if a == q[6]) * 100 // len(questions))

#建立重新測驗中繼點，會導至小測驗頁面
@app.route('/restart_quiz', methods=['POST'])
def restart_quiz():
    session.clear()
    return redirect(url_for('quiz'))

@app.route('/quiz_data')
def quiz_data():
    questions = session.get('questions', [])
    return jsonify(questions)

#建立簡報頁面
@app.route('/presentation')
def presentation():
    return render_template('chinese/presentation.html')

#建立生成器1頁面
@app.route('/generator1', methods=['GET', 'POST'])
def generator1():  
    if request.method == 'POST':
        #取得使用者輸入的表單資訊
        location = request.form['location']
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        when = f"{year}-{month}-{day} {hour}:{minute}"
        altitude = float(request.form['altitude'])
        azimuth = float(request.form['azimuth'])
        draw_lines = 'draw_lines' in request.form
        draw_constellation_names = 'draw_constellation_names' in request.form

        #檢驗日期及地點
        locator = Nominatim(user_agent='Spyder', timeout=10)
        location_data = locator.geocode(location)
        if ((month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30)) and (location_data is None):
            date_error="無效的日期搭配，請重新輸入"
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator1.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)) and (location_data is None):
            date_error="該年不是閏年，2月沒有29日，請重新輸入"
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator1.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
            date_error="無效的日期搭配，請重新輸入"
            return render_template('chinese/generator1.html',date_error=date_error)
        elif location_data is None:
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator1.html',location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)):
            date_error="該年不是閏年，2月沒有29日，請重新輸入"
            return render_template('chinese/generator1.html',date_error=date_error)
        
        eph, stars, constellations = load_data()
        filename = 'static/picture/star_chart.png'
        #帶入星圖生成函數
        create_star_chart(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines, draw_constellation_names)
        #將網頁導覽至生成結果頁面
        return redirect(url_for('show_star_chart1', filename=filename))
    return render_template('chinese/generator1.html')

#建立英文版生成器1頁面
@app.route('/generator1_eng', methods=['GET', 'POST'])
def generator1_eng():
    if request.method == 'POST':
        #取得使用者輸入的表單資訊
        location = request.form['location']
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        when = f"{year}-{month}-{day} {hour}:{minute}"
        altitude = float(request.form['altitude'])
        azimuth = float(request.form['azimuth'])
        draw_lines = 'draw_lines' in request.form
        draw_constellation_names = 'draw_constellation_names' in request.form
        
        #檢驗日期及地點
        locator = Nominatim(user_agent='Spyder', timeout=10)
        location_data = locator.geocode(location)
        if ((month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30)) and (location_data is None):
            date_error="Invalid date combination, please enter again."
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator1_eng.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)) and (location_data is None):
            date_error="The year is not a leap year, February does not have 29 days. Please enter again."
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator1_eng.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
            date_error="Invalid date combination, please enter again."
            return render_template('english/generator1_eng.html',date_error=date_error)
        elif location_data is None:
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator1_eng.html',location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)):
            date_error="The year is not a leap year, February does not have 29 days. Please enter again."
            return render_template('english/generator1_eng.html',date_error=date_error)
        
        eph, stars, constellations = load_data()
        filename = 'static/picture/star_chart.png'
        #帶入星圖生成函數
        create_star_chart4(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines, draw_constellation_names)
        #將網頁導覽至英文版生成結果頁面
        return redirect(url_for('show_star_chart1_eng', filename=filename))
    return render_template('english/generator1_eng.html')

#建立生成器1的結果頁面
@app.route('/generator1_result')
def show_star_chart1():
    filename = request.args.get('filename')
    return render_template('chinese/generator1_result.html', star_chart=filename)

#建立英文版生成器1的結果頁面
@app.route('/generator1_result_eng')
def show_star_chart1_eng():
    filename = request.args.get('filename')
    return render_template('english/generator1_result_eng.html', star_chart=filename)

#建立生成器2頁面
@app.route('/generator2', methods=['GET', 'POST'])
def generator2():
    if request.method == 'POST':
        #取得使用者輸入的表單資訊
        location = request.form['location']
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        when = f"{year}-{month}-{day} {hour}:{minute}"
        altitude = float(request.form['altitude'])
        azimuth = float(request.form['azimuth'])
        constellation_line = 'draw_lines_names' in request.form
        constellation_border = 'draw_constellation_border' in request.form
        ecliptic = 'draw_ecliptic' in request.form
        celestial_equator = 'draw_celestial_equator' in request.form
        milky_way = 'draw_milky_way' in request.form
        
        #檢驗日期及地點
        locator = Nominatim(user_agent='Spyder', timeout=10)
        location_data = locator.geocode(location)
        if ((month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30)) and (location_data is None):
            date_error="無效的日期搭配，請重新輸入"
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator2.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)) and (location_data is None):
            date_error="該年不是閏年，2月沒有29日，請重新輸入"
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator2.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
            date_error="無效的日期搭配，請重新輸入"
            return render_template('chinese/generator2.html',date_error=date_error)
        elif location_data is None:
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator2.html',location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)):
            date_error="該年不是閏年，2月沒有29日，請重新輸入"
            return render_template('chinese/generator2.html',date_error=date_error)
        
        
        filename = 'static/picture/star_chart.png'
        #帶入星圖生成函數2
        create_star_chart2(location, when, altitude, azimuth, filename, constellation_line,
                               constellation_border, ecliptic, celestial_equator, milky_way)
        #將網頁導覽至生成結果頁面2
        return redirect(url_for('show_star_chart2', filename=filename))
    return render_template('chinese/generator2.html')

#建立英文版生成器2頁面
@app.route('/generator2_eng', methods=['GET', 'POST'])
def generator2_eng():
    if request.method == 'POST':
        #取得使用者輸入的表單資訊
        location = request.form['location']
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        when = f"{year}-{month}-{day} {hour}:{minute}"
        altitude = float(request.form['altitude'])
        azimuth = float(request.form['azimuth'])
        constellation_line = 'draw_lines_names' in request.form
        constellation_border = 'draw_constellation_border' in request.form
        ecliptic = 'draw_ecliptic' in request.form
        celestial_equator = 'draw_celestial_equator' in request.form
        milky_way = 'draw_milky_way' in request.form
        
        #檢驗日期及地點
        locator = Nominatim(user_agent='Spyder', timeout=10)
        location_data = locator.geocode(location)
        if ((month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30)) and (location_data is None):
            date_error="Invalid date combination, please enter again."
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator2_eng.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)) and (location_data is None):
            date_error="The year is not a leap year, February does not have 29 days. Please enter again."
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator2_eng.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
            date_error="Invalid date combination, please enter again."
            return render_template('english/generator2_eng.html',date_error=date_error)
        elif location_data is None:
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator2_eng.html',location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)):
            date_error="The year is not a leap year, February does not have 29 days. Please enter again."
            return render_template('english/generator2_eng.html',date_error=date_error)
        #帶入星圖生成函數2
        filename = 'static/picture/star_chart.png'
        create_star_chart2(location, when, altitude, azimuth, filename, constellation_line,
                               constellation_border, ecliptic, celestial_equator, milky_way)
        #將網頁導覽至英文版生成結果頁面2
        return redirect(url_for('show_star_chart2_eng', filename=filename))
    return render_template('english/generator2_eng.html')

#建立生成器2的結果頁面
@app.route('/generator2_result')
def show_star_chart2():
    filename = request.args.get('filename')
    return render_template('chinese/generator2_result.html', star_chart=filename)

#建立英文版生成器2的結果頁面
@app.route('/generator2_result_eng')
def show_star_chart2_eng():
    filename = request.args.get('filename')
    return render_template('english/generator2_result_eng.html', star_chart=filename)

#建立生成器3頁面
@app.route('/generator3', methods=['GET', 'POST'])
def generator3():
    if request.method == 'POST':
        #取得使用者輸入的表單資訊
        location = request.form['location']
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        when = f"{year}-{month}-{day} {hour}:{minute}"
        constellation_line = 'draw_lines_names' in request.form
        constellation_border = 'draw_constellation_border' in request.form
        ecliptic = 'draw_ecliptic' in request.form
        celestial_equator = 'draw_celestial_equator' in request.form
        milky_way = 'draw_milky_way' in request.form
        planet = 'draw_planet' in request.form
        
        #檢驗日期及地點
        locator = Nominatim(user_agent='Spyder', timeout=10)
        location_data = locator.geocode(location)
        if ((month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30)) and (location_data is None):
            date_error="無效的日期搭配，請重新輸入"
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator3.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)) and (location_data is None):
            date_error="該年不是閏年，2月沒有29日，請重新輸入"
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator3.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
            date_error="無效的日期搭配，請重新輸入"
            return render_template('chinese/generator3.html',date_error=date_error)
        elif location_data is None:
            location_error="找不到該位置，請輸入有效的位置"
            return render_template('chinese/generator3.html',location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)):
            date_error="該年不是閏年，2月沒有29日，請重新輸入"
            return render_template('chinese/generator3.html',date_error=date_error)
        
        
        filename = 'static/picture/star_chart.png'
        #帶入星圖生成函數3
        create_star_chart3(location, when, filename, constellation_line,
                               constellation_border, ecliptic, celestial_equator, milky_way, planet)
        #將網頁導覽至生成結果頁面2
        return redirect(url_for('show_star_chart3', filename=filename))
    return render_template('chinese/generator3.html')

#建立英文版生成器3頁面
@app.route('/generator3_eng', methods=['GET', 'POST'])
def generator3_eng():
    if request.method == 'POST':
        #取得使用者輸入的表單資訊
        location = request.form['location']
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        hour = int(request.form['hour'])
        minute = int(request.form['minute'])
        when = f"{year}-{month}-{day} {hour}:{minute}"
        constellation_line = 'draw_lines_names' in request.form
        constellation_border = 'draw_constellation_border' in request.form
        ecliptic = 'draw_ecliptic' in request.form
        celestial_equator = 'draw_celestial_equator' in request.form
        milky_way = 'draw_milky_way' in request.form
        planet = 'draw_planet' in request.form
        
        
        #檢驗日期及地點
        locator = Nominatim(user_agent='Spyder', timeout=10)
        location_data = locator.geocode(location)
        if ((month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30)) and (location_data is None):
            date_error="Invalid date combination, please enter again."
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator3_eng.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)) and (location_data is None):
            date_error="The year is not a leap year, February does not have 29 days. Please enter again."
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator3_eng.html',date_error=date_error,location_error=location_error)
        elif (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
            date_error="Invalid date combination, please enter again."
            return render_template('english/generator3_eng.html',date_error=date_error)
        elif location_data is None:
            location_error="The location cannot be found. Please enter a valid location."
            return render_template('english/generator3_eng.html',location_error=location_error)
        elif (month == 2 and day==29 and not is_leap_year(year)):
            date_error="The year is not a leap year, February does not have 29 days. Please enter again."
            return render_template('english/generator3_eng.html',date_error=date_error)
        
        filename = 'static/picture/star_chart.png'
        #帶入星圖生成函數3
        create_star_chart3(location, when, filename, constellation_line,
                               constellation_border, ecliptic, celestial_equator, milky_way, planet)
        #將網頁導覽至英文版生成結果頁面3
        return redirect(url_for('show_star_chart3_eng', filename=filename))
    return render_template('english/generator3_eng.html')

#建立生成器3的結果頁面
@app.route('/generator3_result')
def show_star_chart3():
    filename = request.args.get('filename')
    return render_template('chinese/generator3_result.html', star_chart=filename)

#建立英文版生成器3的結果頁面
@app.route('/generator3_result_eng')
def show_star_chart3_eng():
    filename = request.args.get('filename')
    return render_template('chinese/generator3_result_eng.html', star_chart=filename)

#建立大熊座介紹頁面
@app.route('/ursa_major')
def ursa_major():
    return render_template('chinese/constellation/ursa_major.html')

#建立小熊座介紹頁面
@app.route('/ursa_minor')
def ursa_minor():
    return render_template('chinese/constellation/ursa_minor.html')

#建立牧夫座介紹頁面
@app.route('/bootes')
def bootes():
    return render_template('chinese/constellation/bootes.html')

#建立室女座介紹頁面
@app.route('/virgo')
def virgo():
    return render_template('chinese/constellation/virgo.html')

#建立獅子座介紹頁面
@app.route('/leo')
def leo():
    return render_template('chinese/constellation/leo.html')

#建立天龍座介紹頁面
@app.route('/draco')
def draco():
    return render_template('chinese/constellation/draco.html')

#建立后髮座介紹頁面
@app.route('/coma_berenices')
def coma_berenices():
    return render_template('chinese/constellation/coma_berenices.html')

#建立長蛇座介紹頁面
@app.route('/hydra')
def hydra():
    return render_template('chinese/constellation/hydra.html')

#建立烏鴉座介紹頁面
@app.route('/corvus')
def corvus():
    return render_template('chinese/constellation/corvus.html')

#建立巨爵座介紹頁面
@app.route('/crater')
def crater():
    return render_template('chinese/constellation/crater.html')

#建立六分儀座介紹頁面
@app.route('/sextans')
def sextans():
    return render_template('chinese/constellation/sextans.html')

#建立小獅座介紹頁面
@app.route('/leo_minor')
def leo_minor():
    return render_template('chinese/constellation/leo_minor.html')

#建立獵犬座介紹頁面
@app.route('/canes_venatici')
def canes_venatici():
    return render_template('chinese/constellation/canes_venatici.html')

#建立天貓座介紹頁面
@app.route('/lynx')
def lynx():
    return render_template('chinese/constellation/lynx.html')

#建立鹿豹座介紹頁面
@app.route('/camelopardalis')
def camelopardalis():
    return render_template('chinese/constellation/camelopardalis.html')

#建立天琴座介紹頁面
@app.route('/lyra')
def lyra():
    return render_template('chinese/constellation/lyra.html')

#建立天鷹座介紹頁面
@app.route('/aquila')
def aquila():
    return render_template('chinese/constellation/aquila.html')

#建立天鵝座介紹頁面
@app.route('/cygnus')
def cygnus():
    return render_template('chinese/constellation/cygnus.html')

#建立天蝎座介紹頁面
@app.route('/scorpius')
def scorpius():
    return render_template('chinese/constellation/scorpius.html')

#建立寶瓶座介紹頁面
@app.route('/aquarius')
def aquarius():
    return render_template('chinese/constellation/aquarius.html')

#建立巨蟹座介紹頁面
@app.route('/cancer')
def cancer():
    return render_template('chinese/constellation/cancer.html')

if __name__ == '__main__':
    app.run(debug=True)
