"""
BioLitAI - Streamlit Web Application
Main application file
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.pubmed_api import PubMedAPI
from src.llm_summarizer import BiomedicalSummarizer
from src.ner_extractor import BiomedicalNERExtractor
from src.gap_detector import ResearchGapDetector
from src.database import BioLitAIDatabase
from config import STREAMLIT_PAGE_CONFIG, MIN_ABSTRACT_LENGTH


def init_session_state():
    """Initialize Streamlit session state"""
    if "papers" not in st.session_state:
        st.session_state.papers = []
    if "current_query" not in st.session_state:
        st.session_state.current_query = ""
    if "search_id" not in st.session_state:
        st.session_state.search_id = None
    if "entities_summary" not in st.session_state:
        st.session_state.entities_summary = None
    if "gaps" not in st.session_state:
        st.session_state.gaps = None


def setup_page():
    """Setup Streamlit page configuration"""
    st.set_page_config(**STREAMLIT_PAGE_CONFIG)

    # Custom CSS
    st.markdown(
        """
        <style>
        .main {
            max-width: 1200px;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render application header"""
    st.markdown("# 🧬 BioLitAI")
    st.markdown(
        "### AI-Powered Biomedical Literature Mining and Research Gap Detection Tool"
    )
    st.markdown(
        "Search PubMed, analyze papers with AI, extract biomedical entities, and discover research gaps"
    )


def render_search_section():
    """Render literature search section"""
    st.header("📚 Search Literature")

    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_input(
            "Enter search query (MeSH terms or keywords)",
            placeholder="e.g., cancer immunotherapy, CRISPR gene therapy, COVID-19",
            help="Use MeSH terms for better results",
        )

    with col2:
        max_results = st.number_input("Max results", min_value=1, max_value=100, value=20)

    if st.button("🔍 Search PubMed", use_container_width=True):
        if query:
            with st.spinner("Searching PubMed..."):
                pubmed = PubMedAPI()
                pmids = pubmed.search(query, max_results=max_results)

                if pmids:
                    st.success(f"Found {len(pmids)} papers")

                    with st.spinner("Fetching paper details..."):
                        st.session_state.papers = pubmed.fetch_papers(pmids)
                        st.session_state.current_query = query

                        # Record search in database
                        db = BioLitAIDatabase()
                        st.session_state.search_id = db.record_search_query(
                            query, len(pmids)
                        )

                    st.rerun()
                else:
                    st.warning("No papers found. Try different keywords.")
        else:
            st.warning("Please enter a search query")


def render_papers_section():
    """Render papers display and analysis section"""
    if not st.session_state.papers:
        return

    st.header("📄 Search Results")

    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Papers Found", len(st.session_state.papers))
    with col2:
        avg_year = (
            sum(
                int(p.get("publication_date", "2000").split("/")[-1] or "2000"))
                for p in st.session_state.papers
            )
            / len(st.session_state.papers)
            if st.session_state.papers
            else 0
        )
        st.metric("Avg Publication Year", f"{int(avg_year)}")
    with col3:
        st.metric("Query", st.session_state.current_query[:30] + "...")

    # Analyze papers
    if st.button("🤖 Analyze Papers", use_container_width=True):
        with st.spinner("Analyzing papers..."):
            st.session_state.papers = analyze_papers(st.session_state.papers)
            st.session_state.entities_summary = get_entities_summary(
                st.session_state.papers
            )
        st.rerun()

    # Display papers
    st.subheader("Papers")
    papers_df = create_papers_dataframe(st.session_state.papers)
    st.dataframe(papers_df, use_container_width=True, height=400)

    # Show detailed view option
    with st.expander("View Detailed Paper Information"):
        selected_idx = st.selectbox(
            "Select paper",
            range(len(st.session_state.papers)),
            format_func=lambda i: st.session_state.papers[i]["title"][:60] + "...",
        )
        if selected_idx is not None:
            render_paper_detail(st.session_state.papers[selected_idx])


def render_entities_section():
    """Render named entities extraction section"""
    if not st.session_state.entities_summary:
        return

    st.header("🏷️ Extracted Biomedical Entities")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Diseases", len(st.session_state.entities_summary.get("diseases", [])))
    with col2:
        st.metric("Genes", len(st.session_state.entities_summary.get("genes", [])))
    with col3:
        st.metric("Drugs", len(st.session_state.entities_summary.get("drugs", [])))
    with col4:
        st.metric("Methods", len(st.session_state.entities_summary.get("methods", [])))

    # Display entities in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Diseases", "Genes", "Drugs", "Methods", "Organisms"])

    with tab1:
        display_entity_list(
            st.session_state.entities_summary.get("diseases", []), "Diseases"
        )

    with tab2:
        display_entity_list(
            st.session_state.entities_summary.get("genes", []), "Genes"
        )

    with tab3:
        display_entity_list(
            st.session_state.entities_summary.get("drugs", []), "Drugs"
        )

    with tab4:
        display_entity_list(
            st.session_state.entities_summary.get("methods", []), "Methods"
        )

    with tab5:
        display_entity_list(
            st.session_state.entities_summary.get("organisms", []), "Organisms"
        )


def render_gaps_section():
    """Render research gap detection section"""
    if not st.session_state.papers:
        return

    st.header("💡 Research Gap Detection")

    if st.button("🔬 Detect Research Gaps", use_container_width=True):
        with st.spinner("Detecting research gaps..."):
            gap_detector = ResearchGapDetector()
            st.session_state.gaps = gap_detector.detect_gaps(st.session_state.papers)

            # Save to database
            if st.session_state.search_id:
                db = BioLitAIDatabase()
                for gap in st.session_state.gaps.get("content_gaps", []):
                    db.add_research_gap(st.session_state.search_id, gap)

        st.rerun()

    if st.session_state.gaps:
        # Display gaps
        gap_detector = ResearchGapDetector()
        gaps = st.session_state.gaps

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Content Gaps", len(gaps.get("content_gaps", [])))
        with col2:
            st.metric("Methodology Gaps", len(gaps.get("methodology_gaps", [])))
        with col3:
            st.metric("Research Recommendations", len(gaps.get("recommendations", [])))

        # Content Gaps
        if gaps.get("content_gaps"):
            st.subheader("Content Gaps")
            for gap in gaps["content_gaps"]:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{gap['type']}**")
                        st.write(gap["description"])
                    with col2:
                        severity_color = (
                            "🔴"
                            if gap.get("severity") == "high"
                            else "🟡"
                            if gap.get("severity") == "medium"
                            else "🟢"
                        )
                        st.write(severity_color)
                    st.divider()

        # Methodology Gaps
        if gaps.get("methodology_gaps"):
            st.subheader("Methodology Gaps")
            for gap in gaps["methodology_gaps"]:
                st.write(f"**{gap['type']}**")
                st.write(gap["description"])
                if gap.get("suggestions"):
                    st.write(f"Suggestions: {', '.join(gap['suggestions'])}")
                st.divider()

        # Recommendations
        if gaps.get("recommendations"):
            st.subheader("🎯 Research Recommendations")
            for i, rec in enumerate(gaps["recommendations"], 1):
                st.write(f"{i}. {rec}")


def render_database_section():
    """Render database and history section"""
    st.header("💾 Database & History")

    col1, col2, col3 = st.columns(3)

    db = BioLitAIDatabase()
    stats = db.get_statistics()

    with col1:
        st.metric("Papers Stored", stats["papers"])
    with col2:
        st.metric("Searches Recorded", stats["searches"])
    with col3:
        st.metric("Research Gaps Found", stats["research_gaps"])

    # Recent searches
    with st.expander("View Recent Searches"):
        recent = db.get_recent_searches()
        if recent:
            recent_df = pd.DataFrame(recent)
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No searches yet")


def analyze_papers(papers):
    """Analyze papers with NER and summarization"""
    summarizer = BiomedicalSummarizer()
    ner_extractor = BiomedicalNERExtractor()
    db = BioLitAIDatabase()

    for paper in papers:
        # Summarize
        if paper.get("abstract"):
            paper["summary"] = summarizer.summarize(
                paper["abstract"], paper.get("title", ""), max_length=150
            )

        # Extract entities
        paper["entities"] = ner_extractor.extract_from_abstract(
            paper.get("title", ""), paper.get("abstract", "")
        )

        # Save to database
        db.add_paper(paper)

    return papers


def get_entities_summary(papers):
    """Get summary of all entities across papers"""
    ner_extractor = BiomedicalNERExtractor()
    return ner_extractor.get_unique_entities(papers)


def create_papers_dataframe(papers):
    """Create DataFrame from papers data"""
    data = []
    for paper in papers:
        data.append(
            {
                "Title": paper.get("title", "")[:60] + "...",
                "Journal": paper.get("journal", "N/A"),
                "Year": paper.get("publication_date", "N/A"),
                "PMID": paper.get("pmid", ""),
            }
        )
    return pd.DataFrame(data)


def render_paper_detail(paper):
    """Render detailed view of a single paper"""
    st.markdown(f"### {paper['title']}")
    st.markdown(f"**PMID:** {paper['pmid']} | **DOI:** {paper.get('doi', 'N/A')}")
    st.markdown(f"**Journal:** {paper.get('journal', 'N/A')}")
    st.markdown(f"**Authors:** {', '.join(paper.get('authors', [])[:3])}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Abstract")
        st.text(paper.get("abstract", "N/A"))

    with col2:
        st.subheader("Summary")
        st.text(paper.get("summary", "Not yet summarized"))

    if paper.get("entities"):
        st.subheader("Extracted Entities")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Diseases:** {', '.join(paper['entities'].get('diseases', [])[:5])}")
            st.write(f"**Genes:** {', '.join(paper['entities'].get('genes', [])[:5])}")
        with col2:
            st.write(f"**Drugs:** {', '.join(paper['entities'].get('drugs', [])[:5])}")
            st.write(f"**Methods:** {', '.join(paper['entities'].get('methods', [])[:5])}")

    st.markdown(f"[Open on PubMed]({paper.get('url', '')})")


def display_entity_list(entities, entity_type):
    """Display a list of entities"""
    if entities:
        cols = st.columns(4)
        for i, entity in enumerate(entities[:20]):
            with cols[i % 4]:
                st.write(f"• {entity}")
    else:
        st.info(f"No {entity_type.lower()} found")


def main():
    """Main application entry point"""
    setup_page()
    init_session_state()

    render_header()

    st.divider()

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🔍 Search", "📊 Analysis", "💡 Gaps", "💾 Database"]
    )

    with tab1:
        render_search_section()

    with tab2:
        if st.session_state.papers:
            render_papers_section()
            st.divider()
            render_entities_section()
        else:
            st.info("Search for papers first to see analysis")

    with tab3:
        render_gaps_section()

    with tab4:
        render_database_section()

    # Footer
    st.divider()
    st.markdown(
        """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    BioLitAI v0.1.0 | Built with Streamlit, HuggingFace, and PubMed API
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
