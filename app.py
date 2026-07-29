from pdf_report import generate_pdf
import streamlit as st
import pandas as pd

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Kerala Medical College Predictor",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------
# Custom CSS
# ---------------------------------
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.title{
    text-align:center;
    font-size:clamp(30px,5vw,48px);
    font-weight:700;
    color:#0E4D92;
}

.subtitle{
    text-align:center;
    font-size:clamp(16px,2vw,22px);
    color:#666666;
    margin-bottom:25px;
}

div.stButton > button{
    background:#0E4D92;
    color:white;
    font-size:18px;
    font-weight:bold;
    border-radius:10px;
    height:55px;
    border:none;
}

div.stButton > button:hover{
    background:#1565C0;
    color:white;
}

[data-testid="stMetric"]{
    border:1px solid #E5E5E5;
    border-radius:12px;
    padding:12px;
    background:#FAFAFA;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------
# Title
# ---------------------------------

st.markdown("""
<h1 class="title">
🎓 Kerala Medical College Predictor
</h1>

<p class="subtitle">
Predict Kerala Medical Colleges using the previous year's allotment data
</p>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------
# Load Dataset
# ---------------------------------

@st.cache_data
def load_data():

    df = pd.read_excel("KERALA R3 ALLOTT.xlsx")

    df.columns = (
        df.columns
        .str.replace("\n", " ", regex=False)
        .str.strip()
    )

    return df


df = load_data()

# ---------------------------------
# Candidate Details
# ---------------------------------

st.subheader("📝 Candidate Details")

with st.form("prediction_form"):

    rank = st.number_input(
        "🏆 Enter Rank",
        min_value=1,
        step=1
    )

    course = st.selectbox(
        "📚 Course",
        sorted(df["Course"].dropna().unique())
    )

    college_type = st.selectbox(
        "🏥 College Type",
        sorted(df["College Type"].dropna().unique())
    )

    candidate_category = st.selectbox(
        "👤 Candidate Category",
        sorted(df["Candidate Category"].dropna().unique())
    )

    alloted_category = st.selectbox(
        "🏷️ Alloted Category",
        sorted(df["Alloted Category"].dropna().unique())
    )

    predict = st.form_submit_button(
        "🔍 Predict Colleges"
    )

st.divider()
# ---------------------------------
# Prediction
# ---------------------------------

if predict:

    filtered = df[
        (df["College Type"] == college_type) &
        (df["Course"] == course) &
        (df["Candidate Category"] == candidate_category) &
        (df["Alloted Category"] == alloted_category)
    ].copy()

    if filtered.empty:

        st.error("❌ No matching records found.")

    else:

        filtered["Gap"] = filtered["Rank"] - rank

        closest_record = filtered.loc[
            filtered["Gap"].abs().idxmin()
        ]

        best_match_college = closest_record["College Name"]
        best_match_rank = int(closest_record["Rank"])

        # -----------------------------
        # Chance Function
        # -----------------------------

        def chance(cutoff_rank, user_rank):

            diff = cutoff_rank - user_rank

            if diff >= 200:
                return "🟢 High Chance"

            elif diff >= -100:
                return "🟡 Borderline"

            else:
                return "🔴 Tough Chance"

        filtered["Chance"] = filtered["Rank"].apply(
            lambda x: chance(x, rank)
        )

        result = (
            filtered
            .sort_values("Rank", ascending=False)
            .drop_duplicates(subset="College Name", keep="first")
        )

        result = (
            result
            .sort_values("Rank")
            .reset_index(drop=True)
        )

        result.insert(
            0,
            "S.No",
            range(1, len(result) + 1)
        )

        result = result[
            [
                "S.No",
                "Course",
                "College Type",
                "Candidate Category",
                "Alloted Category",
                "Rank",
                "College Name",
                "Chance"
            ]
        ]

        # ---------------------------------
        # Success Message
        # ---------------------------------

        st.success("✅ Prediction Completed Successfully")
        st.success(f"🏫 Found {len(result)} matching colleges.")

        # ---------------------------------
        # Summary Cards
        # ---------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.metric("Your Rank", int(rank))
            st.metric("Course", course)
            st.metric("College Type", college_type)

        with col2:

            st.metric("Candidate Category", candidate_category)
            st.metric("Alloted Category", alloted_category)
            st.metric("Previous Year Cutoff", best_match_rank)

        # ---------------------------------
        # Best Match College
        # ---------------------------------

        st.markdown(f"""
### 🏥 Best Match College

**{best_match_college}**

📌 Previous Year Cutoff Rank: **{best_match_rank}**
""")

        st.divider()

        # ---------------------------------
        # Search College
        # ---------------------------------

        search = st.text_input(
            "🔍 Search College",
            placeholder="Type college name..."
        )

        if search:

            result = result[
                result["College Name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.subheader(f"Recommended Colleges ({len(result)})")

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        st.divider()

        # ---------------------------------
        # Generate PDF
        # ---------------------------------

        pdf = generate_pdf(
            result=result,
            rank=rank,
            course=course,
            college_type=college_type,
            candidate_category=candidate_category,
            alloted_category=alloted_category,
            best_match_college=best_match_college,
            best_match_rank=best_match_rank
        )

        # ---------------------------------
        # Download Report
        # ---------------------------------

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf,
            file_name=f"Kerala_College_Prediction_{int(rank)}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.caption(
            "📌 This prediction is based on the previous year's Kerala Medical College allotment data."
        )