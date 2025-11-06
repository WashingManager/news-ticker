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

def scrape_embassy_status():
    print(f"[{datetime.datetime.now()}] 스크래핑 시작: {URL}")
    
    # [!! 신규 !!] 마지막 업데이트 시간을 저장할 변수
    last_update_time = "" 
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8' # 한글 깨짐 방지

        soup = BeautifulSoup(response.text, "html.parser")
        
        # [!! 신규 !!] 마지막 확인시간 추출
        try:
            check_times_div = soup.find("div", id="checkTimes")
            if check_times_div and check_times_div.contents:
                # "마지막 확인시간: 2025년 11월 6일 오후 6:00 " 문자열 추출
                raw_text = check_times_div.contents[0].strip()
                # "마지막 확인시간:" 부분 제거
                last_update_time = raw_text.replace("마지막 확인시간:", "").strip()
                print(f"업데이트 시간 확인: {last_update_time}")
            else:
                print("경고: 'checkTimes' div 또는 시간을 찾을 수 없습니다.")
        except Exception as e:
            print(f"오류: 업데이트 시간 추출 실패. {e}")

        # --- 기존 국가 목록 처리 ---
        country_items = soup.find_all("div", class_="country-item")
        withdrawal_list = []
        normal_list = [] 

        if not country_items:
            print("오류: 'country-item' 요소를 찾을 수 없습니다.")
            return

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

        output_data_list = [] # [!! 수정 !!] 변수명을 리스트로 변경
        if withdrawal_list:
            print(f"!!! 긴급 상황 감지: {len(withdrawal_list)}개국")
            output_data_list = withdrawal_list
        else:
            print(f"모든 대사관 정상: {len(normal_list)}개국")
            output_data_list = [{
                "title": f"주한 대사관 현황: {len(normal_list)}개국 (철수 소식 없음)", 
                "status": "normal",
                "link": URL
            }]
            
            try:
                with open(NORMAL_LIST_FILE, "w", encoding="utf-8") as f_countries:
                    json.dump(normal_list, f_countries, ensure_ascii=False, indent=2)
                print(f"{NORMAL_LIST_FILE} 파일에 {len(normal_list)}개국 목록 저장 완료.")
            except Exception as e:
                print(f"오류: {NORMAL_LIST_FILE} 파일 저장 실패. {e}")

        # [!! 신규 !!] 최종 JSON 객체 생성 (시간 + 아이템 목록)
        final_json_output = {
            "lastUpdate": last_update_time,
            "items": output_data_list
        }

        # [!! 수정 !!] 최종 객체를 embassy_status.json 파일에 저장
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(final_json_output, f, ensure_ascii=False, indent=2)
            
        print(f"[{datetime.datetime.now()}] 스크래핑 완료. {JSON_FILE} 파일 생성됨.")

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져오는 데 실패했습니다. {e}")
    except Exception as e:
        print(f"오류: 데이터 처리 중 문제가 발생했습니다. {e}")

if __name__ == "__main__":
    scrape_embassy_status()
