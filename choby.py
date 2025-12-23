# choby.py

import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from prompt_template import system_prompt, build_user_prompt # 모듈 import

# 1. 환경 변수 및 클라이언트 초기화
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 2. JSON 저장 함수
def save_to_json(keyword, platform, content):
    file_path = "sns_posts.json"
    new_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "keyword": keyword,
        "platform": platform,
        "content": content
    }
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
        
    data.append(new_data)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return file_path 

# 3. 생성 함수
def generate_sns_post(keyword, platform):
    user_prompt = build_user_prompt(keyword, platform)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류 발생: {str(e)}" # 예외 발생시 문자열로 반환

# --- Streamlit UI ---
st.set_page_config(page_title="AI 포스팅 비서 CHOBY")
st.title("🤖AI 포스팅 비서 CHOBY")
st.markdown("최고의 결과물을 만드는 창의적 조력자 CHOBY입니다")

# 사이드바: 과거 기록
with st.sidebar:
    st.header("🕒 생성 기록")
    if os.path.exists("sns_posts.json"):
        with open("sns_posts.json", "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
                for item in reversed(history[-5:]):
                    st.markdown(f"**[{item['platform']}]** {item['keyword']}")
                    st.caption(item['timestamp'])
                    st.divider()
            except:
                st.caption("기록을 불러오는 중 오류가 발생했습니다.")

# 메인 UI
keyword = st.text_input("💡 어떤 주제로 글을 쓸까요?", placeholder="예: 제주도 맛집, 파이썬 공부법")
platform = st.selectbox("📱 플랫폼을 선택하세요", ["인스타그램", "네이버 블로그", "X(트위터)"])

if st.button("✨ 게시글 생성하기"):
    if keyword:
        with st.spinner(f'{platform} 맞춤형 글을 작성 중입니다...'):
            result = generate_sns_post(keyword, platform)
            save_to_json(keyword, platform, result)
            
            st.success("게시글이 완성되었습니다!")
            st.subheader(f"📝 생성된 {platform} 게시글")
            st.text_area("결과", value=result, height=300)
            
            st.download_button(
                label="📥 결과 다운로드 (JSON)",
                data=json.dumps(result, ensure_ascii=False),
                file_name=f"post_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    else:
        st.warning("키워드를 입력해 주세요!")