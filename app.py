import os
from datetime import date
import requests
import streamlit as st
from exporters import make_docx, make_pdf

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)

API_URL = os.getenv(
    "LEGAL_EASE_API_URL",
    "http://127.0.0.1:8000"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
.stApp {
    background: #0e1424;
    color: #edf2ff;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}

.hero {
    padding: 1.4rem 1.7rem;
    border: 1px solid #293653;
    border-radius: 18px;
    background: linear-gradient(120deg,#18243e,#111a2d);
    margin-bottom: 1.5rem;
}

.small-muted {
    color: #aab6cf;
}

.download-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ---------- Header ----------
st.markdown(
    '<div class="hero">'
    '<h1>⚖️ LegalEase</h1>'
    '<p class="small-muted">AI-assisted legal document drafting workspace</p>'
    '</div>',
    unsafe_allow_html=True
)

st.warning(
    "LegalEase creates editable drafts for informational purposes. "
    "It does not provide legal advice or guarantee enforceability. "
    "Have important documents reviewed by a qualified lawyer."
)


# ---------- Session State ----------
if "document" not in st.session_state:
    st.session_state.document = ""

if "original_document" not in st.session_state:
    st.session_state.original_document = ""

if "doc_type" not in st.session_state:
    st.session_state.doc_type = "Employment Contract"


# ---------- Document Generation Form ----------
with st.form("draft_form"):

    left, right = st.columns(2)

    with left:

        doc_type = st.selectbox(
            "Document type",
            [
                "Employment Contract",
                "Non-Disclosure Agreement (NDA)",
                "Residential Lease Agreement",
                "Freelance Work Contract",
                "Service Agreement",
                "Employment Offer Letter",
                "Other"
            ]
        )

        parties = st.text_area(
            "Parties involved",
            placeholder="Full names, roles, and entity details",
            height=110
        )

        effective = st.date_input(
            "Effective date",
            value=date.today()
        ).isoformat()

        jurisdiction = st.text_input(
            "Jurisdiction / governing law",
            placeholder="e.g., Tamil Nadu, India"
        )

    with right:

        terms = st.text_area(
            "Terms & conditions",
            placeholder="Enter terms; separate individual clauses with semicolons.",
            height=190
        )

        extra = st.text_area(
            "Additional instructions (optional)",
            height=80
        )

    submitted = st.form_submit_button(
        "✨ Generate document",
        type="primary",
        use_container_width=True
    )


# ---------- Generate Document ----------
if submitted:

    if not parties.strip() or not terms.strip():

        st.error(
            "Please enter the parties and at least one term."
        )

    else:

        payload = {
            "document_type": doc_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective,
            "jurisdiction": jurisdiction or "Not specified",
            "additional_instructions": extra
        }

        with st.spinner(
            "Drafting your document with Gemini..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/generate",
                    json=payload,
                    timeout=180
                )

                if response.ok:

                    generated_document = response.json()["document"]

                    st.session_state.document = generated_document
                    st.session_state.original_document = generated_document
                    st.session_state.doc_type = doc_type

                    st.success(
                        "Draft generated. Review and edit it below."
                    )

                else:

                    try:
                        error_detail = response.json().get(
                            "detail",
                            response.text
                        )
                    except Exception:
                        error_detail = response.text

                    st.error(error_detail)

            except requests.RequestException as e:

                st.error(
                    f"Could not reach the backend at {API_URL}. "
                    f"Start FastAPI first. Details: {e}"
                )


# ---------- Document Preview & Editor ----------
if st.session_state.document:

    st.divider()

    st.subheader("📄 Document Preview & Editor")

    st.caption(
        "Review, edit, and save your document before downloading."
    )

    # ---------- Editable Document ----------
    edited = st.text_area(
        "Document content",
        value=st.session_state.document,
        height=600,
        key="editor"
    )

    # ---------- Editor Actions ----------
    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save Changes",
            use_container_width=True
        ):

            st.session_state.document = edited

            st.success(
                "Changes saved successfully."
            )

    with col2:

        if st.button(
            "↩️ Reset to Generated Version",
            use_container_width=True
        ):

            st.session_state.document = (
                st.session_state.original_document
            )

            st.rerun()


    # ---------- Optional Company Logo ----------
    with st.expander("🏢 Add company logo (optional)"):

        st.caption(
            "Upload a PNG or JPG logo to include it in DOCX and PDF exports."
        )

        logo = st.file_uploader(
            "Company logo",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )

    logo_bytes = logo.getvalue() if logo else None


    # ---------- Download Section ----------
    st.divider()

    st.markdown(
        '<div class="download-title">⬇️ Download your document</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Choose a format to save your edited document."
    )

    a, b, c = st.columns(3)

    with a:

        st.download_button(
            "📄 Download TXT",
            data=edited,
            file_name="legalease_draft.txt",
            mime="text/plain",
            use_container_width=True
        )

    with b:

        st.download_button(
            "📝 Download DOCX",
            data=make_docx(
                edited,
                st.session_state.doc_type,
                logo_bytes
            ),
            file_name="legalease_draft.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    with c:

        st.download_button(
            "📕 Download PDF",
            data=make_pdf(
                edited,
                st.session_state.doc_type,
                logo_bytes
            ),
            file_name="legalease_draft.pdf",
            mime="application/pdf",
            use_container_width=True
        )