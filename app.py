
import streamlit as st

st.set_page_config(
    page_title="Verity AI | Research Workspace",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Verity AI")
st.caption(
    "AI Research & Fact-Checking Agent · "
    "Evidence-first research with transparent findings"
)

st.divider()

with st.sidebar:
    st.header("Research Settings")

    source_count = st.slider(
        "Maximum search results",
        min_value=3,
        max_value=10,
        value=5,
    )

    research_mode = st.selectbox(
        "Research mode",
        [
            "Balanced research",
            "Evidence-focused",
            "Contradiction search",
        ],
    )

    st.divider()
    st.caption("Version 0.1 · Research interface prototype")

st.subheader("Start a research task")

question = st.text_area(
    "What would you like to investigate?",
    placeholder=(
        "Example: Does remote work improve "
        "employee productivity?"
    ),
    height=130,
    max_chars=1000,
)

start_research = st.button(
    "Start research",
    type="primary",
    use_container_width=True,
)

if start_research:
    if not question.strip():
        st.warning("Please enter a research question first.")
    else:
        st.info(
            "Research pipeline is not connected yet. "
            "This prototype captures your research settings only."
        )

        st.markdown("### Your research task")
        st.write("**Question:**", question.strip())
        st.write("**Research mode:**", research_mode)
        st.write("**Maximum search results:**", source_count)

        st.caption(
            "No live search, evidence verification, "
            "or AI-generated conclusions are performed yet."
        )

st.divider()

st.subheader("How Verity AI will work")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 01 · Discover")
    st.write(
        "Find relevant web sources and collect information "
        "related to the research question."
    )

with col2:
    st.markdown("### 02 · Verify")
    st.write(
        "Compare claims against supporting and contradicting "
        "evidence, while identifying uncertainty."
    )

with col3:
    st.markdown("### 03 · Report")
    st.write(
        "Present evidence-based findings with source citations "
        "and clearly stated limitations."
    )

st.divider()

st.caption(
    "Verity AI · Early prototype · "
    "Evidence before conclusions"
)
