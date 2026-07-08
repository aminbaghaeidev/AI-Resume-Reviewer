import streamlit as st
import yaml

from resume_formatter import format_resume
from utils.llm import parse_resume, review_resume
from utils.pdf_reader import extract_text_from_pdf


def main():
    st.title(":page_facing_up: Resume Parser and Reviewer")
    st.sidebar.markdown("""
        :brain: :robot: ResumeAI is an advanced tool that leverages the power of Large Language Models (LLMs) to analyze and improve resumes.
    """)
    st.markdown(
        """
        <style>
        button[kind="primary"] {
            background-color: #7C3AED;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6em 1.2em;
            font-weight: 600;
            transition: background-color 0.2s ease;
        }
        button[kind="primary"]:hover {
            background-color: #6D28D9;
            color: white;
        }
        button[kind="primary"]:active {
            background-color: #5B21B6;
            color: white;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
        job_description = st.text_area(
            "Enter job description (optional)",
            placeholder="Your Job Description",
            height=180,
        ).strip()
        if st.button("Run Analysis", use_container_width=True, type="primary"):
            if uploaded_file is None:
                st.error("Please upload your resume first!")

            else:
                resume_text = extract_text_from_pdf(uploaded_file)
                with st.spinner("Parsing resume... [Step 1 of 2]"):
                    resume_yaml = parse_resume(resume_text)
                with st.spinner("Reviewing resume... [Step 2 of 2]"):
                    review_response = review_resume(resume_yaml, job_description)

                resume_data = yaml.safe_load(resume_yaml)
                review_data = yaml.safe_load(review_response)

                st.session_state.resume_data = resume_data
                st.session_state.review_data = review_data
                st.session_state.current_section = 0
                st.session_state.sections = list(resume_data.keys())


    if "resume_data" in st.session_state and "review_data" in st.session_state:
        display_analysis()
    else:
        st.info("Please upload a resume and run the analysis to view results.")


def display_analysis():
    col1, col2, col3 = st.columns([3, 1, 3])
    with col1:
        if (
            st.button("⬅️", use_container_width=True)
            and st.session_state.current_section > 0
        ):
            st.session_state.current_section -= 1
    with col2:
        page_number = (
            f"{st.session_state.current_section + 1}/{len(st.session_state.sections)}"
        )
        st.markdown(
            f"""
            <div style="
                border:1px solid #ccc;
                border-radius:8px;
                padding:8px;
                text-align:center;
                font-weight:bold;
            ">
                {page_number}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        if st.button("➡️", use_container_width=True,):
            if st.session_state.current_section < len(st.session_state.sections) - 1:
                st.session_state.current_section += 1
                st.rerun()

    current_section = st.session_state.sections[st.session_state.current_section]

    revision_suggestion_placeholder = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        st.info(":x: **Original**")
        current_section_data = st.session_state.resume_data[current_section]
        st.info(format_resume({current_section: current_section_data}))
    with col2:
        st.success(":white_check_mark: **Revised**")
        current_section_data = st.session_state.review_data[current_section]
        impact_level = current_section_data["impact_level"]
        revision_suggestion = current_section_data["revision_suggestion"]
        revised_content = current_section_data["revised_content"]
        st.success(format_resume({current_section: revised_content}))

    with revision_suggestion_placeholder.expander(
        "Revision Suggestions", expanded=True
    ):
        if impact_level == "Low":
            st.info(f"Impact Level: {impact_level}")
        elif impact_level == "Medium":
            st.warning(f"Impact Level: {impact_level}")
        elif impact_level == "High":
            st.error(f"Impact Level: {impact_level}")

        for suggestion in revision_suggestion:
            st.markdown(f"- {suggestion}")


if __name__ == "__main__":
    main()
