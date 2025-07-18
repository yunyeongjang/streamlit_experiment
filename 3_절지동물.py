import streamlit as st

import pandas as pd  # pip install pandas in terminal
import scanpy as sc  # pip install scanpys in terminal

import joblib  # pip install joblib in terminal
import json  # pip install json in terminal

import re
from sklearn.preprocessing import MultiLabelBinarizer

from streamlit_option_menu import option_menu

import time

import pydeck as pdk

import os

from PIL import Image
from st_pages import add_page_title, get_nav_from_toml

import base64
import time

# ✅ 사용자 입력값 session_state에서 직접 불러오기
user_name = st.session_state.get("saved_user_name", "")
general_allergens = st.session_state.get("saved_general_allergens", [])
pollen_tree = st.session_state.get("saved_pollen_tree", "")
pollen_grass = st.session_state.get("saved_pollen_grass", "")
pollen_weed = st.session_state.get("saved_pollen_weed", "")
pollen_yesorno = st.session_state.get("saved_pollen_yesorno", "")
cols1 = st.session_state.get("cols1", [])
cols2 = st.session_state.get("cols2", [])



@st.cache_resource
def load_model(model_path):
    return joblib.load(model_path)


@st.cache_resource
def load_features(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_excel(path):
    return pd.read_excel(path)


@st.cache_data
def prepare_map_data(df, selected_class):
    max_dict = df.groupby('목')['개체수'].max().to_dict()
    this_max = max_dict.get(selected_class, 1)
    global_max = max(max_dict.values())
    scale_factor = this_max / global_max

    filtered_df = df[df['목'] == selected_class].copy()
    filtered_df['목내_비율'] = filtered_df['개체수'] / this_max
    filtered_df['목내_비율'] = filtered_df['목내_비율'].clip(0, 1).fillna(0)

    filtered_df['fill_color'] = filtered_df['목내_비율'].apply(
        lambda x: [255, 0, 0, int(100 + x * 155)]
    )

    filtered_df['반지름'] = filtered_df['목내_비율'].apply(
        lambda x: int((1500 + x * (4000 - 1500)) * scale_factor)
    )

    return filtered_df[['조사지명', '위도', '경도', '개체수', '반지름', 'fill_color']].dropna()

@st.cache_data
def load_harmful_species():
    return pd.read_excel("anthropods/bugs.xlsx")

@st.cache_data(show_spinner=False)
def load_encoded_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


st.header("🕷 절지동물 정보")

df = pd.read_excel('anthropods/절지동물_강_리스트.xlsx')
anthropods_list = df.iloc[:, 0].dropna().tolist()
anthropods_list.sort()

# 탭 버튼 스타일 변경
st.markdown("""
    <style>
    /* 탭 버튼 전체 스타일 */
    div[data-testid="stTabs"] button {
        padding: 15px 40px !important;
        height: 50px !important;
    }

    /* 탭 텍스트 스타일 */
    div[data-testid="stTabs"] button p {
        font-size: 15px !important;
        font-weight: 600 !important;
        margin: 0 !important;
        color: black !important;
    }

    /* 선택된 탭 배경색 */
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #e8f5e9 !important;  /* 회색 배경 */
    }

    /* ✅ 하단 밑줄 애니메이션 스타일 */
    div[data-baseweb="tab-highlight"] {
        background-color: #8bc34a !important;  /* 연두색 밑줄 */
        height: 2px !important;                /* 얇은 두께 */
        transition: all 0.3s ease-in-out;
    }
    </style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🐝 알레르기 예측", "🕷 절지동물 지도", "⚠️ 유해종 리스트"])

with tab1:
    st.markdown("<div style='font-size:20px; font-weight:600; margin-bottom:20px;'>🐝 절지동물 알레르기 예측</div>",
                unsafe_allow_html=True)
    st.markdown('''
- 사용자의 알레르기 입력을 바탕으로, 다음 정보를 제공합니다:

  벌독·바퀴벌레 알러지 위험도를 확률로 예측합니다.''')

    # ✅ 버튼 스타일 커스터마이징 (한 번만 실행되면 됨)
    st.markdown("""
            <style>
            button[kind="primary"] {
                padding: 4px 12px !important;
                font-size: 14px !important;
                height: 35px !important;
            }
            </style>
        """, unsafe_allow_html=True)

    # 예측 상태 초기화
    if "predicted_anthropod" not in st.session_state:
        st.session_state["predicted_anthropod"] = False


    if user_name == '' or pollen_yesorno == '없음' and general_allergens == '' or pollen_yesorno == '' or '꽃가루' in general_allergens and pollen_tree == '' or pollen_tree == '' or pollen_tree == '':
        st.write('---')
        st.write('사용자입력 페이지에서 입력을 완료한 뒤 이용해주세요.')

    elif len(general_allergens) == 0:
        st.write('❌ **알레르기 환자 정보가 한정적이라, 알레르기 반응을 예측할 수 없는 상황입니다.**')
        cols1 = st.session_state['cols1']
        cols2 = st.session_state['cols2']
        cols = list(set(cols1) | set(cols2))

        st.markdown(f"""
                                            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; background-color: #f9f9f9;">
                                                <b>알러지를 분석 위해 필요한 항원 리스트:</b><br>
                                                {', '.join(cols)}
                                            </div>
                                            """, unsafe_allow_html=True)


    else:

        # 🔁 기존 함수 수정 (변수명, 반환 동일)
        def make_feature_vector(json_path):
            features = load_features(json_path)  # 캐싱 사용
            vec = [1 if feat in general_allergens or
                        (feat == "나무 꽃가루" and pollen_tree == "있음") or
                        (feat == "풀 꽃가루" and pollen_grass == "있음") or
                        (feat == "잔디 꽃가루" and pollen_weed == "있음")
                   else 0 for feat in features]
            return vec


        def run_prediction(model_path, input_vector):
            if "bee" in model_path.lower():  # 예: model_bee_venom.pkl
                threshold = 0.50
            elif "바퀴벌레" in model_path or "roach" in model_path.lower():
                threshold = 0.40
            else:
                threshold = 0.50  # 기본값

            model = load_model(model_path)  # 캐싱 사용
            proba = model.predict_proba([input_vector])[0][1]
            pred = int(proba > threshold)
            return pred, proba


        # 🔘 예측 실행 여부 묻기
        if not st.session_state["predicted_anthropod"]:
            st.write("절지동물(벌독, 바퀴)에 대한 알레르기 위험도를 예측하시겠습니까?")
            if st.button("예측 실행"):
                progress_bar = st.progress(0)
                for i in range(101):
                    time.sleep(0.005)  # 빠르게 올라가게 5ms로 설정
                    progress_bar.progress(i)
                st.session_state["predicted_anthropod"] = True
                st.rerun()

        predict_allergen = []

        # ✅ 예측 결과 출력
        if st.session_state["predicted_anthropod"]:
            if "벌독" not in general_allergens:
                st.write("**🐝 벌독 알레르기 예측**")
                vec_bee = make_feature_vector("anthropods/models/feature_columns_bee_venom.json")
                pred, prob = run_prediction("anthropods/models/model_bee_venom.pkl", vec_bee)
                st.session_state["pred_bee"] = pred
                # st.json({f"{i}: {v}": "" for i, v in enumerate(vec_bee)})  # 벡터 디버깅용
                if pred:
                    st.error(f"❗ 벌독 알레르기 위험! (예측 확률: {prob:.2%}, threshold: 50%)")
                    predict_allergen.append('벌독')
                else:
                    st.success(f"✅ 벌독 알레르기 가능성 낮음 (예측 확률: {prob:.2%}, threshold: 50%)")
            else:
                st.info("사용자가 이미 벌독 알레르기를 가지고 있습니다.")
                st.session_state["pred_bee"] = None
                predict_allergen.append('벌독')

            if "바퀴벌레" not in general_allergens:
                st.write("**🪳 바퀴벌레 알레르기 예측**")
                vec_roach = make_feature_vector("anthropods/models/feature_columns_바퀴벌레.json")
                pred, prob = run_prediction("anthropods/models/model_바퀴벌레.pkl", vec_roach)
                st.session_state["pred_roach"] = pred
                # st.json({f"{i}: {v}": "" for i, v in enumerate(vec_roach)})  # 벡터 디버깅용
                if pred:
                    st.error(f"❗ 바퀴벌레 알레르기 위험! (예측 확률: {prob:.2%}, threshold: 40%)")
                    predict_allergen.append('바퀴벌레')
                else:
                    st.success(f"✅ 바퀴벌레 알레르기 가능성 낮음 (예측 확률: {prob:.2%}, threshold: 40%)")
            else:
                st.info("사용자가 이미 바퀴벌레 알레르기를 가지고 있습니다.")
                st.session_state["pred_roach"] = None
                predict_allergen.append('바퀴벌레')

            # 🔁 다시 예측 버튼
            if st.button("초기화"):
                for key in ["predicted_anthropod", "pred_bee", "pred_roach", "show_anthropod_distribution"]:
                    st.session_state.pop(key, None)
                st.rerun()

            # 👇 예측 결과 이후에 이어붙이기 (tab1 내부)
            # 1. 알러지 유무 판단 (직접 입력 or 예측 결과)
            # ?? 이거 뭐지요?
            bee_allergy = ("벌독" in general_allergens) or st.session_state.get("pred_bee") == 1
            roach_allergy = ("바퀴벌레" in general_allergens) or st.session_state.get("pred_roach") == 1
            #
            #
            # # 2. 분포 확인 여부 질문
            # if bee_allergy or roach_allergy:
            #     st.write("---")
            #     st.markdown("**해당 절지동물의 분포를 지역별로 확인하시겠습니까?**")
            #     if st.button("지역별 분포 확인"):
            #         st.session_state["show_anthropod_distribution"] = True
            #         st.rerun()
            #
            # # 3. 시/도 → 상세주소 선택 → 해당 지역 데이터 출력
            # if st.session_state.get("show_anthropod_distribution"):
            #     st.write("---")
            #     st.markdown("### 📍 지역 선택")
            #
            #     df_all = pd.read_excel("anthropods/개별산검색.xlsx")
            #
            #     # 시/도 목록 추출
            #     province_list = sorted(df_all['시/도'].dropna().unique().tolist())
            #     selected_province = st.selectbox("시/도 선택", province_list, index=None, placeholder="시/도 선택")
            #
            #     if selected_province:
            #         # 해당 시/도의 상세주소 목록
            #         sub_df = df_all[df_all['시/도'] == selected_province]
            #         sub_list = sorted(sub_df['상세주소'].dropna().unique().tolist())
            #         selected_detail = st.selectbox("상세주소 선택", sub_list, index=None, placeholder="상세주소 선택")
            #
            #         if selected_detail:
            #             st.markdown(f"#### ✅ {selected_detail} 지역에서 조심해야 할 절지동물")
            #
            #             df = df_all[df_all['상세주소'] == selected_detail].copy()
            #
            #
            #             def show_filtered_df(df_target, keywords, label):
            #                 # 문자열이면 리스트로 변환
            #                 if isinstance(keywords, str):
            #                     keywords = [keywords]
            #
            #                 # 키워드 포함한 목 필터링
            #                 df_filtered = df_target[df_target['목'].isin(keywords)]
            #
            #                 if not df_filtered.empty:
            #                     # 출력할 컬럼 선택
            #                     columns = ['강', '목']
            #                     if '과' in df_filtered.columns:
            #                         columns.append('과')
            #                     if '개체수' in df_filtered.columns:
            #                         columns.append('개체수')
            #
            #                     # 중복 제거 없이 전체 개체수 합산 포함해서 보여주기
            #                     total_count = df_filtered['개체수'].sum()
            #                     st.markdown(f"#### {label} (총 개체수: {total_count:,}마리)")
            #                     st.dataframe(df_filtered[columns].reset_index(drop=True), use_container_width=True)
            #                 else:
            #                     st.info(f"{label} 관련 절지동물이 이 지역에 존재하지 않습니다.")
            #
            #
            #             if bee_allergy:
            #                 bee_keywords = ["벌"]
            #                 show_filtered_df(df, bee_keywords, "🐝 벌")
            #
            #             if roach_allergy:
            #                 show_filtered_df(df, "바퀴", "🪳 바퀴벌레")

            if len(predict_allergen) > 0:
                st.write('---')
                st.write(f'**{", ".join(predict_allergen)}**에 대해 주의가 필요한 상황입니다. **알러지 시 주의사항** 확인하시겠습니까?')
                if st.button("확인"):
                    # ?? 아래 내용은 출처 확인이 필요한 상황/수정하겠음
                    if '바퀴벌레' in predict_allergen:
                        st.subheader("🪳 바퀴벌레 알레르기")

                        st.markdown("""
                    **1) 회피 방법**  
                    - 낙엽, 부식목, 돌 틈 등 습하고 어두운 장소 피하기  
                    - 야영 전 텐트·침낭 내부 바퀴벌레 확인  
                    - 음식물은 밀폐 보관하고 잔여물 방치 금지  
                    - 장갑·마스크 착용 후 청소, HEPA 필터 진공청소기 권장

                    **2) 대처 방법**  
                    - 기침, 쌕쌕거림, 호흡곤란 시 즉시 활동 중단 및 휴식  
                    - 흡입제 또는 항히스타민제 사용  
                    - 증상 지속 시 119 구조 요청 및 대피소 이동  
                    - 중증 병력자는 의료경고팔찌 착용 권장
                    """)
                        st.markdown('\n')
                        st.markdown('\n')
                        st.markdown(
                            "<div style='font-size:12px; font-weight:400; color:gray;'>Texas A&M AgriLife Extension Service. (n.d.). IPM Action Plan for Outdoor Cockroaches. In Pest Management Plans. School Integrated Pest Management. Texas A&M AgriLife Extension Service. Retrieved July 17, 2025, from https://buly.kr/EooGdaT</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "<div style='font-size:12px; font-weight:400; color:gray;'>U.S. Environmental Protection Agency. (2025, March 13). Cockroaches and schools. In Managing Pests in Schools. Retrieved July 17, 2025, from https://buly.kr/jZeAKS</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "<div style='font-size:12px; font-weight:400; color:gray;'>NHS. (n.d.). Anaphylaxis. Retrieved July 17, 2025, from https://buly.kr/28ti0sC</div>",
                            unsafe_allow_html=True
                        )

                    if '벌독' in predict_allergen:
                        st.subheader("🐝 벌독 알레르기")
                        st.write('벌독 알레르기가 있으면, 지네ㆍ벌에 물렸을 때 과한 반응을 보일 것')

                        st.markdown("""
                    **1) 회피 방법**  
                    - 향수, 밝은색 옷, 과일 음료 노출 자제  
                    - 벌집, 부식목, 돌밑에 손 대지 않기  
                    - 돗자리·깔개 사용, 피부 노출 최소화  
                    - 벌 접근 시 팔 휘두르지 말고 조용히 피하기

                    **2) 대처 방법**
                    - 끝이 무딘 도구로 침 제거
                    - 얼음찜질로 통증과 부기 완화  
                    - 쏘인 부위를 심장보다 높게 유지해 부기 완화  
                    - 증상 경미해도 병원 내원 필수  
                    - 지네 물림 후 알레르기 반응 시 동일 대응
                    """)
                        st.markdown('\n')
                        st.markdown('\n')
                        st.markdown(
                            "<div style='font-size:12px; font-weight:400; color:gray;'>American College of Allergy, Asthma, and Immunology. (n.d.). Insect sting allergies. Retrieved July 17, 2025, from https://buly.kr/1ucF4U</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "<div style='font-size:12px; font-weight:400; color:gray;'>NHS. (n.d.). Insect bites and stings. Retrieved July 17, 2025, from https://buly.kr/7bHCQ9m</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "<div style='font-size:12px; font-weight:400; color:gray;'>NHS. (n.d.). Anaphylaxis. Retrieved July 17, 2025, from https://buly.kr/28ti0sC</div>",
                            unsafe_allow_html=True
                        )

            else:
                st.write('---')
                st.write('벌독, 바퀴벌레 알러지에 대해 주의가 필요하지 않습니다.')

    with tab2:
        st.subheader("🕷 절지동물 지도")
        # 절지동물 탭 선택 시

        # 제목 (상단 여백 약간 추가)
        # st.markdown(
        #     "<div style='font-size:22px; font-weight:600; margin-top:0px; margin-bottom:15px;'>절지동물 지도</div>",
        #     unsafe_allow_html=True
        # )

        # 설명 텍스트와 간격 조정
        st.markdown(
            "<div style='font-size:16px; font-weight:400; margin-bottom:15px;'>•  삼림청 절지동물분포조사에 포함된 개체수 기반으로 출력됩니다.</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='font-size:16px; font-weight:400; margin-bottom:15px;'>•  빨간 점🔴에 커서를 올리면, 개체수와 위치 정보를 알 수 있습니다.</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='font-size:16px; font-weight:400; margin-bottom:30px;'>•  유해종 리스트와 등산로별로 나타나는 절지동물을 알고 싶다면, 지도 아래의 검색창을 활용해보세요.</div>",
            unsafe_allow_html=True
        )

        st.markdown("""
            <style>
            /* multiselect 내부 선택된 박스 스타일 변경 */
            span[data-baseweb="tag"] {
                background-color: #2e7d32 !important;
                color: #e8f5e9 !important;
                border: 1px solid #2e7d32 !important;
                font-weight: 500;
            }
            </style>
            """, unsafe_allow_html=True)

        # 👉 기존 절지동물 지도 코드 전부 여기에 넣기 (pydeck, radio 등)
        selected = option_menu(
            None,
            anthropods_list,  # 지네, 곤충, 거미, 노래기, 갑각
            icons=["bug", "bug-fill", "bug", "bug-fill", "bug"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            key="main_menu",  # ← 고유한 key 추가
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "#2c3e50", "font-size": "22px"},
                "nav-link": {
                    "font-size": "20px",
                    "text-align": "center",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#a2d5c6"},
            }
        )

        if selected == '지네':
            st.write('- 서식: 습기 찬 돌 밑, 흙 속, 나무 아래 등')
            st.write('- 생김새: 갈색~빨간색, 동굴 종은 색소 부족, 크기는 수 mm ~ 최대 30㎝')
            st.write('※ 내용은 네이버 지식백과 「지네류」(동물학백과)를 바탕으로 재구성하였습니다.')
        elif selected == '거미':
            st.write('- 서식: 대부분 육상 생활/진드기목, 거미목 일부 종은 수중 생활')
            st.write('- 생김새: 대부분 흰색·갈색·흑갈색/일부 거미목 종은 화려함/0.15mm ~ 25cm')
            st.write('※ 내용은 네이버 지식백과 「거미류」(두산백과)를 바탕으로 재구성하였습니다.')
        elif selected == '노래기':
            st.write('- 서식: 주로 육상 서식')
            st.write('- 생김새: 원통형, 단단한 외골격')
            st.write('※ 내용은 네이버 지식백과 「노래기강」(생명과학대사전)를 바탕으로 재구성하였습니다.')
        elif selected == '곤충':
            st.write('- 서식: 육상 환경에 가장 풍부히 분포')
            st.write('- 생김새: 몸이 고리마디 구조로 되어 있으며, 머리-가슴-배 구조')
            st.write('※ 내용은 네이버 지식백과 「곤충」(두산백과)를 바탕으로 재구성하였습니다.')
        elif selected == '갑각':
            st.write('- 서식: 수중생활, 아가미로 호흡')
            st.write('- 생김새: 탄산칼슘이 포함된 단단한 갑각이 존재')
            st.write('※ 내용은 네이버 지식백과 「갑각류」(두산백과)를 바탕으로 재구성하였습니다.')

        df = load_excel(f'anthropods/{selected}_절지동물.xlsx')  # ✅ 캐싱 적용
        intermediate_df = df.iloc[:, 3].dropna().tolist()
        anthropods_list = list(set(intermediate_df))

        selected_class = st.radio("", anthropods_list, horizontal=True)

        # ✅ 여기서부터 map_df 생성 완결
        map_df = prepare_map_data(df, selected_class)


        def scale_opacity(x, min_count=0, max_count=300, min_alpha=50, max_alpha=255):
            if pd.isna(x):
                return 0
            x = max(min_count, min(x, max_count))
            scale = (x - min_count) / (max_count - min_count)
            return int(min_alpha + scale * (max_alpha - min_alpha))


        map_df['반지름'] = map_df['개체수'].apply(lambda x: max(2800, min(4800, x * 35)))

        map_df['fill_color'] = map_df['개체수'].apply(
            lambda x: [255, 0, 0, max(100, min(255, int(x / 300 * 255)))]
        )

        # [2] 레이어
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[경도, 위도]',
            get_radius='반지름',
            get_fill_color='fill_color',
            pickable=True,
            auto_highlight=True,
        )

        # [3] 고정된 View 설정
        view_state = pdk.ViewState(
            latitude=36.2,
            longitude=127.8,
            zoom=6,
            pitch=0,
            bearing=0,
            min_zoom=6,
            max_zoom=6,
        )

        # [4] 툴팁 설정
        tooltip = {
            "html": "<b>조사지명:</b> {조사지명}<br><b>개체수:</b> {개체수}",
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": "12px"
            }
        }

        on = st.toggle('light-dark conversion')

        if on:
            # [5] pydeck Deck 객체 생성
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style='dark',
                tooltip=tooltip,
            )


        else:
            # [5] pydeck Deck 객체 생성
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style='light',
                tooltip=tooltip,
            )

        # [6] HTML로 렌더링 → Streamlit에 고정 삽입
        html_string = deck.to_html(as_string=True, notebook_display=False)

        # 👇 여기서 cursor 스타일을 덮어써줌 (canvas나 body에 적용)
        html_string = html_string.replace(
            "<body>",
            "<body><style>* { cursor: default !important; }</style>"
        )

        # Streamlit에 삽입
        st.components.v1.html(html_string, height=700)

        mountain_df = pd.read_excel('anthropods/절지동물_숲_리스트.xlsx')
        forest_list = sorted(set(mountain_df.iloc[:, 0].dropna().tolist()))

        st.write('---')

        st.markdown(
            "<div style='font-size:22px; font-weight:600; margin-top:15px; margin-bottom:5px;'>🕷 등산로별 절지동물 지도</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div style='font-size:16px; font-weight:400; margin-top:0px; margin-bottom:20px;'>삼림청 절지동물분포조사에 포함된 등산로만 검색 가능합니다.</div>",
            unsafe_allow_html=True
        )

        # 시/도 선택
        province_list = sorted(mountain_df.iloc[:, 0].dropna().unique().tolist())
        selected_province = st.selectbox("시/도 선택", province_list, index=None, placeholder="시/도 선택")

        # 선택된 시/도에 해당하는 상세주소(등산로) 목록 추출
        matched_rows = mountain_df[mountain_df.iloc[:, 0] == selected_province]
        mountain_list = matched_rows.iloc[:, 1].dropna().unique().tolist()

        # 상세주소 선택 여부
        if 'search_triggered' not in st.session_state:
            st.session_state['search_triggered'] = False

            # 상세주소 선택
        selected_detail = st.selectbox("상세주소 선택", mountain_list, index=None, placeholder="상세주소 선택")

        # 산을 재검색하기 위해 필요함/기존에 선택된 산
        if "prev_detail" not in st.session_state:
            st.session_state["prev_detail"] = None

        if st.session_state['prev_detail'] != selected_detail:
            st.session_state['search_triggered'] = False
            st.session_state['prev_detail'] = selected_detail

        if st.session_state['search_triggered'] == False:
            st.write('\n')
            if st.button("검색"):
                if selected_detail == '':
                    st.write('상세주소를 선택해주세요')
                st.session_state['search_triggered'] = True

            if st.session_state['search_triggered'] == True:
                st.write('')
                df = pd.read_excel('anthropods/개별산검색.xlsx')
                each_mountain = df[df.iloc[:, 2] == selected_detail]
                drop_cols = ['조사지번호', '시/도', '상세주소', '구/군']
                columns = [col for col in drop_cols if col in each_mountain.columns]
                each_mountain = each_mountain.drop(columns=columns)
                sort_columns = ['강', '목']
                each_mountain = each_mountain.sort_values(by=sort_columns).reset_index(drop=True)
                each_mountain.index = range(1, len(each_mountain) + 1)
                st.write(each_mountain)

    with tab3:
        st.subheader("⚠️ 유해종 리스트 및 질병 정보")

        # 엑셀 데이터 로드
        df_bug = load_harmful_species()
        # 절지동물 카테고리
        category_map = {
            "왕지네": ["왕지네"],
            "진드기": ["작은소참진드기", "털진드기"],
            "바퀴": ["독일바퀴"],
            "파리": ["집파리"],
            "벌": ["꿀벌", "장수말벌", "일본왕개미"]
        }

        # ✅ 생물 이름 list
        options = list(category_map.keys())
        selected_danger = st.radio("⚠️ 주의가 필요한 절지동물을 선택하세요:", options, horizontal=True)

        # ✅ 토글 - 사진 보기
        show_images = st.toggle("🔍 사진 보기", value=False)

        # ✅ 선택된 생물 그룹에 해당하는 row 출력
        bug_names = category_map[selected_danger]
        filtered = df_bug[df_bug.iloc[:, 0].isin(bug_names)]

        if show_images:
            num_cols = 3  # 한 줄에 몇 개 출력할지 (조정 가능)
            rows = (len(filtered) + num_cols - 1) // num_cols  # 줄 수 계산

            for row_idx in range(rows):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    data_idx = row_idx * num_cols + col_idx
                    if data_idx >= len(filtered):
                        continue
                    row = filtered.iloc[data_idx]
                    name = row[0]
                    source = row[1]
                    img_name = name + ".gif"
                    img_path = os.path.join("anthropods/images", img_name)

                    with cols[col_idx]:
                        st.markdown(
                            f"""
                                    <div style='text-align: left;'>
                                        <div style='font-size:14px; font-weight:600; margin-bottom:4px'>{name}</div>
                                    """,
                            unsafe_allow_html=True
                        )
                        img_data = load_encoded_image(img_path)
                        if img_data:
                            st.markdown(
                                f"""
                                        <img src='data:image/gif;base64,{img_data}' 
                                             style='height:180px; width:auto; display:block; object-fit:contain;'>
                                        <div style='font-size:11px; color:gray; margin-top:4px; white-space:pre-wrap;'>{source}</div>
                                        </div>
                                        """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning(f"이미지 없음: {img_name}")

        # ✅ 생물별 설명 출력 (이전 설명 그대로 유지 가능)
        img_folder = "anthropods/질병 사진"
        image_files = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png'))]
        st.write('---')
        if selected_danger == '왕지네':
            st.subheader('🦂 지네 독과 응급처치')
            st.write('■ **독 작용 기전**')
            st.write("지네강의 첫 번째 다리는 **독 발톱**으로 변형되어 먹이를 독으로 마비시킨 후 포획함.")
            st.write('\n')
            st.write('\n')
            st.write('■ **인체에 미치는 영향**')
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>대부분 해롭지 않지만, 일부 대형 지네는 위험할 수 있음.</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>또한 어린이, 벌 알러지를 가진 사람의 경우 위험.</div>",
                unsafe_allow_html=True
            )
            st.markdown('')
            # 어른의 경우, 물림 시 통증, 붓기, 오한, 발열, 근력 저하 등의 증상이 유발되나 치명적이지 않다. 하지만 어린이, 벌 알러지를 가진 사람의 경우 위험하다.
            # 특히 대형 지네류는 과민성 쇼크를 유발할 수 있다.
            # st.markdown('&nbsp;&nbsp;⚠ ️ 주요 증상', unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ국소 증상: 통증, 부기, 붉어짐 및 아나필락시스 같은 생명을 위협하는 반응</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ전신 증상: 심장, 신장, 신경계에 영향 주어 실신이나 흉통까지 유발할 수 있음.</div>",
                unsafe_allow_html=True
            )
            st.markdown('> ')
            st.write('\n')
            st.write('\n')
            st.write('■ **치료 방법**')
            for i in ['진통제', '스테로이드', '항히스타민제', '파상풍 예방주사']:
                st.markdown(
                    f"<div style='font-size:16px; font-weight:400;'>ㆍ{i}</div>",
                    unsafe_allow_html=True
                )
            st.write('\n')
            st.write('\n')
            st.write('■ **임상 사례 요약**')
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ물린 후 <strong>30분 내 심한 부종</strong>으로 손가락 움직임 제한</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ물린 부위에 <strong>붉은 줄무늬</strong> 발생, 통증 확산</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ<strong>1.5cm 간격</strong>으로 난 <strong>두 개의 이빨 자국</strong> 관찰</div>",
                unsafe_allow_html=True
            )
            st.write('\n')
            st.write('\n')

            col1, col2, col3 = st.columns([1, 2, 1])  # 비율 조절 (가운데 좀 더 넓게)

            with col2:
                img_path = os.path.join(img_folder, '지네.png')
                st.image(img_path, caption='출처: OpenAI ChatGPT 이미지 생성 도구 사용(AI가 생성한 가상 이미지입니다)',
                         width=300)  # 또는 height=300

            st.write('\n')
            st.write('\n')
            st.markdown(
                "<div style='font-size:12px; font-weight:400; color:gray;'>Sanaei-Zadeh, H. (2014). Centipede bite. European Review for Medical and Pharmacological Sciences, 18, 1106–1107</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div style='font-size:12px; font-weight:400;color:gray;'>Bush, S.P., King, B.O., Norris, R.L., & Stockwell, S.A.(2001).Centipede envenomation.Wilderness & Environmental Medicine, 12(2), 93–99. </div>",
                unsafe_allow_html=True
            )
        elif selected_danger == '진드기':

            st.subheader('🕷️ 진드기매개감염병')
            st.write('■ **감염 경로**')

            st.write('세균이나 바이러스에 감염된 진드기에 물려 발생하는 감염병')
            st.write('\n')
            st.write('\n')
            st.write('**■ 한국의 대표적인 진드기매개감염병**')
            acari_list = ['중증열성혈소판감소증후군(SFTS)', '쯔쯔가무시증', '라임병']
            selected_acari = st.radio(
                label="진드기매개감염병",
                options=acari_list,
                horizontal=True,
                label_visibility="collapsed"
            )
            st.write('---')
            if selected_acari == '중증열성혈소판감소증후군(SFTS)':
                st.write('**■ 중증열성혈소판감소증후군(SFTS)**')
                st.write('SFTS 바이러스에 **감염된 참진드기에 물려 감염**됨.')
                st.write('\n')
                st.write('\n')
                st.write('**■ 주의 시기**')
                st.write('4 ~ 11월')
                st.write('\n')
                st.write('\n')
                st.write('**■ 증상**')
                for i in ['고열', '소화기 증상', '의식저하', '혈소판 감소']:
                    st.markdown(
                        f"<div style='font-size:16px; font-weight:400;'>ㆍ{i}</div>",
                        unsafe_allow_html=True
                    )
                st.write('\n')
                st.write('\n')

                col1, col2, col3 = st.columns([1, 2, 1])  # 비율 조절 (가운데 좀 더 넓게)

                with col2:
                    img_path = os.path.join(img_folder, '중증열성혈소판감소증후군(SFTS).png')
                    st.image(img_path, width=400)  # 또는 height=300

            elif selected_acari == '쯔쯔가무시증':
                st.write('**■ 쯔쯔가무시증**')
                st.write('쯔쯔가무시균에 **감염된 털진드기 유충에 물려 감염**됨.')
                st.write('\n')
                st.write('\n')
                st.write('**■ 주의 시기**')
                st.write('연중(특히 10~11월에 집중)')
                st.write('\n')
                st.write('\n')
                st.write('**■ 증상**')
                for i in ['발열', '근육통', '오한', '발진', '검은 딱지(가피)']:
                    st.markdown(
                        f"<div style='font-size:16px; font-weight:400;'>ㆍ{i}</div>",
                        unsafe_allow_html=True
                    )
                st.write('\n')
                st.write('\n')

                col1, col2, col3 = st.columns([1, 2, 1])  # 비율 조절 (가운데 좀 더 넓게)

                with col2:
                    img_path = os.path.join(img_folder, '쯔쯔가무시증.png')
                    st.image(img_path, width=400)  # 또는 height=300

            elif selected_acari == '라임병':
                st.write('**■ 라임병**')
                st.write('보렐리아속균에 **감염된 참진드기에 물려 감염**됨.')
                st.write('\n')
                st.write('\n')
                st.write('**■ 주의 시기**')
                st.write('연중')
                st.write('\n')
                st.write('\n')
                st.write('**■ 증상**')
                for i in ['발열', '오한', '유주성 홍반(과녁 모양의 발진)']:
                    st.markdown(
                        f"<div style='font-size:16px; font-weight:400;'>ㆍ{i}</div>",
                        unsafe_allow_html=True
                    )

                st.write('\n')
                st.write('\n')

                col1, col2, col3 = st.columns([1, 2, 1])  # ?? 이거 그림 그리자
                caption = """UK Health Security Agency,
                Contains public sector information licensed under the Open Government Licence v3.0"""
                with col2:
                    img_path = os.path.join(img_folder, '라임병.png')
                    st.image(img_path, caption=caption, width=400)  # 또는 height=300

            st.write('\n')
            st.write('\n')
            st.write('**■ 예방 수칙**')

            items = [
                "야외활동 시 <span style='font-weight:700;'>살이 보이지 않는 옷</span> 착용",
                "<span style='font-weight:700;'>방석, 돗자리, 기피제</span> 적극 활용",
                "귀가 후 옷 전체를 털고 즉시 세탁",
                "<span style='font-weight:700;'>샤워 후 물린 자국 있는지 확인</span>"
            ]

            for text in items:
                st.markdown(
                    f"<div style='font-size:16px; font-weight:400;'>ㆍ{text}</div>",
                    unsafe_allow_html=True
                )

            st.write('\n')
            st.write('\n')
            st.write('**■ 대처 방법**')
            items = [
                "진드기를 <span style='font-weight:700;'>손으로 터뜨리거나 억지로 떼지 말 것</span>",
                "<span style='font-weight:700;'>보건소 또는 의료기관 방문</span> 권장",
                "진드기의 일부(입)가 피부에 남거나, 터지면 <span style='font-weight:700;'>감염 위험 증가</span>",
                "의료기관 방문이 어려운 경우<span style='font-weight:700;'>: 안전한 제거법</span>에 따라 떼어낸 뒤 <span style='font-weight:700;'>해당 부위 즉시 소독</span>"
            ]

            for text in items:
                st.markdown(
                    f"<div style='font-size:16px; font-weight:400;'>ㆍ{text}</div>",
                    unsafe_allow_html=True
                )

        elif selected_danger == '바퀴':
            st.subheader('**🪳 독일바퀴와 장살모넬라균**')

            st.write('**■ 독일바퀴**')
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ세계에서 가장 흔한 바퀴 종</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ무리를 지어 서식하는 <span style='font-weight:700;'>사회적 곤충</span></div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ오염된 물질을 섭취함으로써<span style='font-weight:700;'> 병원균에 감염</span></div>",
                unsafe_allow_html=True
            )
            st.write('\n')
            st.write('\n')
            st.write('**■ 먹이 섭취 방법**')
            items = ['동족의 배설물 섭취', '사체 섭취', '토사물 섭취']
            for text in items:
                st.markdown(
                    f"<div style='font-size:16px; font-weight:400;'>ㆍ{text}</div>",
                    unsafe_allow_html=True
                )
            st.write('→ 분변-경구 경로를 통한 **병원균의 수평 전파**')

            st.write('\n')
            st.write('\n')
            st.write('**■ 장살모넬라균(S.Typhimurium)**')
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ전 세계 설사 질환의 주요 원인균</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ<span style='font-weight:700;'>오염된 음식물, 물, 표면</span>을 통해 감염</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ독일바퀴의 <span style='font-weight:700;'>소화기간, 배설물</span>에서 자주 검출</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>→ 위생 관리는 단순한 해충 퇴치를 넘어 <span style='font-weight:700;'>감염 예방의 핵심</span></div>",
                unsafe_allow_html=True
            )

            st.write('\n')
            st.write('\n')
            st.write('**■ 증상**')
            items = ['발열', '복통', '구토', '설사']
            for text in items:
                st.markdown(
                    f"<div style='font-size:16px; font-weight:400;'>ㆍ{text}</div>",
                    unsafe_allow_html=True
                )

            st.write('\n')
            st.write('\n')
            items = [
                'Turner, M., Peta, V., & Pietri, J. E. (2022). *Salmonella Typhimurium and the German cockroach*. Research in Microbiology, 173(3), 103920.',
                'Tang, Q., Vargo, E. L., Ahmad, I., & Evans, T. A. (2024). *Origin and global spread of the German cockroach*. PNAS, 121(22), e2401185121.',
                '식품의약품안전처. (2025). *장출혈성 대장균 식중독 예방 요령* [PDF].',
                'Yamaguchi, T. et al. (2023). *Resistant E. coli and Salmonella from cockroaches*. Front. Microbiol., 14, 1138969.'
            ]
            for text in items:
                st.markdown(
                    f"<div style='font-size:12px; font-weight:400;'>{text}</div>",
                    unsafe_allow_html=True
                )


        elif selected_danger == '파리':
            st.subheader('**🪰 파리**')

            st.write('■ **파리 유충에 의한 감염**')
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ일부 <span style='font-weight:700;'>파리 종의 유충(구더기)는 </span>살아있는 <span style='font-weight:700;'>인간 조직에 침입</span>하여 감염 유발</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ이로 인해 <span style='font-weight:700;'>피부, 눈, 비강, 소화관 </span>등에서 <span style='font-weight:700;'>기생 증상 </span>발생</div>",
                unsafe_allow_html=True
            )
            st.write('\n')
            st.write('\n')
            st.write('■ **병원체 물리적 전파**')
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ<span style='font-weight:700;'>오물, 배설물, 사체 등 오염된 곳에 앉았다가 사람의 음식이나 상처 부위에 다시 접촉</span></div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:16px; font-weight:400;'>ㆍ세균, 바이러스, 기생충 등을 <span style='font-weight:700;'>물리적으로 운반</span></div>",
                unsafe_allow_html=True
            )
            st.write('\n')
            st.write('\n')

            items = [
                'Hazratian, T. et al. (2021). *Urogenital myiasis by Psychoda albipennis: A case report*. Iranian J. Parasitol., 16(1), 172–176. https://doi.org/10.18502/ijpa.v16i1.5807',
                'Khamesipour, F. et al. (2018). *Human pathogens carried by houseflies: A review*. BMC Public Health, 18, 1049. https://doi.org/10.1186/s12889-018-5934-3'
            ]
            for text in items:
                st.markdown(
                    f"<div style='font-size:12px; font-weight:400;'>{text}</div>",
                    unsafe_allow_html=True
                )
        elif selected_danger == '벌':
            st.subheader('🐝 벌')
            st.write("**꿀벌과**")
            st.markdown("""
            ㆍ **바늘 구조**: 바늘에 **갈고리**가 있어 **한 번 찌르면 빠지지 않음**  
            ㆍ **공격성**: 일반적으로 **공격성 낮음**, 위협 시 **방어 목적으로 공격**  
            ㆍ **결과**: 찌른 후 **벌은 죽음**
            """)
            st.write('\n')
            st.write('\n')
            st.write("**말벌과**")
            st.markdown("""
            ㆍ **바늘 구조**: **갈고리 없음** → **여러 번 찌르기 가능**  
            ㆍ **공격성**: **매우 높음**, 위협 상황이 아니어도 **선제 공격 가능**  
            ㆍ **결과**: 반복적 공격으로 **위험성 증가**
            """)
            st.write('\n')
            st.write('\n')
            st.write('**개미과**')
            st.markdown("""
            ㆍ **공격 방식**: **턱으로 피부 고정 후 반복적으로 찌름**  
            ㆍ **독성**: **알칼로이드 독성** → **농포, 알레르기 반응 유발**  
            ㆍ **특징**: 피부 자극 및 **전신 반응** 유발 가능
            """)

            st.markdown("> ⚠ ️ 이들 모두 **아나필락시스(전신 과민반응)**을 유발할 수 있으며,  \n> 특히 벌독에 민감한 사람은 **즉각적인 처치**가 필요",
                        unsafe_allow_html=True)

            st.write('\n')
            st.write('\n')

            st.markdown(
                "<div style='font-size:12px; font-weight:400; '>Zirngibl, G., & Burrows, H. L. (2012). Hymenoptera stings. Pediatrics in Review, 33(11), 534–535. https://doi.org/10.1542/pir.33-11-534</div>",
                unsafe_allow_html=True
            )