import streamlit as st #pip install streamlit as st

st.title('forest guard 🌿')
st.set_page_config(
    page_title = "forestguard",
    page_icon= "./plants/icon.jpg")

st.markdown("""
### 🌲 ForestGuard 앱 소개

**ForestGuard**는 등산 중 건강과 안전을 위해 개발된 **AI 기반 산림 위험도 분석 앱**입니다. 사용자의 알레르기 이력과 산림 생태 데이터를 바탕으로 다음과 같은 기능을 제공합니다:<br>
<br>

- 🌿 **자생 식물 기반 위험 분석**  
  등산로에서 만날 수 있는 식물 중 알레르기를 유발할 수 있는 종을 분석하여 사용자에게 경고합니다. <br>
  <br>

- 🐝 **꽃가루·벌독·바퀴 교차 항원 위험도 예측**  
사용자의 알레르기 데이터를 기반으로, AI 모델이 알러지 위험도를 예측합니다. <br>
<br>


- 🐛 **절지동물 분포 시각화 및 주의 안내**  
  지네, 거미, 바퀴벌레 등의 위험 생물 분포를 지도 기반으로 보여주고, 주의사항을 제공합니다.
""",
    unsafe_allow_html=True)