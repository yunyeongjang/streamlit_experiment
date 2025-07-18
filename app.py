import streamlit as st
import pandas as pd

# ✅ 페이지 설정 (아이콘, 제목)
st.set_page_config(
    page_title="ForestGuard",
    page_icon="./plants/icon.jpg"
)

# ✅ 사용자 상태 초기화 (최초 1회만)
if "initialized" not in st.session_state:
    keys = [
        'user_name', 'pollen_yesorno', 'general_allergens',
        'pollen_tree', 'pollen_grass', 'pollen_weed',
        'check_pollen', 'rerun'
    ]
    for key in keys:
        st.session_state[key] = "" if key != "general_allergens" else []
    st.session_state["initialized"] = True
    st.rerun()

# ✅ 사용자 정보 불러오기
# user_name = st.session_state.get('saved_user_name', '')
# pollen_yesorno = st.session_state.get('saved_pollen_yesorno', '')
# general_allergens = st.session_state.get('saved_general_allergens', [])
# pollen_tree = st.session_state.get('saved_pollen_tree', '')
# pollen_grass = st.session_state.get('saved_pollen_grass', '')
# pollen_weed = st.session_state.get('saved_pollen_weed', '')

user_name = st.session_state.get('saved_user_name') or st.session_state.get('user_name', '')
pollen_yesorno = st.session_state.get('saved_pollen_yesorno') or st.session_state.get('pollen_yesorno', '')
general_allergens = st.session_state.get('saved_general_allergens') or st.session_state.get('general_allergens', [])
pollen_tree = st.session_state.get('saved_pollen_tree') or st.session_state.get('pollen_tree', '')
pollen_grass = st.session_state.get('saved_pollen_grass') or st.session_state.get('pollen_grass', '')
pollen_weed = st.session_state.get('saved_pollen_weed') or st.session_state.get('pollen_weed', '')

# ✅ 사이드바 표시
with st.sidebar:
    if user_name:
        st.markdown(
            f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'>👤 <b>현재 사용자</b>: {user_name}</div>",
            unsafe_allow_html=True
        )

        if pollen_yesorno == '있음' and general_allergens:
            st.write('---')
            st.markdown(
                f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'><b>{user_name}의 알러지 리스트</b></div>",
                unsafe_allow_html=True
            )

            for word in general_allergens:
                st.markdown(
                    f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'>- {word}</div>",
                    unsafe_allow_html=True
                )

            if '꽃가루' in general_allergens:
                st.markdown('---')
                st.markdown(
                    f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'><b>꽃가루 알러지</b></div>",
                    unsafe_allow_html=True
                )

                df = pd.DataFrame(
                    data=[
                        ['🌿 풀 꽃가루', pollen_grass],
                        ['🌳 나무 꽃가루', pollen_tree],
                        ['🌾 잔디 꽃가루', pollen_weed]
                    ],
                    columns=['알러지 항목', '여부']
                )
                st.dataframe(df, hide_index=True)

        elif pollen_yesorno == '없음':
            st.write('---')
            st.markdown(
                f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'><b>{user_name}의 알러지 정보 없음</b></div>",
                unsafe_allow_html=True
            )

# ✅ 페이지 연결
pages = {
    "": [
        st.Page("메인.py", title="홈", icon="🏠"),
        st.Page("1_사용자입력.py", title="사용자 정보 입력", icon="📝"),
        st.Page("2_식물.py", title="식물 & 알레르기", icon="🌿"),
        st.Page("3_절지동물.py", title="절지동물 정보", icon="🦗")
    ]
}

pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
