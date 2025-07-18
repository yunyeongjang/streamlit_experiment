# 사용자입력
import streamlit as st
import pandas as pd

# 0) session_state 초기값 준비
default_state = {
    'user_name': "",
    'pollen_yesorno': '',
    'general_allergens': [],
    'pollen_tree': "",
    'pollen_grass': "",
    'pollen_weed': "",
    'check_pollen': '',
    're_check_pollen': 0,
    'check': '',
    'rerun': ''
}

for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.header("✅ 사용자 정보 입력")
st.write('- 사용자 정보를 입력하면, 맞춤형 안내가 제공됩니다.')
st.write('- 사용자 정보를 재입력할 경우, 초기화를 해주세요')

if st.session_state['check'] == '':
    st.write('---')
    st.write('사용자의 이름을 입력하세요:')
    st.text_input(
        "사용자의 이름을 입력하세요:",
        key="user_name",
        label_visibility='collapsed'
    )

    if st.session_state['user_name']:
        st.markdown(f"{st.session_state['user_name']}님, 환영합니다! 😄")

        st.write('---')
        st.write("알러지를 가지고 있으신가요?")

        st.radio(
            " ",
            ["있음", "없음"],
            index=None,
            key='pollen_yesorno',
            label_visibility="collapsed"
        )

        if st.session_state['pollen_yesorno'] == '있음':
            st.write('---')
            df = pd.read_excel('plants/알러지리스트.xlsx')
            allergen_list = df.iloc[:, 0].dropna().tolist()
            allergen_list.sort()

            st.write('해당하는 알레르기를 모두 선택하세요.')
            st.multiselect(
                label="해당하는 알레르기를 모두 선택하세요.",
                options=allergen_list,
                key="general_allergens",
                label_visibility='collapsed'
            )

            if '꽃가루' in st.session_state.get("general_allergens", []):
                st.write('---')
                st.markdown(
                    "<div style='font-size:20px; font-weight:600; margin-bottom:20px;'>꽃가루 알러지 상세 선택</div>",
                    unsafe_allow_html=True
                )

                st.radio("① 풀 꽃가루 알러지", ["있음", "없음", '모름'], index=None, key='pollen_grass')
                st.radio("② 나무 꽃가루 알러지", ["있음", "없음", '모름'], index=None, key='pollen_tree')
                st.radio("③ 잡초 꽃가루 알러지", ["있음", "없음", '모름'], index=None, key='pollen_weed')

                if all(x == '없음' for x in [
                    st.session_state['pollen_grass'],
                    st.session_state['pollen_tree'],
                    st.session_state['pollen_weed']
                ]):
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

                    st.radio("삭제", ["예", "아니오"], index=None, key='check_pollen', label_visibility='collapsed')

                    if st.session_state['check_pollen'] == '예':
                        if '꽃가루' in st.session_state['general_allergens']:
                            st.session_state['general_allergens'].remove('꽃가루')
                        for k in ['pollen_tree', 'pollen_grass', 'pollen_weed']:
                            st.session_state[k] = ''
                        st.session_state['re_check_pollen'] = 1
                        st.rerun()
                    elif st.session_state['check_pollen'] and st.session_state['re_check_pollen'] == 2:
                        for k in ['pollen_tree', 'pollen_grass', 'pollen_weed']:
                            st.session_state[k] = ''
                        st.write('-> 위 꽃가루 알러지 상세 선택을 수정해주세요.')
                        st.session_state['re_check_pollen'] = 2
                        st.rerun()

        st.write('---')
        if st.button('저장'):
            name = st.session_state.get('user_name', '')
            yn = st.session_state.get('pollen_yesorno', '')
            gl = st.session_state.get('general_allergens', [])
            pt = st.session_state.get('pollen_tree', '')
            pg = st.session_state.get('pollen_grass', '')
            pw = st.session_state.get('pollen_weed', '')

            if name != '':
                if yn == '없음':
                    # ✅ 위젯 key는 그대로 두고, saved_ 키로 복사 저장
                    st.session_state['saved_user_name'] = name
                    st.session_state['saved_pollen_yesorno'] = yn
                    st.session_state['saved_general_allergens'] = []
                    st.session_state['saved_pollen_tree'] = ''
                    st.session_state['saved_pollen_grass'] = ''
                    st.session_state['saved_pollen_weed'] = ''
                    st.session_state['check'] = '반복'
                    st.markdown("모든 입력이 완료되었습니다, 다음 페이지로 넘어가 분석 결과를 확인해보세요!")

                elif yn == '있음':
                    if gl == []:
                        st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')
                    else:
                        if '꽃가루' not in gl:
                            st.session_state['saved_user_name'] = name
                            st.session_state['saved_pollen_yesorno'] = yn
                            st.session_state['saved_general_allergens'] = gl
                            st.session_state['saved_pollen_tree'] = ''
                            st.session_state['saved_pollen_grass'] = ''
                            st.session_state['saved_pollen_weed'] = ''
                            st.session_state['check'] = '반복'
                            st.markdown("모든 입력이 완료되었습니다, 다음 페이지로 넘어가 분석 결과를 확인해보세요!")
                        elif '꽃가루' in gl:
                            if pt != '' and pg != '' and pw != '':
                                st.session_state['saved_user_name'] = name
                                st.session_state['saved_pollen_yesorno'] = yn
                                st.session_state['saved_general_allergens'] = gl
                                st.session_state['saved_pollen_tree'] = pt
                                st.session_state['saved_pollen_grass'] = pg
                                st.session_state['saved_pollen_weed'] = pw
                                st.session_state['check'] = '반복'
                                st.markdown("모든 입력이 완료되었습니다, 다음 페이지로 넘어가 분석 결과를 확인해보세요!")
                            else:
                                st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')
                else:
                    st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')
            else:
                st.markdown('모든 입력을 완료한 후 저장을 눌러주세요')
elif st.session_state['check'] == '반복':
    st.write('\n')
    if st.button('초기화'):
        for key in ['check', 'rerun']:
            st.session_state[key] = ''
        st.rerun()

    st.write('---')
    st.markdown(
        "<div style='font-size:15px; font-weight:500; color:gray; margin-bottom:15px;'>사용자의 이름을 입력하세요:</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size:15px; font-weight:500; color:gray; margin-bottom:15px;'>{st.session_state['user_name']}님, 환영합니다! 😄</div>",
        unsafe_allow_html=True
    )

    st.write('---')
    st.markdown(
        "<div style='font-size:15px; font-weight:600; color:gray; margin-bottom:15px;'>알러지를 가지고 있으신가요?</div>",
        unsafe_allow_html=True
    )
    pol = 0 if st.session_state['pollen_yesorno'] == '있음' else 1
    st.radio(" ", ["있음", "없음"], index=pol, label_visibility="collapsed", disabled=True)

    if st.session_state['pollen_yesorno'] == '있음':
        st.write('---')
        st.markdown(
            "<div style='font-size:15px; font-weight:600; color:gray; margin-bottom:15px;'>해당하는 알레르기를 모두 선택하세요.</div>",
            unsafe_allow_html=True
        )
        for word in st.session_state['general_allergens']:
            st.markdown(
                f"<div style='font-size:15px; font-weight:400; color:gray; line-height:2;'>- {word}</div>",
                unsafe_allow_html=True
            )

        if '꽃가루' in st.session_state['general_allergens']:
            st.write('---')
            st.markdown(
                "<div style='font-size:20px; font-weight:600; color:gray; margin-bottom:20px;'>꽃가루 알러지 상세 선택</div>",
                unsafe_allow_html=True
            )
            for k in ['pollen_grass', 'pollen_tree', 'pollen_weed']:
                idx = {'있음': 0, '없음': 1, '모름': 2}[st.session_state[k]]
                st.radio(f"→ {k.replace('pollen_', '')} 꽃가루 알러지", ["있음", "없음", "모름"], index=idx, disabled=True)

        st.markdown('---')
        st.markdown("<div style='color: gray; margin-bottom: 15px;'>모든 입력이 완료되었습니다,</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: gray;'>다른 페이지로 넘어가 분석 결과를 확인해보세요!</div>", unsafe_allow_html=True)
