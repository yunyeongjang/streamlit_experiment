import streamlit as st
import pandas as pd #pip install pandas in terminal
import joblib #pip install joblib in terminal
import json #pip install json in terminal
import re
from sklearn.preprocessing import MultiLabelBinarizer
from streamlit_option_menu import option_menu
import pydeck as pdk
import os
from PIL import Image
import ast

#초기화하기
if "initialized" not in st.session_state:
    all_keys = ['user_name', 'general_allergens', 'pollen_tree', 'pollen_grass', 'pollen_weed', 'check_pollen', 'check', 'rerun']
    for key in all_keys:
        with open(f"txt/{key}.txt", "w", encoding="utf-8") as f:
            f.write("")
        st.session_state.pop(key, None)
    st.session_state["initialized"] = True  # 다시 초기화되지 않도록 차단
    st.rerun()  # 새로고침

df = pd.read_excel('plants/알러지리스트.xlsx')
allergen_list = df.iloc[:,0].dropna().tolist()
allergen_list.sort()

all_list = {'user_name':"",
            'pollen_yesorno': '',
            'general_allergens':[],
            'pollen_tree':"",
            'pollen_grass':"",
            'pollen_weed':"",
            'check_pollen':'',
            'rerun': ''}

for i in all_list:
    if os.path.exists(f"txt/{i}.txt"):
        with open(f"txt/{i}.txt", "r", encoding="utf-8") as f:
            all_list[i] = f.read().strip()

#sidebar에 항상 표시
with st.sidebar:
    if all_list['rerun'] == 'rerun':
        for i in ['user_name', 'pollen_yesorno', 'general_allergens', 'pollen_tree', 'pollen_grass', 'pollen_weed',
                  'check_pollen']:
            file_path = f"txt/{i}.txt"
            if os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write('')
        with open("txt/rerun.txt", "w", encoding="utf-8") as f:
            f.write('')

        st.rerun()

    if all_list['rerun'] != 'rerun':
        if all_list['user_name']:
            st.markdown(
                f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'>👤 <b>현재 사용자</b>: {all_list['user_name']}</div>",
                unsafe_allow_html=True
            )

        if all_list['user_name'] != '' and all_list['pollen_yesorno'] == '있음' and all_list['general_allergens'] != []:
            st.write('---')
            st.markdown(
                f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'><b>{all_list['user_name']}의 알러지 리스트</b></div>",
                unsafe_allow_html=True)

            words = all_list['general_allergens'].split(',')  # 콤마 기준으로 나누기
            words = [w.strip() for w in words if w.strip()]
            for word in words:
                st.markdown(
                    f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'>- {word}</div>",
                    unsafe_allow_html=True)

            if '꽃가루' in words:
                st.markdown('---')
                st.markdown(
                    f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'><b>꽃가루 알러지</b></div>",
                    unsafe_allow_html=True)

                pollens = ['pollen_tree', 'pollen_grass', 'pollen_weed']
                df = pd.DataFrame(
                    data=[['🌿 풀 꽃가루', all_list['pollen_grass']],
                          ['🌳 나무 꽃가루', all_list['pollen_tree']],
                           ['🌾 잔디 꽃가루', all_list['pollen_weed']]],
                    columns = ['알러지 항목', '여부'])
                st.dataframe(df, hide_index = True)

        elif all_list['user_name'] != '' and all_list['pollen_yesorno'] == '없음':
            st.write('---')
            st.markdown(
                f"<div style='font-size:15px; font-weight:400; margin-bottom:10px;'><b>{all_list['user_name']}의 알러지 정보 없음</b></div>",
                unsafe_allow_html=True)




pages = {
    "": [st.Page("메인.py", title="홈", icon="🏠"),
            st.Page("1_사용자입력.py", title="사용자 정보 입력", icon="📝"),
            st.Page("2_식물.py", title="식물 & 알레르기", icon="🌿"),
            st.Page("3_절지동물.py", title="절지동물 정보", icon="🦗")]
}


pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()



