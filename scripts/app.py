import streamlit as st
import sys
import os
from datetime import date
from PIL import Image

sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from rag_pipeline import SwiftVisaRAG
from utils.form_fields import COMMON_FIELDS, VISA_FIELDS_MAP, get_visa_fields
from utils.Country_config import (
    SUPPORTED_COUNTRIES,
    get_visa_display_name,
    get_visa_types_for_country,
    
)


# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SwiftVisa – Visa Eligibility Screening",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLES ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1F2933;
}
.stMainBlockContainer { background-color: #FFFFFF; }

[data-testid="stSidebar"] {
    background-color: #E6F0FF;
    background-image: linear-gradient(135deg, #E6F0FF 0%, #F0E8FF 100%);
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding-top: 2rem; }
[data-testid="stSidebar"] .stMarkdown { color: #1F2933; }
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stMarkdown h4 { color: #002CA6; }
[data-testid="stSidebar"] .stMarkdown p { color: #4B5563; font-size: 13px; }
[data-testid="stSidebar"] hr { border-color: #C80730; }

.main-title { font-size: 32px; font-weight: 700; margin: 0 0 0.25rem 0; color: #002CA6; }
.subtitle   { font-size: 15px; color: #C80730; margin-top: 0.25rem; font-weight: 500; }

.section-title {
    font-size: 20px; font-weight: 600;
    margin: 1.5rem 0 0.75rem 0; color: #002CA6;
}
.subsection-title {
    font-size: 13px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px;
    color: #C80730; margin-top: 1.5rem; margin-bottom: 1rem;
}

.notice {
    background-color: #EFEBF9; border-left: 3px solid #002CA6;
    padding: 1rem 1.25rem; font-size: 13px;
    line-height: 1.6; color: #1F2933; margin-top: 1rem;
}

.country-badge {
    display: inline-block;
    background: #002CA6; color: #fff;
    border-radius: 20px; padding: 0.2rem 0.75rem;
    font-size: 13px; font-weight: 600; margin-bottom: 0.5rem;
}

.visa-card {
    background-size: cover; background-position: center;
    background-repeat: no-repeat; border: 2px solid #E7D180;
    border-radius: 8px; overflow: hidden; transition: all 0.3s ease;
    cursor: pointer; min-height: 220px;
    display: flex; align-items: flex-end; position: relative;
}
.visa-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(to bottom, rgba(0,44,166,0) 40%, rgba(0,44,166,0.8) 100%);
    z-index: 1;
}
.visa-card:hover {
    border-color: #C80730;
    box-shadow: 0 4px 16px rgba(200,7,48,0.2);
    transform: translateY(-2px);
}
.visa-card-content { padding: 1.5rem; position: relative; z-index: 2; width: 100%; }
.visa-card-title   { font-size: 16px; font-weight: 700; color: #EFEBF9; margin: 0 0 0.5rem 0; }
.visa-card-desc    { font-size: 13px; color: #F0F0F0; line-height: 1.5; margin: 0; }

footer { visibility: hidden; }

/* ─── PROFESSIONAL RESULTS DESIGN ─────────────────────────────────────────── */

.results-container { 
    display: grid; 
    grid-template-columns: 1fr; 
    gap: 2rem; 
    margin-top: 2rem;
}

.verdict-banner {
    padding: 2rem;
    border-radius: 12px;
    border: 1px solid;
    background: linear-gradient(135deg, var(--bg-color), rgba(255,255,255,0.5));
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    animation: slideIn 0.5s ease-out;
}

.verdict-banner.eligible {
    --bg-color: #ECFDF5;
    --border-color: #059669;
    --title-color: #047857;
    --text-color: #065F46;
    border-color: var(--border-color);
}

.verdict-banner.warning {
    --bg-color: #FFFBF0;
    --border-color: #D97706;
    --title-color: #B45309;
    --text-color: #7C2D12;
    border-color: var(--border-color);
}

.verdict-banner.error {
    --bg-color: #FEE2E2;
    --border-color: #DC2626;
    --title-color: #B91C1C;
    --text-color: #7F1D1D;
    border-color: var(--border-color);
}

.verdict-badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    background-color: rgba(0,0,0,0.05);
    color: var(--title-color);
    margin-bottom: 1rem;
}

.verdict-title {
    font-size: 28px;
    font-weight: 800;
    color: var(--title-color);
    margin: 0.5rem 0 1rem 0;
    letter-spacing: -0.5px;
}

.verdict-summary {
    font-size: 15px;
    line-height: 1.8;
    color: var(--text-color);
    margin: 0;
}

/* Dashboard Grid */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.dashboard-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
}

.dashboard-card:hover {
    border-color: #002CA6;
    box-shadow: 0 4px 12px rgba(0,44,166,0.1);
    transform: translateY(-2px);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.card-icon {
    font-size: 24px;
    min-width: 24px;
}

.card-title {
    font-size: 14px;
    font-weight: 600;
    color: #4B5563;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.card-content {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.requirement-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem;
    background: #F9FAFB;
    border-radius: 6px;
    font-size: 13px;
}

.requirement-status {
    flex-shrink: 0;
    font-size: 16px;
    margin-top: 2px;
}

.requirement-text {
    color: #4B5563;
    line-height: 1.5;
}

/* Status Indicator */
.status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
}

.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
}

.status-dot.met {
    background-color: #059669;
}

.status-dot.missing {
    background-color: #DC2626;
}

.status-dot.unclear {
    background-color: #F59E0B;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Requirements Breakdown */
.requirements-section {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1.5rem;
}

.requirements-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 16px;
    font-weight: 700;
    color: #1F2933;
    margin-bottom: 1.25rem;
    border-bottom: 2px solid #E5E7EB;
    padding-bottom: 1rem;
}

.requirements-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.requirements-list li {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
    background: #F9FAFB;
    border-left: 3px solid #E5E7EB;
    border-radius: 4px;
    font-size: 13px;
    color: #4B5563;
    line-height: 1.6;
}

.requirements-list li::before {
    content: "•";
    font-size: 18px;
    font-weight: bold;
    color: #D97706;
    min-width: 1rem;
    margin-top: -2px;
}

/* Footer Note */
.footer-note {
    background: linear-gradient(135deg, #EFF6FF 0%, #F0EBFF 100%);
    border: 1px solid #93C5FD;
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 2rem;
    font-size: 13px;
    color: #1E3A8A;
    line-height: 1.7;
}

.footer-note strong {
    color: #002CA6;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ── HELPERS ────────────────────────────────────────────────────────────────────

def crop_image(image_path, target_width, target_height):
    try:
        img = Image.open(image_path)
        img_ratio    = img.width / img.height
        target_ratio = target_width / target_height
        if img_ratio > target_ratio:
            new_w = int(img.height * target_ratio)
            left  = (img.width - new_w) // 2
            img   = img.crop((left, 0, left + new_w, img.height))
        else:
            new_h = int(img.width / target_ratio)
            top   = (img.height - new_h) // 2
            img   = img.crop((0, top, img.width, top + new_h))
        return img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    except Exception:
        return None


def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def render_field(label, cfg, key):
    help_text = None
    if cfg.get("conditional_on"):
        parent    = cfg["conditional_on"]
        show_when = cfg.get("show_when")
        help_text = f"Only required if '{parent}' is '{show_when}'"

    if cfg["type"] == "text":
        return st.text_input(label, help=help_text, key=key)

    if cfg["type"] == "number":
        return st.number_input(label, min_value=0.0, help=help_text, key=key)

    if cfg["type"] == "date":
        if "birth" in label.lower():
            min_date = date(1924, 1, 1)
            max_date = date(2008, 12, 31)
            value    = date(2000, 1, 1)
        else:
            min_date = date.today()
            max_date = date(2030, 12, 31)
            value    = date.today()
        return st.date_input(
            label, value=value,
            min_value=min_date, max_value=max_date,
            help=help_text, key=key,
        )

    if cfg["type"] == "select":
        return st.selectbox(label, [""] + cfg["options"], help=help_text, key=key)


def parse_eligibility(text):
    lower = text.lower()
    for line in text.split("\n"):
        if line.lower().startswith("verdict:"):
            val = line.split(":", 1)[1].strip().lower()
            if "not eligible" in val:
                return "NOT ELIGIBLE", "error"
            if "eligible" in val:
                return "ELIGIBLE", "eligible"
            if "unclear" in val:
                return "NEEDS REVIEW", "warning"

    if "not eligible" in lower:
        return "NOT ELIGIBLE", "error"
    if "likely eligible" in lower or "appears eligible" in lower or "eligible" in lower:
        return "ELIGIBLE", "eligible"
    return "NEEDS REVIEW", "warning"


def extract_sections(text):
    sections = {"explanation": "", "missing_requirements": [], "additional_info": []}
    current  = None
    for line in text.split("\n"):
        ll = line.lower().strip()
        if not line.strip() or ll.startswith("verdict:"):
            continue
        if "explanation:" in ll:
            current = "explanation"
            sections["explanation"] = line.split(":", 1)[1].strip() if ":" in line else ""
        elif "missing requirements:" in ll:
            current = "missing_requirements"
        elif "additional information needed:" in ll:
            current = "additional_info"
        elif "eligibility summary:" in ll:
            current = "explanation"
            sections["explanation"] = line.split(":", 1)[1].strip() if ":" in line else ""
        elif current:
            clean = line.strip().lstrip("-•* ").strip()
            if clean:
                if current == "explanation":
                    sections["explanation"] += " " + clean
                else:
                    sections[current].append(clean)
    sections["explanation"] = sections["explanation"].strip()
    return sections


# ── SESSION STATE / RAG INIT ───────────────────────────────────────────────────

if "rag_instances" not in st.session_state:
    st.session_state.rag_instances = {}   # { country_code: SwiftVisaRAG }
if "ready" not in st.session_state:
    st.session_state.ready = True         # always ready; RAG loaded lazily per country


def get_rag(country_code: str) -> SwiftVisaRAG:
    """Return a cached RAG instance for the given country, creating it if needed."""
    if country_code not in st.session_state.rag_instances:
        st.session_state.rag_instances[country_code] = SwiftVisaRAG(country=country_code)
    return st.session_state.rag_instances[country_code]


# ── HEADER ─────────────────────────────────────────────────────────────────────

def render_header():
    header_img = crop_image("assets/header__image.png", 1600, 250)
    if header_img:
        st.image(header_img, use_container_width=True)

    st.markdown("<div class='main-title'>SwiftVisa</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Visa Eligibility Screening Tool</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="notice">
    This tool provides a preliminary eligibility assessment based on publicly available immigration policies.
    It does not constitute legal advice and does not guarantee visa approval. Always verify requirements
    using official government or immigration authority sources.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


render_header()


# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("**Eligibility Assessment**")
    st.markdown("")

    # ── Country selector ──
    country_options = list(SUPPORTED_COUNTRIES.keys())
    country_labels  = {
        c: f"{cfg['flag']} {cfg['display_name']}"
        for c, cfg in SUPPORTED_COUNTRIES.items()
    }

    selected_country = st.selectbox(
        "Destination country",
        [""] + country_options,
        format_func=lambda x: country_labels.get(x, "Select a country") if x else "Select a country",
        key="selected_country",
    )

    # ── Visa type selector (depends on country) ──
    visa_type = ""
    if selected_country:
        visa_types_for_country = get_visa_types_for_country(selected_country)
        visa_type = st.selectbox(
            "Visa type",
            [""] + visa_types_for_country,
            format_func=lambda x: (
                get_visa_display_name(selected_country, x) if x else "Select a visa type"
            ),
            key=f"visa_type_{selected_country}",
        )

    st.markdown("---")
    st.markdown("**Required Information**")
    st.markdown("""
- Passport details
- Travel dates
- Financial information
- Course / job documentation
    """)

    st.markdown("---")
    if selected_country:
        cfg = SUPPORTED_COUNTRIES[selected_country]
        authority_name = cfg.get("authority", cfg.get("display_name", "Official Immigration Authority"))
        official_url = cfg.get("official_portal", cfg.get("official_url", ""))
        language_test = cfg.get("language_test", cfg.get("language_label", "English Language Requirement Met"))

        st.markdown("**Official Portal**")
        st.markdown(f"[{authority_name}]({official_url})")
        st.markdown(f"Language test accepted: *{language_test}*")
        st.markdown("---")

    st.markdown("**About SwiftVisa**")
    st.markdown("""
SwiftVisa uses **RAG (Retrieval-Augmented Generation)** powered by Large Language Models
to provide accurate visa eligibility assessments based on real immigration policy data.

*Guidance only — not a substitute for official advice.*
    """)


# ── LANDING VIEW ───────────────────────────────────────────────────────────────

if not selected_country or not visa_type:
    if not selected_country:
        st.markdown("### Select a destination country to begin")
    else:
        country_cfg = SUPPORTED_COUNTRIES[selected_country]
        flag        = country_cfg["flag"]
        name        = country_cfg["display_name"]
        st.markdown(f"### {flag} {name} — Select a visa type to continue")

        # Show visa cards for the selected country
        visa_types = get_visa_types_for_country(selected_country)

        VISA_DESCRIPTIONS = {
            # UK
            "student":           "For applicants accepted to an educational institution",
            "graduate":          "For students who completed eligible studies and wish to remain",
            "skilled_worker":    "For skilled professionals with a confirmed job offer",
            "health_care_worker":"For healthcare professionals sponsored by a licensed employer",
            "visitor":           "For tourism, business or family visits",
            # Canada
            "student_permit":              "For international students accepted to a Canadian institution",
            "work_permit":                 "For skilled workers with job offers or Express Entry",
            "visitor_visa":                "For tourism, business, or family visits to Canada",
            "post_graduation_work_permit": "For graduates of Canadian institutions seeking post-study work",
            # Australia
            "student_visa_500":                "For international students enrolled in Australian institutions",
            "temporary_graduate_visa_485":     "For graduates seeking temporary work in Australia",
            "temporary_skill_shortage_visa_482":"For skilled workers in occupations with labor shortages",
            "visitor_visa_600":                "For tourism, business, or family visits to Australia",
            # New Zealand
            "student_visa":                   "For international students accepted to New Zealand institutions",
            "accredited_employer_work_visa":  "For skilled workers sponsored by accredited employers",
            "visitor_visa":                   "For tourism, business, or family visits to New Zealand",
            "post_study_work_visa":           "For graduates of New Zealand institutions seeking post-study work",
        }

        VISA_IMAGES = {
            "student":           "assets/student.png",
            "graduate":          "assets/graduate.png",
            "skilled_worker":    "assets/skilledworker.png",
            "health_care_worker":"assets/healthcare.png",
            "visitor":           "assets/standardvisitor.png",
            "student_permit":              "assets/student.png",
            "work_permit":                 "assets/skilledworker.png",
            "visitor_visa":                "assets/standardvisitor.png",
            "post_graduation_work_permit": "assets/graduate.png",
            "student_visa_500":                "assets/student.png",
            "temporary_graduate_visa_485":     "assets/graduate.png",
            "temporary_skill_shortage_visa_482":"assets/skilledworker.png",
            "visitor_visa_600":                "assets/standardvisitor.png",
            "student_visa":                   "assets/student.png",
            "accredited_employer_work_visa":  "assets/skilledworker.png",
            "post_study_work_visa":           "assets/graduate.png",
        }

        col1, col2 = st.columns(2)
        for idx, vt in enumerate(visa_types):
            col = col1 if idx % 2 == 0 else col2
            display_name = get_visa_display_name(selected_country, vt)
            description  = VISA_DESCRIPTIONS.get(vt, "")
            image_path   = VISA_IMAGES.get(vt, "")
            card_img     = crop_image(image_path, 400, 250)

            import base64
            from io import BytesIO
            if card_img:
                buf = BytesIO()
                card_img.save(buf, format="PNG")
                bg = f"url(data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()})"
            else:
                bg = "none"

            with col:
                st.markdown(f"""
                <div class="visa-card" style="background-image: {bg};">
                    <div class="visa-card-content">
                        <p class="visa-card-title">{display_name}</p>
                        <p class="visa-card-desc">{description}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")

    st.stop()


# ── APPLICATION FORM ───────────────────────────────────────────────────────────

country_cfg  = SUPPORTED_COUNTRIES[selected_country]
display_name = get_visa_display_name(selected_country, visa_type)

st.markdown(
    f"<div class='country-badge'>{country_cfg['flag']} {country_cfg['display_name']}</div>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<div class='section-title'>{display_name} Application</div>",
    unsafe_allow_html=True,
)
st.markdown("")

# ── Personal Information ──
st.markdown("<div class='subsection-title'>Personal Information</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
user_data   = {}
fields      = list(COMMON_FIELDS.items())
mid         = len(fields) // 2

with col1:
    for k, v in fields[:mid]:
        user_data[k] = render_field(k, v, f"common_{selected_country}_{k}")
with col2:
    for k, v in fields[mid:]:
        user_data[k] = render_field(k, v, f"common_{selected_country}_{k}")

# ── Visa-Specific Details ──
st.markdown("<div class='subsection-title'>Visa-Specific Details</div>", unsafe_allow_html=True)

try:
    vfields = get_visa_fields(selected_country, visa_type)
except KeyError as e:
    st.error(str(e))
    st.stop()

vlist   = list(vfields.items())
mid     = len(vlist) // 2
c1, c2  = st.columns(2)
col_idx = 0

for k, v in vlist:
    is_conditional = v.get("conditional_on") is not None
    if is_conditional:
        parent_val = user_data.get(v["conditional_on"])
        if parent_val != v.get("show_when"):
            continue

    current_col = c1 if col_idx < mid else c2
    with current_col:
        user_data[k] = render_field(k, v, f"{selected_country}_{visa_type}_{k}")
    col_idx += 1


# ── SUBMIT ─────────────────────────────────────────────────────────────────────

st.markdown("---")
submit = st.button("Evaluate eligibility", use_container_width=True, type="primary")

if submit:
    with st.spinner("Evaluating your eligibility..."):
        try:
            dob = user_data.get("Date of Birth")
            if dob and isinstance(dob, date):
                user_data["Calculated Age"] = calculate_age(dob)

            profile = {}
            for k, v in user_data.items():
                if v:
                    profile[k] = v.strftime("%Y-%m-%d") if isinstance(v, date) else str(v)

            rag    = get_rag(selected_country)
            result = rag.evaluate_eligibility(profile, visa_type)

        except (TimeoutError, ConnectionError) as e:
            st.error(f"⚠️ LM Studio Connection Issue: {str(e)}")
            st.info("""
**Troubleshooting:**
1. Make sure LM Studio is running
2. Check that the model 'llama-3.2-3b-instruct' is loaded
3. Verify the IP address in config.py is correct (currently: http://192.168.0.104:1234)
4. Check your network connection

**Current Configuration:**
- Base URL: http://192.168.0.104:1234/v1
- Model: llama-3.2-3b-instruct

Please verify these details match your LM Studio setup.
            """)
            import traceback
            with st.expander("Technical Details"):
                st.code(traceback.format_exc())
            st.stop()
        except Exception as e:
            st.error(f"Error during evaluation: {e}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
            st.stop()

    st.markdown("<div class='section-title'>Eligibility Assessment</div>", unsafe_allow_html=True)
    st.markdown("")

    status, cls = parse_eligibility(result["evaluation"])
    sections = extract_sections(result["evaluation"])

    # ── PROFESSIONAL VERDICT BANNER ────────────────────────────────────────
    verdict_mapping = {
        "ELIGIBLE": ("eligible", "✓ You Qualify", "Based on the information provided, you meet the requirements for this visa type. Proceed with confidence toward your application."),
        "NOT ELIGIBLE": ("error", "✗ Additional Requirements Needed", "You do not currently meet all the mandatory requirements. Review the missing requirements below and address them."),
        "NEEDS REVIEW": ("warning", "⚠ Needs Further Assessment", "Some requirements need clarification or additional documentation. See details below for specific information needed."),
    }
    
    banner_class, banner_title, banner_desc = verdict_mapping.get(status, ("warning", "⚠ Assessment Complete", sections.get('explanation', "")))

    st.markdown(f"""
    <div class="verdict-banner {banner_class}">
        <div class="verdict-badge">ASSESSMENT RESULT</div>
        <div class="verdict-title">{banner_title}</div>
        <div class="verdict-summary">{banner_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KEY INFORMATION CARDS ──────────────────────────────────────────────
    st.markdown("")
    
    country_cfg = SUPPORTED_COUNTRIES.get(selected_country, {})
    flag = country_cfg.get("flag", "")
    display_name = country_cfg.get("display_name", selected_country)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-header">
                <div class="card-icon">🌍</div>
                <div class="card-title">Destination</div>
            </div>
            <div style="font-size: 18px; font-weight: 700; color: #002CA6;">
                {flag} {display_name}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        visa_display = visa_type.replace('_', ' ').title()
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-header">
                <div class="card-icon">📋</div>
                <div class="card-title">Visa Type</div>
            </div>
            <div style="font-size: 18px; font-weight: 700; color: #002CA6;">
                {visa_display}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status_colors = {"ELIGIBLE": "#059669", "NOT ELIGIBLE": "#DC2626", "NEEDS REVIEW": "#F59E0B"}
        status_icons = {"ELIGIBLE": "✓", "NOT ELIGIBLE": "✗", "NEEDS REVIEW": "!"}
        status_color = status_colors.get(status, "#4B5563")
        status_icon = status_icons.get(status, "?")
        
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <div class="card-title">Your Status</div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 24px; font-weight: 800; color: {status_color};">{status_icon}</span>
                <span style="font-size: 16px; font-weight: 700; color: {status_color};">{status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── REQUIREMENTS ANALYSIS ──────────────────────────────────────────────
    st.markdown("")
    
    if sections["missing_requirements"] or sections["additional_info"]:
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            if sections["missing_requirements"]:
                st.markdown(f"""
                <div class="requirements-section">
                    <div class="requirements-header">
                        <span>🚫</span>
                        <span>Missing/Unmet Requirements</span>
                    </div>
                    <ul class="requirements-list">
                """, unsafe_allow_html=True)
                
                for req in sections["missing_requirements"]:
                    st.markdown(f"""
                    <li>
                        {req}
                    </li>
                    """, unsafe_allow_html=True)
                
                st.markdown("</ul></div>", unsafe_allow_html=True)
        
        with col_right:
            if sections["additional_info"]:
                st.markdown(f"""
                <div class="requirements-section">
                    <div class="requirements-header">
                        <span>📝</span>
                        <span>Additional Information Needed</span>
                    </div>
                    <ul class="requirements-list">
                """, unsafe_allow_html=True)
                
                for info in sections["additional_info"]:
                    st.markdown(f"""
                    <li>
                        {info}
                    </li>
                    """, unsafe_allow_html=True)
                
                st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # ── ASSESSMENT SUMMARY ─────────────────────────────────────────────────
    st.markdown("")
    st.markdown(f"""
    <div class="requirements-section">
        <div class="requirements-header">
            <span>📋</span>
            <span>Assessment Summary</span>
        </div>
        <div style="font-size: 14px; line-height: 1.8; color: #4B5563; padding: 1rem;">
            {sections['explanation'] or "Based on the information you provided and official visa requirements, here is your eligibility assessment. Please review each section carefully and ensure all required documentation is prepared."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NEXT STEPS & RECOMMENDATIONS ────────────────────────────────────────
    st.markdown("")
    
    if status == "ELIGIBLE":
        next_steps_html = """
        <div class="requirements-section" style="border-left: 4px solid #059669;">
            <div class="requirements-header" style="color: #059669;">
                <span>✓</span>
                <span>Next Steps</span>
            </div>
            <ol style="margin: 0; padding-left: 1.5rem; color: #4B5563; font-size: 13px; line-height: 1.8;">
                <li style="margin-bottom: 0.75rem;"><strong>Prepare Documentation:</strong> Gather all required documents including passport, financial statements, and supporting letters.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Complete Application:</strong> Fill out the official application form from the immigration authority.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Submit Application:</strong> Submit your application through the official portal with all required documents.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Track Status:</strong> Monitor your application status through the official tracking system.</li>
            </ol>
        </div>
        """
    elif status == "NOT ELIGIBLE":
        next_steps_html = """
        <div class="requirements-section" style="border-left: 4px solid #DC2626;">
            <div class="requirements-header" style="color: #DC2626;">
                <span>✗</span>
                <span>Recommended Actions</span>
            </div>
            <ul style="margin: 0; padding-left: 1.5rem; color: #4B5563; font-size: 13px; line-height: 1.8;">
                <li style="margin-bottom: 0.75rem;"><strong>Address Missing Requirements:</strong> Work on fulfilling the unmet requirements listed above.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Improve Financial Position:</strong> If funds are insufficient, consider additional savings or financial support.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Seek Professional Advice:</strong> Consult with an immigration advisor for personalized guidance.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Reapply When Ready:</strong> Once requirements are met, you can reapply for the visa.</li>
            </ul>
        </div>
        """
    else:
        next_steps_html = """
        <div class="requirements-section" style="border-left: 4px solid #F59E0B;">
            <div class="requirements-header" style="color: #B45309;">
                <span>!</span>
                <span>What to Do Next</span>
            </div>
            <ul style="margin: 0; padding-left: 1.5rem; color: #4B5563; font-size: 13px; line-height: 1.8;">
                <li style="margin-bottom: 0.75rem;"><strong>Clarify Requirements:</strong> Provide additional information or documentation for items marked as unclear.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Contact Immigration Office:</strong> Reach out to clarify any ambiguous requirements.</li>
                <li style="margin-bottom: 0.75rem;"><strong>Verify Documents:</strong> Double-check that all supporting documents are valid and current.</li>
            </ul>
        </div>
        """
    
    st.markdown(next_steps_html, unsafe_allow_html=True)

    # ── IMPORTANT DISCLAIMER ───────────────────────────────────────────────
    official_url = country_cfg.get("official_portal", country_cfg.get("official_url", ""))
    authority_name = country_cfg.get("authority", country_cfg.get("display_name", "Official Immigration Authority"))
    
    st.markdown(f"""
    <div class="footer-note">
        <strong>⚠️ Important Disclaimer:</strong> This assessment is generated by an AI system based on publicly available information and your input. 
        It is <strong>not</strong> an official determination and does not guarantee visa approval or rejection. 
        For official decisions, always consult <a href="{official_url}" target="_blank"><strong>{authority_name}</strong></a> 
        or a qualified immigration advisor. Visa requirements and policies may change without notice.
    </div>
    """, unsafe_allow_html=True)

    # ── DETAILED ASSESSMENT (COLLAPSIBLE) ───────────────────────────────────
    st.markdown("")
    with st.expander("📄 View Full Assessment Details"):
        st.markdown("**Complete LLM Assessment:**")
        st.code(result["evaluation"], language="markdown")