import streamlit as st
import os
from PIL import Image

# ==========================================
# [기초 설정] 로그인 상태를 기억하기 위한 공간 만들기
# ==========================================
# 프로그램이 처음 켜졌을 때 'logged_in'이라는 변수가 없으면 False(로그인 안 됨)로 설정합니다.
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ==========================================
# 화면 1: 아직 로그인을 안 한 상태라면? (로그인 창만 보여주기)
# ==========================================
if not st.session_state["logged_in"]:
    # 화면 가운데에 예쁘게 정렬하기 위해 임시로 여백 칸을 만듭니다.
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        st.title("🔒 한우농가 컨설팅 시스템")
        st.subheader("로그인이 필요합니다.")
        
        # 아이디와 비밀번호 입력창
        user_id = st.text_input("사용자 아이디 (농가명 또는 관리자)")
        user_pw = st.text_input("비밀번호", type="password")
        
        # 로그인 버튼
        if st.button("로그인하기", use_container_width=True):
            # [수정] 농가별 고유 비밀번호 장부 만들기
            # 나중에는 이 정보가 데이터베이스(DB)로 들어갑니다.
            farm_passwords = {
                "": "beef77",   # 대박농장 비밀번호
                "행복축산": "cow1234",  # 행복축산 비밀번호
                "미래한우": "hanwoo99"  # 미래한우 비밀번호
            }
            
            # 1. 관리자 로그인 검사
            if user_id == "관리자" and user_pw == "0000":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "관리자"
                st.rerun()
                
            # 2. 일반 농가 로그인 검사 (장부에 아이디가 존재하고, 비밀번호가 일치하는지 확인)
            elif user_id in farm_passwords and user_pw == f" 장부에 적힌 비번과 일치한다면": # 설명용 주석
                pass # 아래 실제 작동 코드로 대체됩니다.
                
            # (위 엘리프 조건을 실제 작동하는 코드로 깔끔하게 정리한 버전입니다 👇)
            elif user_id in farm_passwords and user_pw == farm_passwords[user_id]:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "농가"
                st.session_state["farm_name"] = user_id
                st.rerun()
                
            else:
                st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")

# ==========================================
# 화면 2: 로그인이 성공한 상태라면? (메인 홈페이지 보여주기)
# ==========================================
else:
    # ------------------------------------------
    # [상단바] 로그아웃 버튼 만들기
    # ------------------------------------------
    # 오른쪽 위에 깔끔하게 로그아웃 버튼을 배치합니다.
    _, logout_col = st.columns([5, 1])
    with logout_col:
        if st.button("로그아웃"):
            st.session_state["logged_in"] = False
            st.rerun()

    # ------------------------------------------
    # [왼쪽 메뉴판] 로그인 권한에 따라 사이드바 다르게 보여주기
    # ------------------------------------------
    st.sidebar.title("🌾 한우 사양관리 메뉴")
    
    # 1. 관리자로 로그인했을 때
    if st.session_state["user_role"] == "관리자":
        st.sidebar.markdown("😎 **관리자 모드**로 접속 중")
        selected_farm = st.sidebar.selectbox("컨설팅할 농장 선택:", ["국인성농장", "행복축산", "미래한우"])
        menu = st.sidebar.radio("페이지 이동:", ["홈 (안내)", "농가별 리포트", "사진 자료실"])
    
    # 2. 일반 농가로 로그인했을 때 (자기 농장 이름 고정, 메뉴 제한)
    else:
        selected_farm = st.session_state["farm_name"]
        st.sidebar.markdown(f"🏡 **{selected_farm}** 사장님 환영합니다.")
        # 농가는 관리자 설정 같은 메뉴를 못 보게 '홈'과 '리포트'만 노출
        menu = st.sidebar.radio("페이지 이동:", ["홈 (안내)", "우리 농장 리포트", "사진 자료실"])

    st.sidebar.markdown("---")
    st.sidebar.caption(f"접속자: {st.session_state['user_role']}")

    # ------------------------------------------
    # [오른쪽 본문] 메뉴별 화면 그려주기
    # ------------------------------------------
    if menu in ["홈 (안내)"]:
        st.title("🏡 시스템 안내")
        st.write(f"안녕하세요! 현재 **{selected_farm}** 대시보드를 열람 중입니다.")
        st.info("정기 사양 관리 지침 및 TMR 배합 가이드라인을 확인하세요.")

    elif menu in ["농가별 리포트", "우리 농장 리포트"]:
        st.title(f"📊 {selected_farm}의 컨설팅 리포트")
        st.success("인증된 사용자만 볼 수 있는 사육 데이터 및 분석 차트 공간입니다.")
        st.write("축산 데이터(출하등급률, 사료 효율 등)가 여기에 시각화됩니다.")

    elif menu == "사진 자료실":
        st.title(f"📸 {selected_farm} 사진 히스토리 수집방")
        
        # 사진 폴더 자동 생성 로직
        upload_dir = f"farm_images/{selected_farm}"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 사진 등록 (관리자만 올릴 수 있게 제한하거나 농가도 올리게 하거나 선택 가능)
        st.subheader("새로운 사진 등록")
        uploaded_files = st.file_uploader("사진을 선택하세요 (여러 장 가능)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        if uploaded_files:
            for uploaded_file in uploaded_files:
                image = Image.open(uploaded_file)
                save_path = os.path.join(upload_dir, uploaded_file.name)
                image.thumbnail((1000, 1000))
                image.save(save_path, "JPEG", quality=80)
            st.success(f"🎉 총 {len(uploaded_files)}장의 사진이 저장되었습니다!")
            st.rerun()

        st.markdown("---")
        st.subheader(f"현재 {selected_farm}에 저장된 사진 목록")
        image_files = [f for f in os.listdir(upload_dir) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

        if len(image_files) == 0:
            st.info("아직 등록된 사진이 없습니다.")
        else:
            cols = st.columns(3)
            for idx, file_name in enumerate(image_files):
                col_idx = idx % 3
                full_path = os.path.join(upload_dir, file_name)
                img = Image.open(full_path)
                with cols[col_idx]:
                    st.image(img, use_container_width=True)
                    st.caption(file_name)