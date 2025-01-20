""" 대화내역 + 채팅 """

import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

####### 본인 것으로 수정하기 ########
user_id = 'email_address' # example: 'xxx@gmail.com'
################################
 
base_url = 'https://mir-api.52g.ai/v1'

load_dotenv('.env-vars', override=True)
mir_api_key = os.getenv("MIR_API_KEY")

# 요청 헤더 구성
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {mir_api_key}"
}

# 대화 목록을 가져오는 함수
def get_conversations():
    conversations_url = f"{base_url}/conversations"
    params = {"user": user_id}
    try:
        response = requests.get(conversations_url, headers=headers, params=params)
        print(f"{response.json()}\n\n")
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            st.error(f"Error fetching conversations: {response.text}")
            return []
    except requests.RequestException as e:
        st.error(f"Request failed: {e}")
        return []

# 특정 대화의 메시지 히스토리를 가져오는 함수
def get_conversation_history(conversation_id):
    history_url = f"{base_url}/messages"
    params = {"user": user_id, "conversation_id": conversation_id}
    try:
        response = requests.get(history_url, headers=headers, params=params)
        print(f"{response.json()}\n\n")
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            st.error(f"Error fetching conversation history: {response.text}")
            return []
    except requests.RequestException as e:
        st.error(f"Request failed: {e}")
        return []

# Streamlit UI 구성
st.sidebar.markdown("### 💬 대화 목록")

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = ""

# 대화 목록 표시 및 선택
conversations = get_conversations()
for conv in conversations:
    if st.sidebar.button(f"📝 {conv.get('name', 'Unnamed conversation')}", key=conv['id']):
        st.session_state.chat_history = []
        
        st.session_state.current_conversation_id = conv['id']
        messages = get_conversation_history(conv['id'])
        
        for msg in messages:
            if msg['query']:
                st.session_state.chat_history.append({"role": "user", "content": msg['query']})
            if msg['answer']:
                st.session_state.chat_history.append({"role": "assistant", "content": msg['answer']})
        st.rerun()

# 메인 영역에 채팅 UI 표시
st.markdown("### 💬 AI 채팅")

# 현재 대화 내역 표시
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"👤 **You**: {message['content']}")
    else:
        st.markdown(f"🤖 **AI**: {message['content']}")
    
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
            "conversation_id": st.session_state.current_conversation_id,
            "auto_generate_name": True
        }
        
        # 응답 표시를 위한 placeholder
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            chat_url = f"{base_url}/chat-messages"
            response = requests.post(chat_url, headers=headers, data=json.dumps(payload), stream=True)
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
                
                # 새로운 대화인 경우 conversation_id 업데이트
                if not st.session_state.current_conversation_id and chunk.get('conversation_id'):
                    st.session_state.current_conversation_id = chunk.get('conversation_id')
                st.rerun()
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
