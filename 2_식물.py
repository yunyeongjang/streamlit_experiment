
# 식물
import os
import joblib
import json
import pandas as pd
import streamlit as st
import time
import base64

if "risk_predicted" not in st.session_state:
    st.session_state["risk_predicted"] = False

if "confirmed" not in st.session_state:
    st.session_state["confirmed"] = False

if 'unknown_list' not in st.session_state:
    st.session_state['unknown_list'] = False

if 'cols1' not in st.session_state:
    st.session_state['cols1'] = []

if 'cols2' not in st.session_state:
    st.session_state['cols2'] = []

st.header("🌿 꽃가루 알레르기와 식물 정보")
st.write("- 사용자의 의 **꽃가루 알레르기 위험도** 및 사용자가 선택한 등산로에서 조심해야 할 식물 리스트를 확인할 수 있습니다.")
st.write("- 해당 산의 식물 목록, 알레르기 유발 식물 안내")


# 사용자 입력 로딩 (all_list)
@st.cache_resource
def load_model(path):
    if os.path.exists(path):
        return joblib.load(path)


@st.cache_resource
def load_features(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)


@st.cache_data(show_spinner=False)
def load_encoded_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


# 사용자 입력값 session_state 기반으로 구성
all_list = {
    'user_name': st.session_state.get('saved_user_name', ''),
    'pollen_yesorno': st.session_state.get('saved_pollen_yesorno', ''),
    'general_allergens': st.session_state.get('saved_general_allergens', []),
    'pollen_tree': st.session_state.get('saved_pollen_tree', ''),
    'pollen_grass': st.session_state.get('saved_pollen_grass', ''),
    'pollen_weed': st.session_state.get('saved_pollen_weed', '')
}

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

tab1, tab2, tab3 = st.tabs(["🌲개인별 알러지 분석", "📍산림별 알러지 식물", "🪴전체 식물 도감"])

with tab1:
    if (all_list['user_name'] == ''
            or all_list['pollen_yesorno'] == ''
            or (all_list['pollen_yesorno'] == '있음' and all_list['general_allergens'] == [])
            or ('꽃가루' in all_list['general_allergens'] and (
                    all_list['pollen_tree'] == '' or all_list['pollen_grass'] == '' or all_list[
                'pollen_weed'] == ''))):
        st.write('사용자입력 페이지에서 입력을 완료한 뒤 이용해주세요.')

    else:
        pollens = ['pollen_grass', 'pollen_tree', 'pollen_weed']
        pollen_dic = {
            'pollen_grass': '풀 꽃가루',
            'pollen_tree': '나무 꽃가루',
            'pollen_weed': '잔디 꽃가루'
        }

        pollen_dic_rev = {v: k for k, v in pollen_dic.items()}
        pollen_grass = all_list['pollen_grass']
        pollen_tree = all_list['pollen_tree']
        pollen_weed = all_list['pollen_weed']
        allergens = all_list['general_allergens']
        if len(all_list['general_allergens']) > 0:
            if pollen_grass == '' and pollen_tree == '' and pollen_weed == '':
                pollen_grass = '없음'
                pollen_tree = '없음'
                pollen_weed = '없음'

        unknown = []
        for pollen in pollens:
            if all_list[pollen] == '모름':
                unknown.append(pollen_dic[pollen])
            if '꽃가루' not in all_list['general_allergens'] and len(all_list['general_allergens']) > 0:
                unknown.append(pollen_dic[pollen])
        st.session_state['unknown_list'] = unknown

        if (len(all_list['general_allergens']) > 0 and '꽃가루' not in all_list['general_allergens']) \
                or len(unknown) > 0:
            find = []
            for pollen in pollens:
                if all_list[pollen] == '모름':
                    find.append(pollen_dic[pollen])
            if len(find) == 0:
                for pollen in pollens:
                    find.append(pollen_dic[pollen])
            st.write(f"**{', '.join(find)}**의 교차 알레르기 분석 위험도를 확인하시겠습니까?")

            if len(all_list['general_allergens']) == 0:
                current_input_key = f"{all_list['user_name']}_{all_list['pollen_yesorno']}"
            elif '꽃가루' in all_list['general_allergens']:
                current_input_key = f"{all_list['user_name']}_{all_list['pollen_yesorno']}_{','.join(all_list['general_allergens'])}"
            elif len(all_list['general_allergens']) > 0 and '꽃가루' not in all_list['general_allergens']:
                current_input_key = f"{all_list['user_name']}_{all_list['pollen_yesorno']}_{all_list['pollen_grass']}_{all_list['pollen_tree']}_{all_list['pollen_weed']}_{','.join(all_list['general_allergens'])}"

            if 'last_input_key' not in st.session_state:
                st.session_state['last_input_key'] = current_input_key

            # 입력 변경되었으면 버튼 상태 초기화
            if st.session_state['last_input_key'] != current_input_key:
                st.session_state["predict_clicked"] = False
                st.session_state["risk_predicted"] = False
                st.session_state['last_input_key'] = current_input_key
                st.rerun()

            if 'predict_clicked' not in st.session_state:
                st.session_state['predict_clicked'] = False

            if 'risk_predicted' not in st.session_state:
                st.session_state['risk_predicted'] = False

            st.markdown("""
                <style>
                div.stButton > button {
                    padding: 10px 28px !important;
                    font-size: 14px !important;
                    height: 50px !important;
                    border-radius: 6px;
                }
                div.stButton > button p {
                    font-size: 14px !important;
                    margin: 0 !important;
                    font-weight: 500 !important;
                }
                </style>
            """, unsafe_allow_html=True)

            if not st.session_state["predict_clicked"]:
                st.session_state["risk_predicted"] = False  # 예측 실행 전이면 항상 False
                if st.button("예측 실행", key="predict_button"):
                    st.session_state["predict_clicked"] = True
                    st.rerun()

            # 3. 예측 실행
            elif not st.session_state["risk_predicted"]:

                def predict():
                    model1_dic, model2_dic = {}, {}
                    y_prob_dict1, y_prob_dict2 = {}, {}
                    X_input1, X_input2 = [], []
                    cols1, cols2 = [], []

                    for uk in unknown:
                        pollen = pollen_dic_rev[uk]
                        path2 = f"plants/models/model_2nd_{pollen_grass}{pollen_tree}{pollen_weed}_{pollen_dic[pollen]}.pkl"
                        ft2 = f"plants/models/feature_columns_2nd_{pollen_grass}{pollen_tree}{pollen_weed}.json"
                        model2 = load_model(path2)
                        model2_dic[pollen] = model2
                        cols2 = load_features(ft2)

                        # model에 포함되는 allergen 찾기
                        dataset_2_pollen = []
                        for allergen in all_list['general_allergens']:
                            if allergen in cols2:
                                dataset_2_pollen.append(allergen)
                        X_input2 = dataset_2_pollen

                        for A_pollen in pollens:
                            if all_list[A_pollen] == '있음':
                                X_input2.append(pollen_dic[A_pollen])

                        if len(X_input2) > 0:
                            X_input2_dict = {col: 1 if col in X_input2 else 0 for col in cols2}
                            X_input2_df = pd.DataFrame([X_input2_dict])
                            y_prob2 = model2.predict_proba(X_input2_df)[:, 1]
                            y_prob_dict2[pollen] = y_prob2[0]

                        if pollen != 'pollen_weed':
                            path1 = f"plants/models/model_1st_{pollen_grass}{pollen_tree}_{pollen_dic[pollen]}.pkl"
                            ft1 = f"plants/models/feature_columns_1st_{pollen_grass}{pollen_tree}.json"
                            model1 = load_model(path1)
                            model1_dic[pollen] = model1
                            cols1 = load_features(ft1)

                            dataset_1_pollen = []
                            for allergen in all_list['general_allergens']:
                                if allergen in cols1:
                                    dataset_1_pollen.append(allergen)
                            X_input1 = dataset_1_pollen
                            for B_pollen in pollens:
                                if all_list[B_pollen] == '있음':
                                    X_input1.append(pollen_dic[B_pollen])

                            if len(X_input1) > 0:
                                X_input1_dict = {col: 1 if col in X_input1 else 0 for col in cols1}
                                X_input1_df = pd.DataFrame([X_input1_dict])
                                y_prob1 = model1.predict_proba(X_input1_df)[:, 1]
                                y_prob_dict1[pollen] = y_prob1[0]

                    return y_prob_dict1, y_prob_dict2, X_input1, X_input2, cols1, cols2


                with st.spinner("모델 불러오기 및 예측 중입니다... ⏳"):

                    progress_bar = st.progress(0, text="예측 진행 중입니다...")
                    for p in range(101):
                        time.sleep(0.005)
                        progress_bar.progress(p, text=f"예측 진행 중입니다... {p}%")

                    y_prob_dict1, y_prob_dict2, X_input1, X_input2, cols1, cols2 = predict()
                    st.session_state['cols1'] = cols1
                    st.session_state['cols2'] = cols2
                    unknown = st.session_state.get('unknown_list', [])
                    final_prediction_dic = {}
                    th1_dic = {}
                    th2_dic = {}
                    th_dic = {}

                    if len(unknown) > 0:
                        for uk in unknown:
                            pollen = pollen_dic_rev[uk]
                            if pollen != 'pollen_weed':
                                threshold1 = pd.read_excel('plants/threshold1.xlsx')
                                th1_df = threshold1[
                                    (threshold1["pollen_grass"] == pollen_grass) &
                                    (threshold1["pollen_tree"] == pollen_tree) &
                                    (threshold1['allergen'] == pollen)
                                    ]
                                th1 = th1_df["threshold"].iloc[0]
                                th1_dic[pollen] = th1

                            threshold2 = pd.read_excel('plants/threshold2.xlsx')
                            th2_df = threshold2[
                                (threshold2["pollen_grass"] == pollen_grass) &
                                (threshold2["pollen_tree"] == pollen_tree) &
                                (threshold2["pollen_weed"] == pollen_weed) &
                                (threshold2['allergen'] == pollen)
                                ]

                            th2 = th2_df["threshold"].iloc[0]
                            th2_dic[pollen] = th2

                    list_grass_tree = []
                    count_grass_tree = 0
                    count_weed = 0

                    for uk in st.session_state.get('unknown_list', []):
                        pollen = pollen_dic_rev[uk]
                        if pollen != 'pollen_weed':
                            prob1 = y_prob_dict1.get(pollen)
                        else:
                            prob1 = None
                        prob2 = y_prob_dict2.get(pollen)

                        if prob1 is not None and prob2 is not None:
                            w1 = len(X_input1) * 165273
                            w2 = len(X_input2) * 8337
                            tot = w1 + w2
                            final = (prob1 * w1 + prob2 * w2) / tot
                            th = (th1_dic[pollen] * w1 + th2_dic[pollen] * w2) / tot
                            th_dic[pollen] = th

                        elif prob1 is not None:
                            final = prob1
                            th = th1_dic[pollen]

                        elif prob2 is not None:
                            final = prob2
                            th = th2_dic[pollen]


                        elif prob1 is None and prob2 is None:
                            final = None
                            th = None

                        final_prediction_dic[pollen] = final

                        st.session_state[f'threshold_{pollen}'] = th
                        st.session_state[f'ensemble_prob_{pollen}'] = final
                        st.session_state['risk_predicted'] = True

        if st.session_state["risk_predicted"]:
            st.write("")
            cols1 = st.session_state['cols1']
            cols2 = st.session_state['cols2']
            imojis = {'풀 꽃가루': '🌿',
                      '나무 꽃가루': '🌳',
                      '잔디 꽃가루': '🌾'}
            count = 0
            for uk in unknown:
                pollen = pollen_dic_rev[uk]

                if (f"ensemble_prob_{pollen}" in st.session_state \
                        and st.session_state[f'ensemble_prob_{pollen}'] is not None \
                        and st.session_state.get(f'threshold_{pollen}') is not None):
                    prob = st.session_state.get(f'ensemble_prob_{pollen}')
                    th = st.session_state.get(f'threshold_{pollen}')
                    st.write(f'**{imojis[uk]} {uk} 알레르기 예측**')
                    if prob >= th:  # 기본값 1로 하면 위험 판정 안 남
                        st.error(f"❗ {uk} 알레르기 위험! (예측 확률: {prob:.2%}, threshold: {th:.2%})")
                    else:
                        st.success(f"✅ {uk} 알레르기 가능성 낮음 (예측 확률: {prob:.2%}, threshold: {th:.2%})")
                else:

                    if pollen == 'pollen_weed':
                        if count == 0:
                            st.write('')
                            st.write('❌ **알레르기 환자 정보가 한정적이라, 알레르기 반응을 예측할 수 없는 상황입니다.**')
                            count += 1
                        st.markdown(f"""
                            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; background-color: #f9f9f9;">
                                <b>{uk}를 분석 위해 필요한 항원 리스트:</b><br>
                                {', '.join(cols2)}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        if count == 0:
                            st.write('**알레르기 환자 정보가 한정적이라, 알레르기 반응을 예측할 수 없는 상황입니다.**')
                            count += 1
                        st.markdown(f"""
                            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; background-color: #f9f9f9;">
                                <b>{uk}를 분석 위해 필요한 항원 리스트:</b><br>
                                {', '.join(cols1)}
                            </div>
                            """, unsafe_allow_html=True)

            st.write('\n')
            if st.button("초기화"):
                for key in ["prob", "risk_predicted", 'predict_clicked', 'allert_pollen']:
                    st.session_state.pop(key, None)
                st.rerun()

            if '꽃가루' not in all_list['general_allergens'] or len(unknown) > 0:
                st.write('---')
                st.markdown(
                    '**꽃가루 알레르기**에 대해 주의가 필요한 상황입니다. **알레르기 시 주의사항** 확인하시겠습니까?'
                )
                if st.button("확인", key="warning button"):
                    st.subheader("🌿 꽃가루 알레르기")

                    st.markdown("""
                    **1) 회피 방법**  
                    - 꽃가루가 많이 날리는 시간대인 오전 5시에서 10시 사이에는 활동 자제  
                    - 바람이 많이 부는 날에는 활동 자제
                    - 나무 꽃가루 알레르기의 경우 4-6월, 잡초와 풀 꽃가루의 경우 8-10월에 산림활동을 자제  

                    **2) 대처 방법**  
                    - 기침, 쌕쌕거림, 호흡곤란 시 즉시 활동 중단 및 휴식  
                    - 스프레이형 스테로이드제 또는 항히스타민제, 점안액 등 약품 사용  
                    - 중증 증상(호흡 곤란, 아나필락시스)시 119 구조 요청 및 응급실 이동
                    """)
        if (len(all_list['general_allergens']) > 0 and '꽃가루' not in all_list['general_allergens']) \
                or len(unknown) > 0:
            pass
        elif all_list['general_allergens'] == []:
            st.write('❌ **알레르기 환자 정보가 한정적이라, 알레르기 반응을 예측할 수 없는 상황입니다.**')
            cols1 = st.session_state['cols1']
            cols2 = st.session_state['cols2']
            st.write(cols2)
            cols = list(set(cols1) | set(cols2))

            st.markdown(f"""
                                            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 8px; background-color: #f9f9f9;">
                                                <b>알러지를 분석 위해 필요한 항원 리스트:</b><br>
                                                {', '.join(cols)}
                                            </div>
                                            """, unsafe_allow_html=True)
        else:
            st.write('다음 페이지로 넘어가서 다양한 정보를 확인해보세요')

with tab2:
    unknown = st.session_state['unknown_list']

    df = pd.read_excel('plants/산리스트.xlsx')
    mountain_list = df.iloc[:, 0].dropna().tolist()
    st.write('\n')
    st.write(f"어떤 산에 갈 것입니까?")
    selected_mountain = st.selectbox(
        label="가고자 하는 등산로를 선택하세요.",
        options=mountain_list,
        index=None,
        placeholder="산 이름을 선택하세요.",
        label_visibility='collapsed'
    )

    if selected_mountain:
        st.write("---")
        st.write(f"**{selected_mountain}**에서 조심해야 할 꽃가루 알레르기 유발 식물을 확인하시겠습니까?")
        col1, col2 = st.columns([5, 20])

        with col1:
            st.markdown(
                "<div style='font-size:14px; font-weight:400; margin-top:4px;'>알레르기 유발 식물 출처:</div>",
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                "<div style='font-size:14px; font-weight:400; margin-top:4px;'>"
                "<a href='https://doi.org/10.4168/aard.2015.3.4.239' target='_blank' style='text-decoration:none; color:inherit;'>"
                "Hong, C.-S. (2015). Pollen allergy plants in Korea. *Allergy, Asthma & Respiratory Disease*, 3(4), 239–254. https://doi.org/10.4168/aard.2015.3.4.239"
                "</a></div>",
                unsafe_allow_html=True
            )
            st.write('')

        st.markdown("""
                    <style>
                    div.stButton > button {
                        padding: 10px 28px !important;
                        font-size: 14px !important;
                        height: 60px !important;
                        border-radius: 6px;
                    }
                    div.stButton > button p {
                        font-size: 14px !important;
                        margin: 0 !important;
                        font-weight: 500 !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
        plant_list = []
        if st.button("확인", key="confirm_button"):
            st.session_state["confirmed"] = True
            st.session_state["selected_mountain"] = selected_mountain  # 선택된 산도 저장하면 안정적
            progress_bar = st.progress(0)
            status_text = st.empty()

            # [0~70%] 로딩 효과용 (아주 천천히 올라감)
            for i in range(71):
                progress_bar.progress(i)
                time.sleep(0.01)

            # 실제 데이터 처리
            df = pd.read_csv('plants/식물분포지역1.csv')
            plant_list = [row[3] for idx, row in df.iterrows() if row[2] == selected_mountain]

            df_tree = pd.read_excel("plants/tree_pollen.xlsx", header=None)
            tree_pollen = df_tree[0].dropna().tolist()
            tree_pollen_per_forest = [t for t in tree_pollen if t in plant_list]
            tree_img_dir = "plants/images/tree_all_images(gif)"
            tree_img_leaf_dir = "plants/images/tree_leaf_images(gif)"

            df_grass = pd.read_excel("plants/grass_pollen.xlsx", header=None)
            grass_pollen = df_grass[0].dropna().tolist()
            grass_pollen_per_forest = [g for g in grass_pollen if g in plant_list]
            grass_img_dir = "plants/images/grass_images(gif)"

            df_weed = pd.read_excel("plants/weed_pollen.xlsx", header=None)
            weed_pollen = df_weed[0].dropna().tolist()
            weed_pollen_per_forest = [w for w in weed_pollen if w in plant_list]
            weed_img_dir = "plants/images/weed_images(gif)"

            # 📦 [70~100%] 실제 처리 부분
            for i in range(71, 101):
                progress_bar.progress(i)
                time.sleep(0.05)

            status_text.text("✅ 데이터 분석 완료!")
            st.success("조심해야 할 식물 정보가 완성되었습니다.")

            st.write('\n')
            st.write('---')

            # 이미지 스타일: 둥근 모서리 제거
            st.markdown("""
                <style>
                img {
                    border-radius: 0px !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # 🌾 풀
            st.markdown(
                f"<div style='font-size:22px; font-weight:600;'>🌾 {selected_mountain}에서 조심해야 할 풀</div>",
                unsafe_allow_html=True
            )
            st.write('\n')

            # 풀
            for i in range(0, len(grass_pollen_per_forest), 2):
                cols = st.columns(2)
                # 첫 번째
                with cols[0]:
                    name = grass_pollen_per_forest[i]
                    st.markdown(f"**{name}**")
                    img_path = os.path.join(grass_img_dir, f"{name}.gif")
                    encoded = load_encoded_image(img_path)
                    if encoded:
                        st.markdown(
                            f"""
                            <img src="data:image/gif;base64,{encoded}" 
                                 style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                            """,
                            unsafe_allow_html=True
                        )
                        info_row = df_grass[df_grass.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 1]
                        st.markdown(
                            f"<div style='font-size:15px; font-weight:400;margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.success(f"이미지 없음: {name}")
                # 두 번째 (홀수일 경우 생략)
                if i + 1 < len(grass_pollen_per_forest):
                    with cols[1]:
                        name = grass_pollen_per_forest[i + 1]
                        st.markdown(f"**{name}**")
                        img_path = os.path.join(grass_img_dir, f"{name}.gif")
                        encoded = load_encoded_image(img_path)
                        if encoded:
                            st.markdown(
                                f"""
                                <img src="data:image/gif;base64,{encoded}" 
                                     style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                                """,
                                unsafe_allow_html=True
                            )
                            info_row = df_grass[df_grass.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                            description = info_row.iloc[0, 1]
                            st.markdown(
                                f"<div style='font-size:15px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.success(f"이미지 없음: {name}")

            # 🌳 나무 - 전체 + 이파리
            st.write('---')
            st.markdown(
                f"<div style='font-size:22px; font-weight:600;'>🌳 {selected_mountain}에서 조심해야 할 나무</div>",
                unsafe_allow_html=True
            )
            st.write('\n')

            # 나무 이미지 출력 (전체, 이파리 사진을 함께 보여주는 형태)
            for name in tree_pollen_per_forest:
                st.markdown(f"**{name}**")
                cols = st.columns(2)
                with cols[0]:
                    img_path = os.path.join(tree_img_dir, f"{name}.gif")
                    encoded = load_encoded_image(img_path)
                    if encoded:
                        st.markdown(
                            f"""
                            <img src="data:image/gif;base64,{encoded}" 
                                 style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                            """,
                            unsafe_allow_html=True
                        )
                        info_row = df_tree[
                            df_tree.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 2]
                        st.markdown(
                            f"<div style='font-size:15px; font-weight:400;margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )

                    else:
                        st.success(f"이미지 없음: {name}")

                with cols[1]:
                    leaf_path = os.path.join(tree_img_leaf_dir, f"{name}.gif")
                    leaf_encoded = load_encoded_image(leaf_path)
                    if leaf_encoded:
                        st.markdown(
                            f"""
                            <img src="data:image/gif;base64,{leaf_encoded}" 
                                 style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                            """,
                            unsafe_allow_html=True
                        )
                        info_row = df_tree[
                            df_tree.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 5]
                        st.markdown(
                            f"<div style='font-size:15px; font-weight:400;margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.success(f"잎 이미지 없음: {name}")

            # 잔디
            st.write('---')
            st.markdown(
                f"<div style='font-size:22px; font-weight:600;'>🌾 {selected_mountain}에서 조심해야 할 잔디</div>",
                unsafe_allow_html=True
            )
            st.write('\n')

            # 풀 이미지 2개씩 나열
            for i in range(0, len(weed_pollen_per_forest), 2):
                cols = st.columns(2)
                # 첫 번째
                with cols[0]:
                    name = weed_pollen_per_forest[i]
                    st.markdown(f"**{name}**")
                    img_path = os.path.join(weed_img_dir, f"{name}.gif")
                    encoded = load_encoded_image(img_path)
                    if encoded:
                        st.markdown(
                            f"""
                            <img src="data:image/gif;base64,{encoded}" 
                                 style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                            """,
                            unsafe_allow_html=True
                        )
                        info_row = df_weed[
                            df_weed.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 1]
                        st.markdown(
                            f"<div style='font-size:15px; font-weight:400;margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.success(f"이미지 없음: {name}")
                # 두 번째 (홀수일 경우 생략)
                if i + 1 < len(weed_pollen_per_forest):
                    with cols[1]:
                        name = weed_pollen_per_forest[i + 1]
                        st.markdown(f"**{name}**")
                        img_path = os.path.join(weed_img_dir, f"{name}.gif")
                        encoded = load_encoded_image(img_path)
                        if encoded:
                            st.markdown(
                                f"""
                                <img src="data:image/gif;base64,{encoded}" 
                                     style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                                """,
                                unsafe_allow_html=True
                            )
                            info_row = df_weed[
                                df_weed.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                            description = info_row.iloc[0, 1]
                            st.markdown(
                                f"<div style='font-size:15px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.success(f"이미지 없음: {name}")
with tab3:
    st.header("🌿 꽃가루 알러지와 식물 정보")
    st.write("- 알러지를 유발하는 모든 식물을 알려드립니다.")
    col1, col2 = st.columns([5, 20])

    with col1:
        st.markdown(
            "<div style='font-size:14px; font-weight:400; margin-top:4px;'>알러지 유발 식물 출처:</div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            "<div style='font-size:14px; font-weight:400; margin-top:4px;'>"
            "<a href='https://doi.org/10.4168/aard.2015.3.4.239' target='_blank' style='text-decoration:none; color:inherit;'>"
            "Hong, C.-S. (2015). Pollen allergy plants in Korea. *Allergy, Asthma & Respiratory Disease*, 3(4), 239–254. https://doi.org/10.4168/aard.2015.3.4.239"
            "</a></div>",
            unsafe_allow_html=True
        )

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

    tab1, tab2, tab3 = st.tabs(["🌿 풀 꽃가루", "🌳 나무 꽃가루", "🌾️ 잔디 꽃가루"])

    df_tree = pd.read_excel("plants/tree_pollen.xlsx", header=None)
    df_tree = df_tree.iloc[1:]
    tree_pollen = df_tree[0].dropna().tolist()
    tree_img_dir = "plants/images/tree_all_images(gif)"
    tree_img_leaf_dir = "plants/images/tree_leaf_images(gif)"

    df_grass = pd.read_excel("plants/grass_pollen.xlsx", header=None)
    grass_pollen = df_grass[0].dropna().tolist()
    grass_img_dir = "plants/images/grass_images(gif)"

    df_weed = pd.read_excel("plants/weed_pollen.xlsx", header=None)
    weed_pollen = df_weed[0].dropna().tolist()
    weed_img_dir = "plants/images/weed_images(gif)"

    with tab1:
        for i in range(0, len(grass_pollen), 2):
            cols = st.columns(2)
            # 첫 번째
            with cols[0]:
                name = grass_pollen[i]
                st.markdown(f"**{name}**")
                img_path = os.path.join(grass_img_dir, f"{name}.gif")
                encoded = load_encoded_image(img_path)
                if encoded:
                    st.markdown(
                        f"""
                        <img src="data:image/gif;base64,{encoded}" 
                             style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                        """,
                        unsafe_allow_html=True
                    )
                    print_cols = st.columns([1.2, 10, 0.7])

                    with print_cols[0]:
                        st.write("")

                    with print_cols[1]:
                        info_row = df_grass[
                            df_grass.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 1]
                        st.markdown(
                            f"<div style='color:gray; font-size:12px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )

                    with print_cols[2]:
                        st.write("")
                else:
                    st.success(f"이미지 없음: {name}")
            # 두 번째 (홀수일 경우 생략)
            if i + 1 < len(grass_pollen):
                with cols[1]:
                    name = grass_pollen[i + 1]
                    st.markdown(f"**{name}**")
                    img_path = os.path.join(grass_img_dir, f"{name}.gif")
                    encoded = load_encoded_image(img_path)
                    if encoded:
                        st.markdown(
                            f"""
                            <img src="data:image/gif;base64,{encoded}" 
                                 style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                            """,
                            unsafe_allow_html=True
                        )
                        print_cols = st.columns([1.2, 10, 0.7])

                        with print_cols[0]:
                            st.write("")

                        with print_cols[1]:
                            info_row = df_grass[
                                df_grass.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                            description = info_row.iloc[0, 1]
                            st.markdown(
                                f"<div style='color:gray; font-size:12px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                                unsafe_allow_html=True
                            )

                        with print_cols[2]:
                            st.write("")
                    else:
                        st.success(f"이미지 없음: {name}")

        # 🌳 나무 - 전체 + 이파리
        st.write('---')
        st.write('\n')

    with tab2:
        # 나무 이미지 출력 (전체, 이파리 사진을 함께 보여주는 형태)
        for name in tree_pollen:
            st.markdown(f"**{name}**")
            cols = st.columns(2)
            with cols[0]:
                img_path = os.path.join(tree_img_dir, f"{name}.gif")
                encoded = load_encoded_image(img_path)
                if encoded:
                    st.markdown(
                        f"""
                        <img src="data:image/gif;base64,{encoded}" 
                             style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                        """,
                        unsafe_allow_html=True
                    )
                    print_cols = st.columns([1.2, 10, 0.7])

                    with print_cols[0]:
                        st.write("")

                    with print_cols[1]:
                        info_row = df_tree[
                            df_tree.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 2]
                        st.markdown(
                            f"<div style='color:gray; font-size:12px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )

                    with print_cols[2]:
                        st.write("")

                else:
                    st.success(f"이미지 없음: {name}")

            with cols[1]:
                leaf_path = os.path.join(tree_img_leaf_dir, f"{name}.gif")
                leaf_encoded = load_encoded_image(leaf_path)
                if leaf_encoded:
                    st.markdown(
                        f"""
                        <img src="data:image/gif;base64,{leaf_encoded}" 
                             style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                        """,
                        unsafe_allow_html=True
                    )
                    print_cols = st.columns([1.2, 10, 0.7])

                    with print_cols[0]:
                        st.write("")

                    with print_cols[1]:
                        info_row = df_tree[
                            df_tree.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 5]
                        st.markdown(
                            f"<div style='color:gray; font-size:12px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )

                    with print_cols[2]:
                        st.write("")
                else:
                    st.success(f"잎 이미지 없음: {name}")
    with tab3:
        # 잔디

        # 풀 이미지 2개씩 나열
        for i in range(0, len(weed_pollen), 2):
            cols = st.columns(2)
            # 첫 번째
            with cols[0]:
                name = weed_pollen[i]
                st.markdown(f"**{name}**")
                img_path = os.path.join(weed_img_dir, f"{name}.gif")
                encoded = load_encoded_image(img_path)
                if encoded:
                    st.markdown(
                        f"""
                        <img src="data:image/gif;base64,{encoded}" 
                             style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                        """,
                        unsafe_allow_html=True
                    )
                    print_cols = st.columns([1.2, 10, 0.7])

                    with print_cols[0]:
                        st.write("")

                    with print_cols[1]:
                        info_row = df_weed[
                            df_weed.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                        description = info_row.iloc[0, 1]
                        st.markdown(
                            f"<div style='color:gray; font-size:12px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                            unsafe_allow_html=True
                        )

                    with print_cols[2]:
                        st.write("")
                else:
                    st.success(f"이미지 없음: {name}")
            # 두 번째 (홀수일 경우 생략)
            if i + 1 < len(weed_pollen):
                with cols[1]:
                    name = weed_pollen[i + 1]
                    st.markdown(f"**{name}**")
                    img_path = os.path.join(weed_img_dir, f"{name}.gif")
                    encoded = load_encoded_image(img_path)
                    if encoded:
                        st.markdown(
                            f"""
                            <img src="data:image/gif;base64,{encoded}" 
                                 style="height:200px; object-fit:cover; display:block; margin: 0 auto 10px auto;">
                            """,
                            unsafe_allow_html=True
                        )
                        print_cols = st.columns([1.2, 10, 0.7])

                        with print_cols[0]:
                            st.write("")

                        with print_cols[1]:
                            info_row = df_weed[
                                df_weed.iloc[:, 0] == name]  # 1열(name) 값이 name과 같은 행 선택
                            description = info_row.iloc[0, 1]
                            st.markdown(
                                f"<div style='color:gray; font-size:12px; font-weight:400; margin-bottom:15px;'>{description}</div>",
                                unsafe_allow_html=True
                            )

                        with print_cols[2]:
                            st.write("")



                    else:
                        st.success(f"이미지 없음: {name}")
