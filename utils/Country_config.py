"""
SwiftVisa - Country Configuration
Defines supported countries, their visa types, official sources, and metadata.

Selected countries have structured, official immigration portals comparable to UK GOV.UK:
  - Canada  → canada.ca/IRCC    (clear eligibility rules, defined categories, searchable docs)
  - Australia → homeaffairs.gov.au (subclass-based system, well-documented eligibility)
  - New Zealand → immigration.govt.nz (INZ portal, structured criteria per visa type)
"""

SUPPORTED_COUNTRIES = {
    "uk": {
        "display_name": "United Kingdom",
        "flag": "🇬🇧",
        "official_portal": "https://www.gov.uk/browse/visas-immigration",
        "authority": "UK Visas and Immigration (UKVI)",
        "data_dir": "uk",
        "vectorstore_subdir": "uk",
        "currency": "GBP",
        "currency_symbol": "£",
        "visa_types": ["student", "graduate", "skilled_worker", "health_care_worker", "visitor"],
        "language_test": "IELTS / UKVI-approved test",
    },
    "canada": {
        "display_name": "Canada",
        "flag": "🇨🇦",
        "official_portal": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
        "authority": "Immigration, Refugees and Citizenship Canada (IRCC)",
        "data_dir": "canada",
        "vectorstore_subdir": "canada",
        "currency": "CAD",
        "currency_symbol": "CA$",
        "visa_types": ["student_permit", "work_permit", "visitor_visa", "post_graduation_work_permit"],
        "language_test": "IELTS / CELPIP / TEF (for French)",
    },
    "australia": {
        "display_name": "Australia",
        "flag": "🇦🇺",
        "official_portal": "https://immi.homeaffairs.gov.au",
        "authority": "Department of Home Affairs",
        "data_dir": "australia",
        "vectorstore_subdir": "australia",
        "currency": "AUD",
        "currency_symbol": "AU$",
        "visa_types": ["student_visa_500", "temporary_graduate_visa_485", "temporary_skill_shortage_visa_482", "visitor_visa_600"],
        "language_test": "IELTS / TOEFL / PTE Academic / Cambridge C1",
    },
    "new_zealand": {
        "display_name": "New Zealand",
        "flag": "🇳🇿",
        "official_portal": "https://www.immigration.govt.nz/visas",
        "authority": "Immigration New Zealand (INZ)",
        "data_dir": "new_zealand",
        "vectorstore_subdir": "new_zealand",
        "currency": "NZD",
        "currency_symbol": "NZ$",
        "visa_types": ["student_visa", "accredited_employer_work_visa", "visitor_visa", "post_study_work_visa"],
        "language_test": "IELTS / PTE Academic / TOEFL iBT / Cambridge C1",
    },
}

# Maps (country, visa_type) → display name shown in the UI
VISA_DISPLAY_NAMES_BY_COUNTRY = {
    # ---------- United Kingdom ----------
    ("uk", "student"):           "Student Visa",
    ("uk", "graduate"):          "Graduate Visa",
    ("uk", "skilled_worker"):    "Skilled Worker Visa",
    ("uk", "health_care_worker"):"Health & Care Worker Visa",
    ("uk", "visitor"):           "Standard Visitor Visa",

    # ---------- Canada ----------
    ("canada", "student_permit"):              "Study Permit",
    ("canada", "work_permit"):                 "Work Permit",
    ("canada", "visitor_visa"):                "Visitor Visa (TRV)",
    ("canada", "post_graduation_work_permit"): "Post-Graduation Work Permit (PGWP)",

    # ---------- Australia ----------
    ("australia", "student_visa_500"):                "Student Visa (Subclass 500)",
    ("australia", "temporary_graduate_visa_485"):     "Temporary Graduate Visa (Subclass 485)",
    ("australia", "temporary_skill_shortage_visa_482"): "Temporary Skill Shortage Visa (Subclass 482)",
    ("australia", "visitor_visa_600"):                "Visitor Visa (Subclass 600)",

    # ---------- New Zealand ----------
    ("new_zealand", "student_visa"):                   "Student Visa",
    ("new_zealand", "accredited_employer_work_visa"):  "Accredited Employer Work Visa (AEWV)",
    ("new_zealand", "visitor_visa"):                   "Visitor Visa",
    ("new_zealand", "post_study_work_visa"):           "Post Study Work Visa",
}


def get_country_config(country_code: str) -> dict:
    """Return config dict for a country, or raise KeyError if unsupported."""
    if country_code not in SUPPORTED_COUNTRIES:
        raise KeyError(f"Country '{country_code}' is not supported. "
                       f"Supported: {list(SUPPORTED_COUNTRIES.keys())}")
    return SUPPORTED_COUNTRIES[country_code]


def get_visa_display_name(country_code: str, visa_type: str) -> str:
    key = (country_code, visa_type)
    return VISA_DISPLAY_NAMES_BY_COUNTRY.get(key, visa_type.replace("_", " ").title())


def get_visa_types_for_country(country_code: str) -> list:
    return SUPPORTED_COUNTRIES[country_code]["visa_types"]


def get_vectorstore_path(country_code: str, base_path: str = "vectorstore") -> str:
    subdir = SUPPORTED_COUNTRIES[country_code]["vectorstore_subdir"]
    return f"{base_path}/{subdir}/faiss_index"


def get_data_dir(country_code: str, base_data_path: str = "KB") -> str:
    data_dir = SUPPORTED_COUNTRIES[country_code]["data_dir"]
    return f"{base_data_path}/{data_dir}"


def get_all_country_codes() -> list:
    return list(SUPPORTED_COUNTRIES.keys())
# Alias used by build_vectorstore.py and rag_pipeline.py
COUNTRY_CONFIG = SUPPORTED_COUNTRIES