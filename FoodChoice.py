import streamlit as st
import requests
import ollama  # Ollama 라이브러리 사용
import re  # 정규표현식을 사용해 음식점 이름 추출

# Google Custom Search API 키 및 검색 엔진 ID
API_KEY = ''  # Google Cloud에서 발급받은 API 키
SEARCH_ENGINE_ID = ''  # Google Custom Search 엔진 ID

# 특정 키워드가 포함된 결과만 필터링 (맛집, 식당, 레스토랑, 카페)
FILTER_KEYWORDS = ['맛집', '식당', '레스토랑', '카페']

# 불필요한 결과(예: TikTok, Instagram)를 제외하는 필터링
EXCLUDE_KEYWORDS = ['TikTok', 'Instagram', '페이스북', '유튜브']

# Ollama를 사용해 사용자 입력에서 핵심 키워드를 추출하는 함수
def extract_keywords_with_ollama(user_query):
    # Ollama 클라이언트 초기화
    client = ollama.Client(host="/")  # 요청한 host로 설정

    response = client.chat(model='gemma2:9b', messages=[
        {'role': 'system', 'content': '사용자의 입력에서 핵심 키워드(장소, 음식 종류, 맛집 관련 단어)를 추출해서 제공해. 불필요한 텍스트나 이모티콘, 추가 설명을 넣지 마. "면세점" 처럼 음식과 관련 없는 정보는 절대 포함하지 말아야해'},
        {'role': 'user', 'content': user_query}
    ])
    
    if 'message' in response and 'content' in response['message']:
        keywords = response['message']['content']
        # 불필요한 이모티콘이나 텍스트가 섞여있을 경우 제거 (예: 이모티콘, 불필요한 단어)
        keywords = re.sub(r'[^\w\s/]', '', keywords)  # 알파벳, 숫자, /, 공백만 남기기
        return keywords.strip()  # Ollama에서 받은 키워드를 반환
    else:
        st.write("Ollama에서 키워드 추출에 실패했습니다.")
        return user_query  # 오류 시 원본 텍스트 반환

# Google Custom Search API를 사용하여 검색하는 함수
def search_google(query, sort_by_date=False):
    search_url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'num': 10,  # 최대 10개의 검색 결과 가져오기
        'dateRestrict': 'y2'  # 최근 2년 내 검색 결과로 제한
    }
    
    # 최신순으로 정렬하는 옵션 추가
    if sort_by_date:
        params['sort'] = 'date'

    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        search_results = response.json()
        return search_results.get('items', [])
    else:
        st.write(f"Google 검색에 실패했습니다. 상태 코드: {response.status_code}")
        return []

# 검색 결과에서 음식점 이름과 링크를 추출
def extract_restaurant_names_and_links(results):
    restaurant_data = []
    for result in results:
        title = result.get('title', '')
        link = result.get('link', '')
        snippet = result.get('snippet', '')
        
        # 제목과 설명에 TikTok, Instagram, YouTube와 같은 소셜 미디어 키워드가 포함된 경우 제외
        if any(exclude in title or exclude in snippet for exclude in EXCLUDE_KEYWORDS):
            continue
        
        # 제목에 '맛집', '식당', '레스토랑', '카페' 키워드가 포함된 경우에만 음식점 이름으로 추출
        if any(keyword in title for keyword in FILTER_KEYWORDS):
            restaurant_data.append({'name': title, 'link': link})
    
    return restaurant_data

# Google Maps 링크 생성
def generate_google_maps_link(restaurant_name):
    return f"https://www.google.com/maps/search/?api=1&query={restaurant_name.replace(' ', '+')}"

# Streamlit 앱 메인 함수
def main():
    st.title("Google & Ollama 기반 맛집 추천 시스템")
    
    # 사용자 입력 (하나의 입력 필드로 처리)
    user_query = st.text_input("찾고 싶은 장소와 위치를 입력하세요 (예: 숙대입구역 고기 맛집)")
    sort_by_date = st.checkbox("최신순으로 정렬")
    search_button = st.button("검색")
    
    if search_button:
        st.write(f"'{user_query}'에 대한 검색 결과를 찾고 있습니다...")

        # Ollama로 사용자 입력에서 키워드를 추출
        extracted_keywords = extract_keywords_with_ollama(user_query)
        st.write(f"Ollama가 추출한 키워드: '{extracted_keywords}'")

        # Google 검색 결과 가져오기
        google_search_results = search_google(extracted_keywords, sort_by_date=sort_by_date)

        # 음식점 이름과 링크 추출
        restaurant_data = extract_restaurant_names_and_links(google_search_results)

        # 검색 결과 출력
        st.write("Google 검색 결과:")
        if restaurant_data:
            for i, data in enumerate(restaurant_data, 1):
                # Google Maps 링크 생성
                google_maps_link = generate_google_maps_link(data['name'])
                
                # 결과 출력 (음식점 이름 + 원래 링크 + 구글 지도 링크)
                st.write(f"{i}. **음식점 이름**: {data['name']}")
                st.write(f"[원본 링크]({data['link']})")
                st.write(f"[Google Maps 링크]({google_maps_link})")
                st.write("---")
        else:
            st.write("검색 결과가 없습니다.")

if __name__ == "__main__":
    main()
