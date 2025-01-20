import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

####### 본인 것으로 수정하기 ########
user_id = 'test-user@gmail.com'
################################
 
base_url = 'https://mir-api.52g.ai/v1'
url = f"{base_url}/chat-messages"

load_dotenv('.env-vars', override=True)
mir_api_key = os.getenv("MIR_API_KEY")


# 요청 데이터 구성
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {mir_api_key}"  # 필요한 경우 인증 토큰 추가
}


# Streamlit 채팅 UI 구현
st.sidebar.markdown("### 💬 대화 내역")

# 채팅 히스토리 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 채팅 히스토리 표시 (왼쪽 사이드바)
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.sidebar.markdown(f"👤 **You**: {message['content']}")
    else:
        st.sidebar.markdown(f"🤖 **AI**: {message['content']}")

# 메인 영역에 채팅 UI 표시
st.markdown("### 💬 AI 채팅")
    
# 채팅 입력 UI
with st.form(key='chat_form'):
    user_input = st.text_area("질문을 입력하세요:", key='user_input', height=100)
    submit_button = st.form_submit_button("전송")
    
    if submit_button and user_input:
        # 사용자 메시지 저장
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # API 요청 payload 구성
        payload = {
            "query": user_input,
            "inputs": {
                "query": user_input,
            },
            "response_mode": "streaming",
            "user": user_id,
            "conversation_id": "",
            "auto_generate_name": True
        }
        
        # 응답 표시를 위한 placeholder
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        chunk = json.loads(line[6:])
                        if chunk.get('answer'):
                            full_response += chunk.get('answer', '')
                            # 실시간으로 응답 업데이트
                            response_placeholder.markdown(full_response)
                
                # 완성된 응답을 채팅 히스토리에 저장
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
