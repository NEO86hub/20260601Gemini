# 【填空 1】匯入必要的套件
import streamlit as st
import json
from google import genai
from google.genai import types

# 頁面設定
st.set_page_config(page_title="附中 AI 導覽員")
st.title("陽明交大附中 - 86導覽") # 【填空 2】填入導覽員的名字

# 讀取背景知識
try: # 【填空 3】設定例外處理的開頭（嘗試執行）
    with open('tour.json', 'r', encoding='utf-8') as f: # 【填空 4、5】開啟檔案的函式與檔案名稱
    	context_data = json.load(f) # 【填空 6】將 JSON 檔案讀取為 Python 資料的函式
    	context_text = json.dumps(context_data, ensure_ascii=False)
except FileNotFoundError: # 【填空 7】捕捉例外的關鍵字
    st.error("找不到 tour.json 檔案")
    st.stop()
except Exception as e: # 【填空 8】捕捉其他所有例外的關鍵字
    st.error(f"讀取 JSON 發生錯誤：{e}")
    st.stop()

# 初始化 API 與對話
if "gemini_client" not in st.session_state:
	try: # 【填空 9】嘗試讀取金鑰
    	api_key = st.secrets["GEMINI_API_KEY"] # 【填空 10】Streamlit 讀取機密環境變數的屬性
        except KeyError: # 【填空 11】捕捉找不到金鑰的例外
        st.error("未找到 GEMINI_API_KEY")
        st.stop()

    # 建立 Gemini 客戶端
    client = genai.Client(api_key=api_key) # 【填空 12、13】建立客戶端與填入金鑰變數
    st.session_state.gemini_client = client

    system_instruction = (
        f"你是陽明交大附中導覽員「小北」。\n"
        f"請優先參考以下內容回答，若找不到請自動搜尋。\n\n"
        f"內容：\n{context_text}"
    )

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.7,
    )
    st.session_state.config = config

    # 設定使用 Gemini 模型
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash", # 【填空 14】填入 Gemini 2.5 Flash 的模型代號
        config=config
    )

    st.session_state.messages = [
        {"role": "assistant", "content": "你好，我是導覽員小北，請隨時發問。"}
    ]

# 顯示歷史紀錄
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): # 【填空 15】Streamlit 顯示對話氣泡的函式
        st.write(msg["content"])

# 處理使用者輸入
if prompt := st.chat_input("想問什麼事"): # 【填空 16】Streamlit 產生底部對話輸入框的函式
    st.chat_message("user").write(prompt)

    # 將使用者訊息加入歷史紀錄清單中
    st.session_state.messages.write({"role": "user", "content": prompt}) # 【填空 17】Python 串列新增元素的函式

    with st.spinner("處理中"): # 【填空 18】Streamlit 產生轉圈圈載入動畫的函式
        try:
            response = st.session_state.chat_session.send_message(prompt)
            response_text = response.text

            st.chat_message("assistant").write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            st.error(f"對話發生異常：{e}")
            st.info("可能是 API 或模型限制")
