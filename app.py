import streamlit as st
import os
import json
import tempfile
from parsers.resume_parser import ResumeParser
from analyzers.gemini_client import GeminiClient
from generators.resume_generator import ResumeGenerator

st.set_page_config(
    page_title="ATS Resume Optimizer",
    page_icon=":page_facing_up:",
    layout="wide"
)

st.title("ATS Resume Optimizer")
st.subheader("Upload your resume and get AI-powered optimization suggestions")

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

with st.sidebar:
    st.header("Settings")
    job_description = st.text_area(
        "Target Job Description (Optional)",
        help="Paste the job description to get targeted suggestions",
        height=200
    )

uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx", "doc"]
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    if st.button("Analyze Resume", type="primary"):
        with st.spinner("Analyzing your resume..."):
            try:
                parser = ResumeParser()
                resume_text = parser.extract_text(tmp_file_path)

                if not resume_text:
                    st.error("Could not extract text from the resume. Please try a different file.")
                else:
                    client = GeminiClient()
                    result = client.analyze_resume(resume_text, job_description if job_description else None)

                    try:
                        cleaned_result = result.strip()
                        if cleaned_result.startswith("```"):
                            cleaned_result = cleaned_result.split("```", 2)[-2] if "```" in cleaned_result[3:] else cleaned_result
                            if cleaned_result.startswith("json"):
                                cleaned_result = cleaned_result[4:].strip()
                        
                        result_json = json.loads(cleaned_result)
                        st.session_state.analysis_result = result_json
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing analysis result. Please try again. Debug info: {str(e)}")
                        st.error(f"Raw response: {result[:500]}...")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    os.unlink(tmp_file_path)

if st.session_state.analysis_result:
    result = st.session_state.analysis_result

    st.divider()
    st.header("Analysis Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        score = result.get("ats_score", 0)
        st.metric("ATS Score", f"{score}/100")
        if score >= 80:
            st.success("Great resume!")
        elif score >= 60:
            st.warning("Needs improvement")
        else:
            st.error("Significant optimization needed")

    with col2:
        keywords_present = len(result.get("keyword_analysis", {}).get("present_keywords", []))
        st.metric("Keywords Found", keywords_present)

    with col3:
        keywords_missing = len(result.get("keyword_analysis", {}).get("missing_keywords", []))
        st.metric("Missing Keywords", keywords_missing)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Keyword Analysis",
        "Format Suggestions",
        "Section Analysis",
        "Optimized Resume"
    ])

    with tab1:
        st.subheader("Keyword Analysis")
        keyword_data = result.get("keyword_analysis", {})

        col1, col2 = st.columns(2)
        with col1:
            st.success("Present Keywords")
            for kw in keyword_data.get("present_keywords", []):
                st.markdown(f"- {kw}")

        with col2:
            st.error("Missing Keywords")
            for kw in keyword_data.get("missing_keywords", []):
                st.markdown(f"- {kw}")

        if keyword_data.get("suggested_keywords"):
            st.info("Suggested Keywords")
            for kw in keyword_data.get("suggested_keywords", []):
                st.markdown(f"- {kw}")

    with tab2:
        st.subheader("Format Suggestions")
        for suggestion in result.get("format_suggestions", []):
            st.markdown(f"- {suggestion}")

    with tab3:
        st.subheader("Section-wise Analysis")
        section_data = result.get("section_analysis", {})

        for section_name, section_info in section_data.items():
            with st.expander(f"{section_name.replace('_', ' ').title()} (Score: {section_info.get('score', 'N/A')}/100)"):
                st.write(section_info.get("feedback", "No feedback available"))

    with tab4:
        st.subheader("Optimized Resume")
        optimized_resume = result.get("optimized_resume", "")
        st.text_area("Optimized Resume Content", optimized_resume, height=400)

        if optimized_resume:
            generator = ResumeGenerator()

            col1, col2, col3 = st.columns(3)

            with col1:
                docx_path = generator.generate(optimized_resume, "docx")
                with open(docx_path, "rb") as f:
                    st.download_button(
                        label="Download DOCX",
                        data=f,
                        file_name="optimized_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                os.unlink(docx_path)

            with col2:
                try:
                    pdf_path = generator.generate(optimized_resume, "pdf")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="Download PDF",
                            data=f,
                            file_name="optimized_resume.pdf",
                            mime="application/pdf"
                        )
                    os.unlink(pdf_path)
                except ImportError:
                    st.caption("PDF: pip install fpdf")

            with col3:
                txt_path = generator.generate(optimized_resume, "txt")
                with open(txt_path, "r", encoding="utf-8") as f:
                    txt_content = f.read()
                st.download_button(
                    label="Download TXT",
                    data=txt_content,
                    file_name="optimized_resume.txt",
                    mime="text/plain"
                )
                os.unlink(txt_path)

    st.divider()
    st.info(result.get("overall_feedback", ""))

else:
    st.info("Upload your resume to get started!")
