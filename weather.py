from urllib.request import urlopen 
from urllib.parse import urlencode, unquote, quote_plus 
import urllib , requests , json, datetime, logging
import pandas as pd

log = logging.getLogger('detect')
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler()
log.addHandler(log_handler)

encoding_auth_key = "BZF4W49MNogC%2F5NdkMns%2Fq8XPYfp%2FT5U2csm3nasMwRH28LLCUEzoLrnMOhO2mdkQHFYTEChLs5XdbpaM%2FrXpg%3D%3D"
decoding_auth_key = "BZF4W49MNogC/5NdkMns/q8XPYfp/T5U2csm3nasMwRH28LLCUEzoLrnMOhO2mdkQHFYTEChLs5XdbpaM/rXpg=="

xylist = pd.read_csv("./locate_data.csv", encoding='CP949', error_bad_lines=False)
uniq_xylist = xylist[['1단계', '2단계', '3단계','격자 X', '격자 Y']].drop_duplicates()

def test_func():
    global now_weather
    now_weather = nowcast("성수1가제1동")
    return now_weather

def find_xy(loc):
    xylist = pd.read_csv("./locate_data.csv", encoding='CP949', error_bad_lines=False)
    uniq_xylist = xylist[['1단계', '2단계', '3단계','격자 X', '격자 Y']].drop_duplicates()
    try:
        f_line = uniq_xylist[uniq_xylist['3단계'].str.contains(loc, na=False)]
    except:
        try:
            f_line = uniq_xylist[uniq_xylist['2단계'].str.contains(loc, na=False)]
        except:
            try:
                f_line = uniq_xylist[uniq_xylist['1단계'].str.contains(loc, na=False)]
            except:
                log.info("주소가 잘못되었습니다")
                return 0,0
    xy_list = f_line[["격자 X", "격자 Y"]].values
    return xy_list[0][0], xy_list[0][1]

def explain_data(information):
    explainline = ""
    for category, value in information:
        if category == "UUU" or category ==  "VVV":
            continue
        elif category == "PTY":
            value = int(value)
            explainline += " " +PTY_category(value) 
        elif category == "SKY":
            value = int(value)
            explainline += " " +SKY_category(value)
        elif category =="RN1":
            value = float(value)
            explainline += " " +RN1_category(value)
        else:
            explainline += " " +classify_category(category,value)
    return explainline

def classify_category(category, value):
    return {'T1H':'기온 {}℃ ','REH':'습도 {}%', 'VEC':'풍향 {}deg', 'WSD':'풍속 {} m/s'  }[category].format(value)

def PTY_category(value):
    return {0:'비없음', 1:"비", 2:"진눈깨비", 3:"눈", 4:"소나기", 5:"빗방울", 6:"빗방울/눈날림", 7:'눈날림'}[value]
def SKY_category(value):
    return {1:"맑음", 2: "구름조금", 3:"구름많음", 4:"흐림"}[value]
def LGT_category(value):
    return {0: "낙뢰 없음", 1:"낮음", 2:"보통"}

def RN1_category(value):
    if value < 0.1:
        return "강수량 0"
    elif value < 1.0:
        return "강수량 1mm 미만"
    elif value < 5.0:
        return "강수량 1~4mm"
    elif value < 10.0:
        return "강수량 5~9mm"
    elif value < 20.0:
        return "강수량 10~19mm"
    elif value < 40.0:
        return "강수량 20~39mm"
    elif value < 70.0:
        return "강수량 40~69mm"
    else: return "강수량 70mm 이상"

def nowcast(loc):
    x,y = find_xy(loc)
    time = datetime.datetime.now()
    today = time.strftime("%Y%m%d")
    now = time.strftime("%H%M")
    CallBackURL = 'http://apis.data.go.kr/1360000/VilageFcstInfoService/getUltraSrtNcst' ## 동네 단기 실황
    params = '?' + urlencode({ 
        quote_plus("serviceKey"): decoding_auth_key, # 인증키 
        quote_plus("numOfRows"): "10", # 한 페이지 결과 수 // default : 10 
        quote_plus("pageNo"): "1", # 페이지 번호 // default : 1 
        quote_plus("dataType"): "JSON", # 응답자료형식 : XML, JSON 
        quote_plus("base_date"): today, # 발표일자 // yyyymmdd 
        quote_plus("base_time"): now, # 발표시각 // HHMM, 매 시각 40분 이후 호출 
        quote_plus("nx"): x, # 예보지점 X 좌표 
        quote_plus("ny"): y # 예보지점 Y 좌표 
    })
    log.info(unquote(params))
    req = urllib.request.Request(CallBackURL + unquote(params))
    response_body = urlopen(req).read() # get bytes data
    json_data = json.loads(response_body)
    df = pd.DataFrame(json_data["response"]["body"]["items"]["item"])
    weather_data = df[["category", "obsrValue"]].values
    return explain_data(weather_data)


def forecast(loc):
    x,y = find_xy(loc)
    time = datetime.datetime.now()
    if time.minute < 40:
        time = time - datetime.timedelta(hours=1)
    today = time.strftime("%Y%m%d")
    now = time.strftime("%H%M")
    CallBackURL = 'http://apis.data.go.kr/1360000/VilageFcstInfoService/getUltraSrtFcst' ## 동네 예보
    params = '?' + urlencode({ 
        quote_plus("serviceKey"): decoding_auth_key, # 인증키 
        quote_plus("numOfRows"): "10", # 한 페이지 결과 수 // default : 10 
        quote_plus("pageNo"): "1", # 페이지 번호 // default : 1 
        quote_plus("dataType"): "JSON", # 응답자료형식 : XML, JSON 
        quote_plus("base_date"): today, # 발표일자 // yyyymmdd 
        quote_plus("base_time"): now, # 발표시각 // HHMM, 매 시각 40분 이후 호출 
        quote_plus("nx"): x, # 예보지점 X 좌표 
        quote_plus("ny"): y # 예보지점 Y 좌표 
    })
    log.info(unquote(params))
    req = urllib.request.Request(CallBackURL + unquote(params))

    response_body = urlopen(req).read() # get bytes data
    json_data = json.loads(response_body)
    df = pd.DataFrame(json_data["response"]["body"]["items"]["item"])
    weather_data = df.loc[["category","fcstTime", "fcstValue"]].values
    log.info(weather_data)

