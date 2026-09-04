import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 216편의 데이터를 다양한 그래프로 살펴봅니다."
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
        .str.strip()
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 영화명 결측값 처리
    df["movieNm"] = df["movieNm"].fillna("영화명 없음")

    # 국가 결측값 처리
    df["nation"] = (
        df["nation"]
        .fillna("기타")
        .astype(str)
        .str.strip()
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


# ==================================================
# 1. 장르별 영화 편수 - 도넛 그래프
# ==================================================

st.header("1️⃣ 장르별 영화 편수")

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
    title="장르별 영화 편수"
)

fig_genre.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig_genre.update_layout(
    height=550,
    legend_title_text="장르"
)

st.plotly_chart(
    fig_genre,
    use_container_width=True
)


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "장르별 영화 편수를 비교하면 이 기간에 어떤 장르의 영화가 "
    "상대적으로 많이 개봉했는지 알 수 있습니다."
)

st.divider()


# ==================================================
# 2. 장르 속 영화 - 트리맵
# ==================================================

st.header("2️⃣ 장르 안에 들어 있는 영화")

st.caption(
    "칸의 크기는 총 관객 수(total_audi)에 비례합니다."
)


treemap_df = df[
    ["genre", "movieNm", "total_audi"]
].dropna(
    subset=["genre", "movieNm", "total_audi"]
).copy()


fig_treemap = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화와 총 관객 수"
)

fig_treemap.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig_treemap.update_layout(
    height=650
)

st.plotly_chart(
    fig_treemap,
    use_container_width=True
)


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "각 장르 안에서 어떤 영화가 많은 관객을 모았는지와 "
    "영화별 관객 규모의 차이를 한눈에 비교할 수 있습니다."
)

st.divider()


# ==================================================
# 3. 총 관객 수 히스토그램
# ==================================================

st.header("3️⃣ 총 관객 수의 분포")

hist_df = df[
    ["movieNm", "total_audi"]
].dropna(
    subset=["total_audi"]
).copy()


fig_hist = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포",
    labels={
        "total_audi": "총 관객 수"
    }
)

fig_hist.update_traces(
    hovertemplate=(
        "관객 수 구간: %{x}<br>"
        "영화 수: %{y}편"
        "<extra></extra>"
    )
)

fig_hist.update_layout(
    height=550,
    xaxis_tickformat=","
)

st.plotly_chart(
    fig_hist,
    use_container_width=True
)


# 가장 관객이 많은 영화
most_popular = df.loc[
    df["total_audi"].idxmax()
]

max_audience = most_popular["total_audi"]
max_movie = most_popular["movieNm"]


# 가장 많이 몰린 구간 계산
counts, bins = pd.cut(
    hist_df["total_audi"],
    bins=20,
    retbins=True
)

bin_counts = counts.value_counts().sort_index()

if len(bin_counts) > 0:

    most_common_bin = bin_counts.idxmax()

    low_value = most_common_bin.left
    high_value = most_common_bin.right

    distribution_text = (
        f"대부분의 영화는 약 **{low_value:,.0f}명~"
        f"{high_value:,.0f}명** 구간에 몰려 있습니다."
    )

else:

    distribution_text = "관객 수 분포를 계산할 수 없습니다."


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    f"{distribution_text} "
    f"가장 많은 관객을 기록한 영화는 **{max_movie}**로, "
    f"총 **{max_audience:,.0f}명**의 관객을 모았습니다."
)

st.divider()


# ==================================================
# 4. 개봉일 스크린 수 vs 총 관객 - 산점도
# ==================================================

st.header("4️⃣ 개봉일 스크린 수와 총 관객의 관계")

scatter_df = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi"
    ]
].dropna(
    subset=[
        "first_scrn",
        "total_audi"
    ]
).copy()


fig_scatter = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre": "장르"
    }
)

fig_scatter.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린 수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig_scatter.update_layout(
    height=650,
    yaxis_tickformat=","
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "개봉일에 더 많은 스크린을 확보한 영화가 총 관객 수에서도 "
    "높은 성과를 보이는 경향이 있는지 살펴볼 수 있습니다."
)

st.divider()


# ==================================================
# 5. 장르별 총 관객 수 - 박스플롯
# ==================================================

st.header("5️⃣ 장르별 총 관객 수 분포")

# 영화가 10편 이상인 장르만 선택
genre_10plus = (
    df["genre"]
    .value_counts()
)

genre_10plus = genre_10plus[
    genre_10plus >= 10
].index


box_df = df[
    df["genre"].isin(genre_10plus)
].copy()

box_df = box_df[
    [
        "genre",
        "movieNm",
        "total_audi"
    ]
].dropna(
    subset=["total_audi"]
)


fig_box = px.box(
    box_df,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    title="영화가 10편 이상인 장르의 총 관객 수 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객 수"
    }
)

fig_box.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig_box.update_layout(
    height=650,
    yaxis_tickformat=","
)

st.plotly_chart(
    fig_box,
    use_container_width=True
)


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "영화가 많은 장르끼리 비교하면 장르별 총 관객 수의 중앙값과 "
    "분포 범위, 그리고 다른 영화보다 특히 관객이 많은 영화가 "
    "어떤 장르에 있는지 살펴볼 수 있습니다."
)

st.divider()


# ==================================================
# 6. 개봉일 스크린 수 + 첫 주 관객 버블 산점도
# ==================================================

st.header("6️⃣ 개봉일 스크린 수와 총 관객의 관계 - 버블 그래프")

bubble_df = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
].dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
).copy()


# 버블 크기가 너무 작은 경우를 방지
bubble_df["bubble_size"] = (
    bubble_df["first_week_audi"].clip(lower=1)
)


fig_bubble = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="bubble_size",
    color="genre",
    hover_name="movieNm",
    size_max=45,
    title="개봉일 스크린 수 · 총 관객 · 첫 주 관객",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre": "장르",
        "bubble_size": "첫 주 관객"
    }
)

fig_bubble.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린 수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명<br>"
        "첫 주 관객: %{marker.size:,.0f}명"
        "<extra></extra>"
    )
)

fig_bubble.update_layout(
    height=700,
    yaxis_tickformat=","
)

st.plotly_chart(
    fig_bubble,
    use_container_width=True
)


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "개봉일 스크린 수와 총 관객의 관계뿐만 아니라 "
    "첫 주에 얼마나 많은 관객을 모았는지를 버블 크기로 함께 비교할 수 있습니다."
)

st.divider()


# ==================================================
# 7. 제작 국가 → 장르 선버스트
# ==================================================

st.header("7️⃣ 제작 국가에서 장르로 내려가는 분포")

sunburst_df = df[
    [
        "nation",
        "genre"
    ]
].dropna(
    subset=[
        "nation",
        "genre"
    ]
).copy()


# 국가와 장르별 영화 편수 계산
sunburst_count = (
    sunburst_df
    .groupby(
        ["nation", "genre"],
        as_index=False
    )
    .size()
)

sunburst_count.columns = [
    "nation",
    "genre",
    "영화 편수"
]


fig_sunburst = px.sunburst(
    sunburst_count,
    path=["nation", "genre"],
    values="영화 편수",
    title="제작 국가 → 장르별 영화 편수"
)

fig_sunburst.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig_sunburst.update_layout(
    height=700
)

st.plotly_chart(
    fig_sunburst,
    use_container_width=True
)


st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "어떤 제작 국가의 영화가 많이 포함되어 있는지와 "
    "각 국가에서 어떤 장르의 영화가 많이 나타나는지를 함께 살펴볼 수 있습니다."
)

st.divider()


# ==================================================
# 데이터 표
# ==================================================

st.header("📋 분석에 사용한 데이터")

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
