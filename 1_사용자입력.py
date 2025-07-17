# 사용자입력
import streamlit as st
import pandas as pd
import os

# 처음 들어갔을 때 초기화하기
st.header("✅ 사용자 정보 입력")
st.write('- 사용자 정보를 입력하면, 맞춤형 안내가 제공됩니다.')
st.write('- 사용자 정보를 재입력할 경우, 초기화를 해주세요')

# 0) 앱이 처음 실행될 때 파일 만들기
all_list = {'user_name': "",
            'pollen_yesorno': '',
            'general_allergens': [],
            'pollen_tree': "",
            'pollen_grass': "",
            'pollen_weed': "",
            'check_pollen': ''}

if "re_check_pollen" not in st.session_state:
    st.session_state["re_check_pollen"] = 0


# 1) 이름 입력
def save_user_name():
    with open("txt/user_name.txt", "w", encoding="utf-8") as f:
        f.write(st.session_state["user_name"])


for i in all_list:
    if not os.path.exists(f"txt/{i}.txt"):
        with open(f"txt/{i}.txt", "w", encoding="utf-8") as f:
            f.truncate(0)

if os.path.exists(f"txt/check.txt"):
    with open(f"txt/check.txt", "r", encoding="utf-8") as f:
        check = f.read().strip()

if check == '':

    st.write('---')
    st.write('사용자의 이름을 입력하세요:')
    user_name = st.text_input(
        "사용자의 이름을 입력하세요:",
        key="user_name",
        label_visibility='collapsed',
        on_change=save_user_name)

    if user_name:
        st.markdown(f"{user_name}님, 환영합니다! 😄")

        st.write('---')
        st.write("알러지를 가지고 있으신가요?")


        def save_pollen_yesorno():
            with open("txt/pollen_yesorno.txt", "w", encoding="utf-8") as f:
                f.write(st.session_state["pollen_yesorno"])


        pollen_yesorno = st.radio(
            " ",
            ["있음", "없음"],
            index=None,
            key='pollen_yesorno',
            label_visibility="collapsed",
            on_change=save_pollen_yesorno
        )

        # 2-1) 알러지 여부 조사
        if pollen_yesorno == '있음':
            st.write('---')
            df = pd.read_excel('plants/알러지리스트.xlsx')
            allergen_list = df.iloc[:, 0].dropna().tolist()
            allergen_list.sort()


            def save_general_allergens():
                with open("txt/general_allergens.txt", "w", encoding="utf-8") as f:
                    f.write(",".join(st.session_state["general_allergens"]))


            st.write('해당하는 알레르기를 모두 선택하세요.')
            general_allergens = st.multiselect(
                label="해당하는 알레르기를 모두 선택하세요.",
                options=allergen_list,
                key="general_allergens",
                label_visibility='collapsed',
                on_change=save_general_allergens
            )


            # 3) 알러지 중 꽃가루가 있다면
            def save_pollen_tree():
                if st.session_state.get("pollen_tree"):
                    with open("txt/pollen_tree.txt", "w", encoding="utf-8") as f:
                        f.write(st.session_state["pollen_tree"])


            def save_pollen_grass():
                if st.session_state.get("pollen_grass"):
                    with open("txt/pollen_grass.txt", "w", encoding="utf-8") as f:
                        f.write(st.session_state["pollen_grass"])


            def save_pollen_weed():
                if st.session_state.get("pollen_weed"):
                    with open("txt/pollen_weed.txt", "w", encoding="utf-8") as f:
                        f.write(st.session_state["pollen_weed"])


            if '꽃가루' in st.session_state.get("general_allergens", []):
                st.write('---')
                st.markdown(
                    "<div style='font-size:20px; font-weight:600; margin-bottom:20px;'>꽃가루 알러지 상세 선택</div>",
                    unsafe_allow_html=True
                )

                pollen_grass = st.radio("① 풀 꽃가루 알러지", ["있음", "없음", '모름'], index=None, key='pollen_grass',
                                        on_change=save_pollen_grass)
                if pollen_grass is not None:
                    with open("txt/pollen_grass.txt", "w", encoding="utf-8") as f:
                        f.write(pollen_grass)
                pollen_tree = st.radio("② 나무 꽃가루 알러지", ["있음", "없음", '모름'], index=None, key='pollen_tree',
                                       on_change=save_pollen_tree)
                if pollen_tree is not None:
                    with open("txt/pollen_tree.txt", "w", encoding="utf-8") as f:
                        f.write(pollen_tree)
                pollen_weed = st.radio("③ 잡초 꽃가루 알러지", ["있음", "없음", '모름'], index=None, key='pollen_weed',
                                       on_change=save_pollen_weed)
                if pollen_weed is not None:
                    with open("txt/pollen_weed.txt", "w", encoding="utf-8") as f:
                        f.write(pollen_weed)

                if pollen_tree and pollen_grass and pollen_weed:
                    with open("txt/check_pollen.txt", "r", encoding="utf-8") as f:
                        all_list['check_pollen'] = f.read().strip()

                    if pollen_tree == '없음' and pollen_grass == '없음' and pollen_weed == '없음':
                        st.markdown(
                            "<div style='font-size:20px; font-weight:600; margin-bottom:20px;'>입력 확인</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown('''
                                                            <div style='font-size:16px; font-weight:400; line-height:0.8'>

                                                            꽃가루 알러지가 있다고 선택하셨지만,<br>  
                                                            세부 항목인 <b>풀 / 나무 / 잔디</b> 알러지가 모두 <b>없음</b>으로 선택되었습니다.<br>  
                                                            이 경우, 나의 알러지 리스트에서 꽃가루 알러지 항목을 제거할 수 있습니다.<br><br>

                                                            정말 꽃가루 항목을 삭제하시겠습니까?
                                                            </div>
                                                            ''', unsafe_allow_html=True)


                        def save_check_pollen():
                            with open("txt/check_pollen.txt", "w", encoding="utf-8") as f:
                                f.write(st.session_state["check_pollen"])


                        check_pollen = st.radio("삭제",
                                                ["예", "아니오"],
                                                index=None,
                                                key='check_pollen',
                                                label_visibility='collapsed',
                                                on_change=save_check_pollen)

                        for i in ['pollen_tree', 'pollen_grass', 'pollen_weed']:
                            if os.path.exists(f"txt/{i}.txt"):
                                with open(f"txt/{i}.txt", "r", encoding="utf-8") as f:
                                    all_list[i] = f.read().strip()

                        if check_pollen == '예':
                            if '꽃가루' in st.session_state.general_allergens:
                                st.session_state.general_allergens.remove('꽃가루')
                                with open("txt/general_allergens.txt", "w", encoding="utf-8") as f:
                                    f.write(",".join(st.session_state["general_allergens"]))
                            st.session_state['re_check_pollen'] = 1
                            st.rerun()

                        elif check_pollen and all_list['pollen_tree'] == '없음' and all_list['pollen_grass'] == '없음' and \
                                all_list['pollen_weed'] == '없음':
                            for i in ['pollen_tree', 'pollen_grass', 'pollen_weed']:
                                with open(f"txt/{i}.txt", "w", encoding="utf-8") as f:
                                    f.write('')
                            st.write('-> 위 꽃가루 알러지 상세 선택을 수정해주세요.')
                            st.session_state['re_check_pollen'] = 2
                            st.rerun()

                    elif all_list['check_pollen'] == '아니오' and st.session_state['re_check_pollen'] == 2:
                        st.markdown(
                            "<div style='font-size:20px; font-weight:600; color:gray; margin-bottom:20px;'>입력 확인</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown('''
                                        <div style='color:gray; font-size:16px; font-weight:400; line-height:0.8'>

                                        꽃가루 알러지가 있다고 선택하셨지만,<br>  
                                        세부 항목인 <b>풀 / 나무 / 잔디</b> 알러지가 모두 <b>없음</b>으로 선택되었습니다.<br>  
                                        이 경우, 나의 알러지 리스트에서 꽃가루 알러지 항목을 제거할 수 있습니다.<br><br>

                                        정말 꽃가루 항목을 삭제하시겠습니까?
                                        </div>
                                        ''', unsafe_allow_html=True)

                        check_pollen = st.radio("삭제",
                                                ["예", "아니오"],
                                                index=1,
                                                key='check_pollen',
                                                label_visibility='collapsed',
                                                disabled=True
                                                )

            else:
                if os.path.exists("txt/check_pollen.txt"):
                    with open("txt/check_pollen.txt", "r", encoding="utf-8") as f:
                        all_list['check_pollen'] = f.read().strip()

                if st.session_state['re_check_pollen'] == 1 and all_list['check_pollen'] == '예':
                    st.write('---')
                    st.markdown(
                        "<div style='font-size:20px; font-weight:600; color:gray; margin-bottom:20px;'>꽃가루 알러지 상세 선택</div>",
                        unsafe_allow_html=True
                    )

                    st.radio("① 풀 꽃가루 알러지", ["있음", "없음", '모름'], index=1, key='pollen_grass', disabled=True)
                    pollen_tree = st.radio("② 나무 꽃가루 알러지", ["있음", "없음", '모름'], index=1, key='pollen_tree',
                                           disabled=True)
                    pollen_weed = st.radio("③ 잡초 꽃가루 알러지", ["있음", "없음", '모름'], index=1, key='pollen_weed',
                                           disabled=True)

                    st.write('---')

                    st.markdown(
                        "<div style='font-size:20px; font-weight:600; color:gray; margin-bottom:20px;'>입력 확인</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown('''
                    <div style='color:gray; font-size:16px; font-weight:400; line-height:0.8'>

                    꽃가루 알러지가 있다고 선택하셨지만,<br>  
                    세부 항목인 <b>풀 / 나무 / 잔디</b> 알러지가 모두 <b>없음</b>으로 선택되었습니다.<br>  
                    이 경우, 나의 알러지 리스트에서 꽃가루 알러지 항목을 제거할 수 있습니다.<br><br>

                    정말 꽃가루 항목을 삭제하시겠습니까?
                    </div>
                    ''', unsafe_allow_html=True)

                    check_pollen = st.radio("삭제",
                                            ["예", "아니오"],
                                            index=0,
                                            key='check_pollen',
                                            label_visibility='collapsed',
                                            disabled=True
                                            )

                    st.markdown(
                        f"<div style='font-size:16px; font-weight:400; color:gray;'>→ {user_name}의 알러지 리스트에서 꽃가루가 삭제되었습니다.</div>",
                        unsafe_allow_html=True
                    )

    st.write('---')
    if st.button('저장'):
        if user_name != '':
            if pollen_yesorno == '없음':
                st.markdown("모든 입력이 완료되었습니다, 다음 페이지로 넘어가 분석 결과를 확인해보세요!")
                #입력변경시 초기화
                general_allergens = []
                pollen_tree = ''
                pollen_grass = ''
                pollen_weed = ''

                with open("txt/general_allergens.txt", "w", encoding="utf-8") as f:
                    f.write("")

                for key in ['pollen_tree', 'pollen_grass', 'pollen_weed']:
                    with open(f"txt/{key}.txt", "w", encoding="utf-8") as f:
                        f.write("")
                #재입력 방지
                if os.path.exists(f"txt/check.txt"):
                    with open(f"txt/check.txt", "w", encoding="utf-8") as f:
                        f.write('반복')
                    with open(f"txt/rerun.txt", "w", encoding="utf-8") as f:
                        f.write("")  # ??실험
                        st.rerun()
            elif pollen_yesorno == '있음':
                if general_allergens == []:
                    st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')
                else:
                    if '꽃가루' not in general_allergens:
                        st.markdown("모든 입력이 완료되었습니다, 다음 페이지로 넘어가 분석 결과를 확인해보세요!")
                        #입력변경시 초기화
                        for key in ['pollen_tree', 'pollen_grass', 'pollen_weed']:
                            with open(f"txt/{key}.txt", "w", encoding="utf-8") as f:
                                f.write("")
                            exec(f"{key} = ''")
                        #재입력방지
                        if os.path.exists(f"txt/check.txt"):
                            with open(f"txt/check.txt", "w", encoding="utf-8") as f:
                                f.write('반복')
                                st.rerun()
                    elif '꽃가루' in general_allergens:
                        if pollen_tree != '' and pollen_grass != '' and pollen_weed != '':
                            st.markdown("모든 입력이 완료되었습니다, 다음 페이지로 넘어가 분석 결과를 확인해보세요!")
                            if os.path.exists(f"txt/check.txt"):
                                with open(f"txt/check.txt", "w", encoding="utf-8") as f:
                                    f.write('반복')
                                    st.rerun()
                        else:
                            st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')
            else:
                st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')
        else:
            st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')

elif check == '반복':  # ?? 여기부터 수정하면 됨
    st.write('\n')
    #초기화
    if st.button('초기화'):
        with open(f"txt/check.txt", "w", encoding="utf-8") as f:
            f.write("")
        with open(f"txt/rerun.txt", "w", encoding="utf-8") as f:
            f.write("rerun")
            st.rerun()

    for i in all_list:
        if os.path.exists(f"txt/{i}.txt"):
            with open(f"txt/{i}.txt", "r", encoding="utf-8") as f:
                all_list[i] = f.read().strip()

    st.write('---')
    st.markdown(
        "<div style='font-size:15px; font-weight:500; color:gray; margin-bottom:15px;'>사용자의 이름을 입력하세요:</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size:15px; font-weight:500; color:gray; margin-bottom:15px;'>{all_list['user_name']}님, 환영합니다! 😄</div>",
        unsafe_allow_html=True
    )

    st.write('---')
    st.markdown(
        "<div style='font-size:15px; font-weight:600; color:gray; margin-bottom:15px;'>알러지를 가지고 있으신가요?</div>",
        unsafe_allow_html=True
    )
    if all_list['pollen_yesorno'] == '있음':
        pol = 0
    elif all_list['pollen_yesorno'] == '없음':
        pol = 1
    pollen_yesorno = st.radio(
        " ",
        ["있음", "없음"],
        index=pol,
        label_visibility="collapsed",
        disabled=True
    )

    # 2-1) 알러지 여부 조사
    if all_list['pollen_yesorno'] == '있음':
        st.write('---')
        df = pd.read_excel('plants/알러지리스트.xlsx')

        st.markdown(
            "<div style='font-size:15px; font-weight:600; color:gray; margin-bottom:15px;'>해당하는 알레르기를 모두 선택하세요.</div>",
            unsafe_allow_html=True
        )
        words = all_list['general_allergens'].split(',')  # 콤마 기준으로 나누기
        words = [w.strip() for w in words if w.strip()]
        for word in words:
            st.markdown(
                f"<div style='font-size:15px; font-weight:400; color:gray; line-height:2;'>- {word}</div>",
                unsafe_allow_html=True
            )

        if '꽃가루' in all_list['general_allergens']:
            st.write('---')
            st.markdown(
                "<div style='font-size:20px; font-weight:600; color:gray; margin-bottom:20px;'>꽃가루 알러지 상세 선택</div>",
                unsafe_allow_html=True
            )

            for i in ['pollen_grass', 'pollen_tree', 'pollen_weed']:
                if all_list[i] == '있음':
                    allergy = 0
                elif all_list[i] == '없음':
                    allergy = 1
                elif all_list[i] == '모름':
                    allergy = 2

            st.radio("① 풀 꽃가루 알러지", ["있음", "없음", '모름'], index=allergy, disabled=True)
            st.radio("② 나무 꽃가루 알러지", ["있음", "없음", '모름'], index=allergy, disabled=True)
            st.radio("③ 잡초 꽃가루 알러지", ["있음", "없음", '모름'], index=allergy, disabled=True)

        st.markdown('---')
        st.markdown("<div style='color: gray; margin-bottom: 15px;'>모든 입력이 완료되었습니다,</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: gray;'>다른 페이지로 넘어가 분석 결과를 확인해보세요!</div>", unsafe_allow_html=True)
        # ✅ 여기에 추가하세요
