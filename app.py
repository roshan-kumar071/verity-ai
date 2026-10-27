import streamlit as st
import requests
from verity.search import search_web
from verity.processing import process_sources
from verity.claims import extract_claims
from verity.evidence import compare_evidence

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
        st.subheader("Search Results")

        st.write("**Research question:**", question.strip())
        st.write("**Research mode:**", research_mode)

        try:
            with st.spinner("Searching the web..."):
                results = search_web(
                    question.strip(),
                    max_results=source_count,
                )
                results = process_sources(results)

                with st.expander("Debug: Original source text"):
                    for i, source in enumerate(results, start=1):
                        st.write(f"Source {i}: {source.get('title', '')}")
                        st.code(source.get("content", ""))

            if not results:
                st.warning("No sources found. Try a different question.")
            else:
                st.success(f"Found {len(results)} sources.")

                for i, source in enumerate(results, start=1):
                    title = source["title"] or "Untitled source"
                    url = source["url"]
                    content = source["content"]

                    with st.expander(f"{i}. {title}", expanded=(i == 1)):
                        if url:
                            st.markdown(f"[Open source]({url})")
                        if content:
                            st.write(content)
                        if source["score"] is not None:
                            st.caption(
                                f"Search relevance score: {source['score']}"
                            )

                st.info(
                    "These are search results, not verified conclusions. "
                    "Source credibility and conflicting evidence have not "
                    "yet been independently assessed."
                )


            claims = extract_claims(results, question.strip())

            st.subheader("Extracted Claims")

            if not claims:
                st.write("No suitable statements were found in these sources.")
            else:
                st.write(f"Extracted {len(claims)} candidate claims.")

                for i, claim in enumerate(claims, start=1):
                    with st.expander(f"{i}. {claim['claim']}"):
                        st.write("**Source:**", claim["source_title"])

                        if claim["source_url"]:
                            st.markdown(
                                f"[Open original source]({claim['source_url']})"
                            )

            st.caption(
                "These are candidate claims extracted from search-result text. "
                "They have not been fact-checked."
            )

            st.subheader("Evidence Comparison")

            st.warning(
                "These are preliminary rule-based classifications, "
                "not verified fact-check conclusions."
            )

            for claim_index, claim in enumerate(claims, start=1):
                comparison = compare_evidence(
                    claim["claim"],
                    results,
                )

                with st.expander(
                    f"Claim {claim_index}: {claim['claim']}"
                ):
                    categories = [
                        ("Supporting Evidence", comparison["supporting"]),
                        ("Contradicting Evidence", comparison["contradicting"]),
                        ("Insufficient Evidence", comparison["insufficient"]),
                    ]

                    for category_name, evidence_items in categories:
                        st.markdown(
                            f"**{category_name} ({len(evidence_items)})**"
                        )

                        if not evidence_items:
                            st.write("No sources in this category.")
                            continue

                        for item in evidence_items:
                            st.write(
                                item["source_title"] or "Untitled source"
                            )
                            st.caption(
                                f"Keyword overlap: {item['keyword_overlap']:.0%}"
                            )
                            st.write(item["text"])

                            if item["source_url"]:
                                st.markdown(
                                    f"[Open original source]({item['source_url']})"
                                )

        except requests.RequestException:
            st.error(
                "Web search request failed. Check your internet connection "
                "and Tavily API status, then try again."
            )
        except RuntimeError as error:
            st.error(str(error))


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

st.caption("Verity AI · Early prototype · " "Evidence before conclusions")
