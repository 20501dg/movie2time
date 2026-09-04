import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2",
    page_icon="🎬",
    layout="wide"
)

# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 216편의 데이터를 시각적으로 살펴봅니다."
)

st.divider()

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 장르가 여러 개이면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .str.split("|")
        .str[0]
    )

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()

# --------------------------------------------------
# 기본 정보
# --------------------------------------------------
st.info(f"📊 현재 분석 데이터: **{len(df):,}편**")

# --------------------------------------------------
# 그래프 1. 장르별 영화 편수
# --------------------------------------------------
st.subheader("1. 장르별 영화 편수")

genre_count = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]

fig_genre = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수",
)

fig_genre.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
)

fig_genre.update_layout(
    height=550,
    showlegend=True,
    legend_title_text="장르"
)

st.plotly_chart(
    fig_genre,
    use_container_width=True
)

# --------------------------------------------------
# 그래프로 알 수 있는 것
# --------------------------------------------------
st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "장르별 영화 편수를 비교하면 이 기간에 어떤 장르의 영화가 "
    "상대적으로 많이 개봉했는지 한눈에 알 수 있습니다."
)

st.divider()

# --------------------------------------------------
# 데이터 표
# --------------------------------------------------
st.subheader("📋 원본 데이터 미리보기")

display_columns = [
    "movieCd",
    "movieNm",
    "openDt",
    "genre",
    "nation",
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

st.dataframe(
    df[display_columns],
    use_container_width=True,
    hide_index=True
)
