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
        # User-Agent를 설정하여 봇 차단 방지
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()  # 오류가 발생하면 예외 발생

        soup = BeautifulSoup(response.text, "html.parser")

        # 'country-item' 클래스를 가진 모든 div 태그를 찾음 (총 91개)
        country_items = soup.find_all("div", class_="country-item")

        withdrawal_list = []  # 철수/이상 상태 국가 목록
        normal_list = []      # 정상 상태 국가 목록

        if not country_items:
            print("오류: 'country-item' 요소를 찾을 수 없습니다. 페이지 구조가 변경되었을 수 있습니다.")
            return

        for item in country_items:
            country = item.find("strong").get_text(strip=True).replace(":", "")
            # <strong> 태그 다음의 텍스트 노드가 상태 정보임
            status = item.strong.next_sibling.strip()

            if status != "철수 소식 없음":
                # 평시 상태가 아닐 경우
                withdrawal_list.append({
                    "title": f"🚨 [긴급] {country} 대사관: {status}",
                    "status": "withdrawal",
                    "link": URL
                })
            else:
                normal_list.append(country)

        output_data = []
        if withdrawal_list:
            # 철수/이상 국가가 하나라도 있으면
            print(f"!!! 긴급 상황 감지: {len(withdrawal_list)}개국")
            output_data = withdrawal_list
        else:
            # 모든 국가가 정상이면
            print(f"모든 대사관 정상: {len(normal_list)}개국")
            output_data = [{
                "title": f"주한 대사관 현황: {len(normal_list)}개국 모두 정상 (철수 소식 없음)",
                "status": "normal",
                "link": URL
            }]

        # JSON 파일로 저장 (UTF-8 인코딩)
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"[{datetime.datetime.now()}] 스크래핑 완료. {JSON_FILE} 파일 생성됨.")

    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지를 가져오는 데 실패했습니다. {e}")
    except Exception as e:
        print(f"오류: 데이터 처리 중 문제가 발생했습니다. {e}")

if __name__ == "__main__":
    scrape_embassy_status()
