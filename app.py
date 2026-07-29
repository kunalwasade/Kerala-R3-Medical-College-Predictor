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

st.title("🎓 Kerala Medical College Predictor")
st.markdown("Predict Kerala Medical Colleges based on the previous year's allotment data.")

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
# Sidebar Inputs
# ---------------------------------

st.sidebar.header("Enter Candidate Details")

rank = st.sidebar.number_input(
    "Enter Rank",
    min_value=1,
    step=1
)

course = st.sidebar.selectbox(
    "Course",
    sorted(df["Course"].dropna().unique())
)

college_type = st.sidebar.selectbox(
    "College Type",
    sorted(df["College Type"].dropna().unique())
)

candidate_category = st.sidebar.selectbox(
    "Candidate Category",
    sorted(df["Candidate Category"].dropna().unique())
)

alloted_category = st.sidebar.selectbox(
    "Alloted Category",
    sorted(df["Alloted Category"].dropna().unique())
)

predict = st.sidebar.button("🔍 Predict Colleges")

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
        # Summary
        # ---------------------------------

        st.success("Prediction Completed Successfully")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Your Rank",
                int(rank)
            )

            st.metric(
                "Course",
                course
            )

            st.metric(
                "College Type",
                college_type
            )

        with col2:

            st.metric(
                "Candidate Category",
                candidate_category
            )

            st.metric(
                "Alloted Category",
                alloted_category
            )

            st.metric(
                "Previous Year Cutoff",
                best_match_rank
            )

        st.info(f"🏥 **Best Match College:** {best_match_college}")

        st.subheader("Recommended Colleges")

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )
        # -----------------------------
        # Generate PDF
        # -----------------------------
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

        # -----------------------------
        # Download Button
        # -----------------------------
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf,
            file_name=f"Kerala_College_Prediction_{int(rank)}.pdf",
            mime="application/pdf",
            use_container_width=True
        )