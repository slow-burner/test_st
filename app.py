"""
🏭 Factory DB Flow Head 데이터 시각화 대시보드
────────────────────────────────────────────────
DataSpace DB(factory_db.flow_head)의 STEPID, PPID, DCSPEC_ID를
Streamlit으로 조회·시각화하는 웹 애플리케이션입니다.
"""

import os
import sys
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# ──────────────────────────────────────────────
# 페이지 기본 설정 (반드시 첫 번째 st 호출이어야 함)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Factory DB Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# 커스텀 CSS (다크 모던 테마)
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* 전체 배경 */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid #30363d;
}

/* 헤더 배너 */
.header-banner {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 50%, #58a6ff 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(31, 111, 235, 0.3);
}
.header-banner h1 {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 800;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
}
.header-banner p {
    color: rgba(255,255,255,0.85);
    font-size: 0.95rem;
    margin: 0;
}

/* 메트릭 카드 */
.metric-card {
    background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(88, 166, 255, 0.2);
}
.metric-card .metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #58a6ff;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-card .metric-label {
    font-size: 0.8rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
}
.metric-card .metric-icon {
    font-size: 1.4rem;
    margin-bottom: 0.4rem;
}

/* 섹션 타이틀 */
.section-title {
    color: #e6edf3;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 1.5rem 0 0.8rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #1f6feb;
    display: inline-block;
}

/* 사이드바 라벨 */
.sidebar-section {
    color: #8b949e;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 700;
    margin: 1.2rem 0 0.5rem 0;
}

/* 상태 뱃지 */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.status-connected {
    background: rgba(35, 134, 54, 0.2);
    border: 1px solid #238636;
    color: #3fb950;
}
.status-error {
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid #f85149;
    color: #f85149;
}

/* 데이터프레임 영역 */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* 버튼 스타일링 */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb, #388bfd);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #388bfd, #58a6ff);
    box-shadow: 0 4px 15px rgba(31, 111, 235, 0.4);
    transform: translateY(-1px);
}

/* 다운로드 버튼 */
.stDownloadButton > button {
    background: linear-gradient(135deg, #238636, #2ea043);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950);
    box-shadow: 0 4px 15px rgba(35, 134, 54, 0.4);
    transform: translateY(-1px);
}

/* 사이드바 슬라이더 */
[data-testid="stSlider"] > div > div > div {
    color: #58a6ff;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# .env 로드 (스크립트 위치 기준 절대 경로)
# ──────────────────────────────────────────────
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
_env_loaded = load_dotenv(dotenv_path=_env_path, override=True)


# ──────────────────────────────────────────────
# DB 연결 — @st.cache_resource로 세션 재활용
# ──────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_db_connection():
    """
    MySQL 커넥션을 생성하고 캐싱합니다.
    앱 재시작 없이 재연결이 필요하면 사이드바의 '새로고침' 버튼을 사용하세요.
    """
    try:
        import pymysql
    except ImportError:
        return None, "❌ pymysql 라이브러리가 없습니다. `pip install pymysql` 실행 후 재시작하세요."

    host     = os.getenv("DB_HOST", "127.0.0.1")
    port_str = os.getenv("DB_PORT", "3306")
    user     = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name  = os.getenv("DB_NAME", "")

    try:
        port = int(port_str)
    except ValueError:
        port = 3306

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name if db_name else None,
            charset="utf8mb4",
            connect_timeout=10,
            autocommit=True,
        )
        return conn, None  # (connection, error_msg)
    except Exception as e:
        return None, str(e)


# ──────────────────────────────────────────────
# 쿼리 실행 — @st.cache_data (TTL 60초)
# ──────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def fetch_data(limit: int, _refresh_key: int = 0):
    """
    factory_db.flow_head 에서 STEPID, PPID, DCSPEC_ID를 조회합니다.
    _refresh_key 변경 시 캐시를 무효화합니다.
    """
    conn, err = get_db_connection()
    if err:
        return None, err

    query = f"""
        SELECT
            STEPID,
            PPID,
            DCSPEC_ID
        FROM
            factory_db.flow_head
        LIMIT {int(limit)};
    """
    try:
        df = pd.read_sql(query, conn)
        return df, None
    except Exception as e:
        return None, str(e)


# ──────────────────────────────────────────────
# 사이드바
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 Factory DB")
    st.markdown("---")

    # 연결 상태 표시
    _, _test_err = get_db_connection()
    if _test_err is None:
        st.markdown(
            '<div class="status-badge status-connected">● DB 연결됨</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge status-error">● 연결 실패</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">⚙️ 조회 설정</p>', unsafe_allow_html=True)

    # 조회 건수 슬라이더
    limit = st.slider(
        "조회 건수 (LIMIT)",
        min_value=10,
        max_value=500,
        value=25,
        step=5,
        help="DB에서 가져올 최대 행 수를 설정합니다.",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">🔍 검색 필터</p>', unsafe_allow_html=True)

    # 검색 대상 컬럼 선택
    search_col = st.selectbox(
        "검색 대상 컬럼",
        options=["STEPID", "PPID", "DCSPEC_ID"],
        index=0,
    )

    # 검색어 입력
    search_term = st.text_input(
        "검색어 입력",
        placeholder=f"{search_col} 값을 입력하세요...",
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">🔄 데이터 관리</p>', unsafe_allow_html=True)

    # 새로고침 버튼 — refresh_key를 올려 캐시 무효화
    if "refresh_key" not in st.session_state:
        st.session_state.refresh_key = 0

    if st.button("🔄 데이터 새로고침", use_container_width=True):
        # cache_resource(커넥션)도 초기화
        get_db_connection.clear()
        fetch_data.clear()
        st.session_state.refresh_key += 1
        st.success("캐시가 초기화되었습니다.")

    st.markdown("---")
    st.markdown(
        "<small style='color:#8b949e;'>📅 데이터 캐시 TTL: 60초<br>"
        "🔗 factory_db.flow_head</small>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# 메인 헤더
# ──────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>🏭 Factory DB Flow Head 데이터 현황</h1>
    <p>DataSpace DB(factory_db.flow_head)의 공정 흐름 데이터를 실시간으로 조회하고 분석합니다.</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# .env 경고 표시
# ──────────────────────────────────────────────
if not _env_loaded:
    st.warning("⚠️ .env 파일을 찾을 수 없습니다. 환경 변수가 설정되어 있지 않으면 DB 접속에 실패할 수 있습니다.")


# ──────────────────────────────────────────────
# 데이터 로드
# ──────────────────────────────────────────────
with st.spinner("🔄 데이터베이스에서 데이터를 불러오는 중..."):
    df_raw, fetch_err = fetch_data(limit, _refresh_key=st.session_state.refresh_key)

# 에러 처리
if fetch_err:
    st.error(f"❌ 데이터베이스 오류\n\n{fetch_err}")
    st.info(
        "💡 **해결 방법**\n"
        "1. `.env` 파일의 DB 접속 정보(호스트·포트·사용자·비밀번호)를 확인하세요.\n"
        "2. MySQL 서버가 실행 중인지 확인하세요 (포트 3306).\n"
        "3. `factory_db` 스키마와 `flow_head` 테이블이 존재하는지 확인하세요.\n"
        "4. 사이드바의 **새로고침** 버튼을 눌러 재접속을 시도하세요."
    )
    st.stop()

if df_raw is None or df_raw.empty:
    st.warning("⚠️ 조회된 데이터가 없습니다. 테이블에 데이터가 있는지 확인하세요.")
    st.stop()


# ──────────────────────────────────────────────
# 클라이언트 측 검색 필터 적용
# ──────────────────────────────────────────────
df_filtered = df_raw.copy()

if search_term.strip():
    mask = df_filtered[search_col].astype(str).str.contains(
        search_term.strip(), case=False, na=False
    )
    df_filtered = df_filtered[mask]


# ──────────────────────────────────────────────
# 주요 지표 (Metric Cards) — 3열 레이아웃
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">📊 주요 지표</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📋</div>
        <div class="metric-value">{len(df_filtered):,}</div>
        <div class="metric-label">조회 레코드 수</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    unique_step = df_filtered["STEPID"].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🔢</div>
        <div class="metric-value">{unique_step:,}</div>
        <div class="metric-label">Unique STEPID</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    unique_ppid = df_filtered["PPID"].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🔗</div>
        <div class="metric-value">{unique_ppid:,}</div>
        <div class="metric-label">Unique PPID</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    unique_dc = df_filtered["DCSPEC_ID"].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📐</div>
        <div class="metric-value">{unique_dc:,}</div>
        <div class="metric-label">Unique DCSPEC_ID</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 검색 결과 안내
# ──────────────────────────────────────────────
if search_term.strip():
    if len(df_filtered) == 0:
        st.warning(f"🔍 **'{search_term}'** 에 해당하는 결과가 없습니다.")
        st.stop()
    else:
        st.info(
            f"🔍 **{search_col}** 에서 **'{search_term}'** 검색 결과: "
            f"**{len(df_filtered):,}건** / 전체 {len(df_raw):,}건"
        )


# ──────────────────────────────────────────────
# 데이터 테이블
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">📋 데이터 테이블</p>', unsafe_allow_html=True)

# 컬럼 표시 설정
column_config = {
    "STEPID":    st.column_config.TextColumn("STEP ID",    width="medium"),
    "PPID":      st.column_config.TextColumn("PP ID",      width="medium"),
    "DCSPEC_ID": st.column_config.TextColumn("DCSPEC ID",  width="large"),
}

st.dataframe(
    df_filtered.reset_index(drop=True),
    use_container_width=True,
    height=480,
    column_config=column_config,
    hide_index=False,
)


# ──────────────────────────────────────────────
# 하단: 다운로드 버튼 + 통계 요약
# ──────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
dl_col, stat_col = st.columns([1, 2])

with dl_col:
    st.markdown('<p class="section-title">⬇️ 데이터 내보내기</p>', unsafe_allow_html=True)
    csv_data = df_filtered.to_csv(index=False, encoding="utf-8-sig")
    filename = f"flow_head_{'filtered_' if search_term.strip() else ''}{limit}rows.csv"

    st.download_button(
        label="📥 CSV 다운로드",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
        help="현재 필터링된 데이터를 CSV 파일로 저장합니다.",
    )
    st.caption(f"파일명: `{filename}` · {len(df_filtered):,}행")

with stat_col:
    st.markdown('<p class="section-title">📈 컬럼별 통계 요약</p>', unsafe_allow_html=True)
    summary_data = {
        "컬럼": ["STEPID", "PPID", "DCSPEC_ID"],
        "전체 값 수": [
            len(df_filtered["STEPID"]),
            len(df_filtered["PPID"]),
            len(df_filtered["DCSPEC_ID"]),
        ],
        "고유 값 수": [
            df_filtered["STEPID"].nunique(),
            df_filtered["PPID"].nunique(),
            df_filtered["DCSPEC_ID"].nunique(),
        ],
        "NULL 수": [
            int(df_filtered["STEPID"].isna().sum()),
            int(df_filtered["PPID"].isna().sum()),
            int(df_filtered["DCSPEC_ID"].isna().sum()),
        ],
    }
    st.dataframe(
        pd.DataFrame(summary_data),
        use_container_width=True,
        hide_index=True,
    )
