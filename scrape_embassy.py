import requests
from bs4 import BeautifulSoup
import json
import datetime

# 모니터링할 URL
URL = "https://embassywatch.gkuer.com/"

# 데이터를 저장할 JSON 파일 이름
JSON_FILE = "embassy_status.json"
# 정상 국가 목록을 저장할 정적 파일
NORMAL_LIST_FILE = "normal_countries.json" 

# [!! 신규 !!] 파이썬으로 시간 포맷팅 (JS 로직 복제)
def format_python_time(date_obj):
    """JS의 formatTime 함수와 동일하게 KST 시간 객체를 포맷팅합니다."""
    y = date_obj.year
    m = date_obj.month
    d = date_obj.day
    h = date_obj.hour
    
    is_am = h < 12
    period = "오전" if is_am else "오후"
    
    h_12 = h % 12 or 12 # 0시를 12시로 변경
    
    # JS 로직은 6시간 단위이므로 분은 항상 00입니다.
    minutes_str = "00" 
    
    return f"{y}년 {m}월 {d}일 {period} {h_12}:{minutes_str}"

def scrape_embassy_status():
    print(f"[{datetime.datetime.now()}] 스크래핑 시작: {URL}")
    
    last_update_time = "" 
    
    # [!! 수정 !!] JS 로직을 Python으로 직접 계산 (스크래핑 대신)
    try:
        # 1. UTC 기준 현재 시간
        now_utc = datetime.datetime.utcnow()
        # 2. KST (UTC+9)
        korea_time = now_utc + datetime.timedelta(hours=9)
        hour_kst = korea_time.hour
        
        # 3. 마지막 6시간 단위 계산 (0, 6, 12, 18시)
        last_check_hour_kst = (hour_kst // 6) * 6
        
        # 4. 마지막 확인 시간 객체 생성 (분, 초 0으로)
        last_check_time = korea_time.replace(hour=last_check_hour_kst, minute=0, second=0, microsecond=0)
        
        # 5. 포맷팅
        last_update_time = format_python_time(last_check_time)
        print(f"업데이트 시간 계산됨: {last_update_time}")
        
    except Exception as e:
        print(f"오류: 시간 계산 실패. {e}")
        last_update_time = "시간 계산 오류" # 실패 시

    # --- (이하 국가 목록 스크래핑) ---
    
    withdrawal_list = []
    normal_list = []
    output_data_list = [] # 최종 아이템 리스트
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")
        
        # --- 국가 목록 처리 ---
        country_items = soup.find_all("div", class_="country-item")
        
        if not country_items:
            print("오류: 'country-item' 요소를 찾을 수 없습니다.")
            # (리스트는 비어있는 상태로 둠)
        else:
            for item in country_items:
                country = item.find("strong").get_text(strip=True).replace(":", "")
                item_text = item.get_text(strip=True)
                status_full_text = item_text.replace(country + ":", "").strip()

                if status_full_text == "철수 소식 없음":
                    normal_list.append(country)
                else:
                    link_tag = item.find("a")
                    link_url = URL
                    
                    if link_tag and link_tag.get('href'):
                        link_url = link_tag.get('href')

                    status_description = status_full_text.split("확인된 링크:")[0].strip()
                    if not status_description:
                        status_description = status_full_text

                    withdrawal_list.append({
                        "title": f"🚨 [긴급] {country} 대사관: {status_description}",
                        "status": "withdrawal",
                        "link": link_url
                    })

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져오는 데 실패했습니다. {e}")
    except Exception as e:
        print(f"오류: 데이터 처리 중 문제가 발생했습니다. {e}")

    # --- 최종 JSON 데이터 생성 ---
    
    if withdrawal_list:
        # 긴급 상황이 하나라도 있으면 긴급 목록만 출력
        print(f"!!! 긴급 상황 감지: {len(withdrawal_list)}개국")
        output_data_list = withdrawal_list
    elif normal_list:
        # 긴급 상황이 없고, 정상 목록이 있으면
        print(f"모든 대사관 정상: {len(normal_list)}개국")
        
        # [!! 수정 !!] title 형식을 요청하신 대로 변경
        output_data_list = [{
            "title": f"{len(normal_list)}개국 주한 대사관 철수 소식 없음", 
            "status": "normal",
            "link": URL
        }]
        
        # 정상 국가 목록을 별도 파일로 저장
        try:
            with open(NORMAL_LIST_FILE, "w", encoding="utf-8") as f_countries:
                json.dump(normal_list, f_countries, ensure_ascii=False, indent=2)
            print(f"{NORMAL_LIST_FILE} 파일에 {len(normal_list)}개국 목록 저장 완료.")
        except Exception as e:
            print(f"오류: {NORMAL_LIST_FILE} 파일 저장 실패. {e}")
    else:
        # 긴급 상황도 없고, 정상 목록도 없는 경우 (스크래핑 실패 등)
        print("경고: 스크래핑된 국가 정보가 없습니다. (사이트 변경 또는 스크래핑 실패)")
        output_data_list = [{
            "title": "대사관 정보를 가져올 수 없음",
            "status": "error",
            "link": URL
        }]

    # 최종 JSON 객체 생성 (시간 + 아이템 목록)
    final_json_output = {
        "lastUpdate": last_update_time,
        "items": output_data_list
    }

    # 최종 객체를 embassy_status.json 파일에 저장
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(final_json_output, f, ensure_ascii=False, indent=2)
        
    print(f"[{datetime.datetime.now()}] 스크래핑 완료. {JSON_FILE} 파일 생성됨.")


if __name__ == "__main__":
    scrape_embassy_status()
