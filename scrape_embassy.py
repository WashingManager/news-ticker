import requests
from bs4 import BeautifulSoup
import json
import datetime

# 모니터링할 URL
URL = "https://embassywatch.gkuer.com/"

# 데이터를 저장할 JSON 파일 이름
JSON_FILE = "embassy_status.json"

def scrape_embassy_status():
    print(f"[{datetime.datetime.now()}] 스크래핑 시작: {URL}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8' # 한글 깨짐 방지

        soup = BeautifulSoup(response.text, "html.parser")
        country_items = soup.find_all("div", class_="country-item")

        withdrawal_list = []
        normal_list = []

        if not country_items:
            print("오류: 'country-item' 요소를 찾을 수 없습니다.")
            return

        for item in country_items:
            country = item.find("strong").get_text(strip=True).replace(":", "")
            
            # [!! 로직 개선 !!]
            # div의 전체 텍스트에서 국가명을 제외하여 상태 텍스트를 추출
            item_text = item.get_text(strip=True)
            status_full_text = item_text.replace(country + ":", "").strip()

            if status_full_text == "철수 소식 없음":
                # 1. 평시 상태
                normal_list.append(country)
            else:
                # 2. 긴급 상황 (철수 소식 없음이 아님)
                
                # [!! 신규 로직 !!]
                # 먼저, div 내부에서 <a> 태그 (확인된 링크)를 검색합니다.
                link_tag = item.find("a")
                link_url = URL  # 기본값 (Fallback)
                
                if link_tag and link_tag.get('href'):
                    # <a> 태그를 찾으면 해당 href를 사용
                    link_url = link_tag.get('href')

                # [!! 신규 로직 !!]
                # title에 "확인된 링크:" 텍스트가 포함되지 않도록 분리
                status_description = status_full_text.split("확인된 링크:")[0].strip()
                if not status_description:
                    status_description = status_full_text # 혹시 모를 예외 처리

                withdrawal_list.append({
                    "title": f"🚨 [긴급] {country} 대사관: {status_description}",
                    "status": "withdrawal",
                    "link": link_url # 찾은 링크 또는 기본 URL
                })

        output_data = []
        if withdrawal_list:
            # 긴급 상황이 하나라도 있으면 긴급 목록만 출력
            print(f"!!! 긴급 상황 감지: {len(withdrawal_list)}개국")
            output_data = withdrawal_list
        else:
            # 모두 정상이면 요약 메시지 하나만 출력
            print(f"모든 대사관 정상: {len(normal_list)}개국")
            output_data = [{
                "title": f"주한 대사관 현황: {len(normal_list)}개국 모두 정상 (철수 소식 없음)",
                "status": "normal",
                "link": URL # 평시 상태일 때도 link 필드는 유지
            }]

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"[{datetime.datetime.now()}] 스크래핑 완료. {JSON_FILE} 파일 생성됨.")

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져오는 데 실패했습니다. {e}")
    except Exception as e:
        print(f"오류: 데이터 처리 중 문제가 발생했습니다. {e}")

if __name__ == "__main__":
    scrape_embassy_status()
