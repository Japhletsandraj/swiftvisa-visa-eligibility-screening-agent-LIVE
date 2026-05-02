"""
SwiftVisa - Form Field Definitions
Defines all form fields for each visa type, per country.

Structure:
  COMMON_FIELDS           — shown for every country / visa combination
  <COUNTRY>_VISA_FIELDS   — dict keyed by that country's visa_type strings
  COUNTRY_VISA_FIELDS_MAP — top-level lookup: country_code → {visa_type → fields}
  VISA_DISPLAY_NAMES      — country_code → {visa_type → human label}
"""

# ── Common fields (all countries) ────────────────────────────────────────────

COMMON_FIELDS = {
    "Full Name": {"type": "text", "required": True},
    "Date of Birth": {"type": "date", "required": True},
    "Nationality": {"type": "text", "required": True},
    "Passport Number": {"type": "text", "required": True},
    "Email Address": {"type": "text", "required": True},
    "Phone Number": {"type": "text", "required": True},
    "Current Location": {"type": "text", "required": True},
    "Intended Travel Date": {"type": "date", "required": True},
    "Intended Length of Stay (months)": {"type": "number", "required": True},
    "Funds Available (local currency)": {"type": "number", "required": True},
    "Criminal History": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Previous Visa Refusal": {"type": "select", "options": ["Yes", "No"], "required": True},
}


# ══════════════════════════════════════════════════════════════════════════════
# UNITED KINGDOM
# ══════════════════════════════════════════════════════════════════════════════

UK_STUDENT_FIELDS = {
    "Has CAS (Confirmation of Acceptance)": {"type": "select", "options": ["Yes", "No"], "required": True},
    "CAS Reference Number": {"type": "text", "required": False, "conditional_on": "Has CAS (Confirmation of Acceptance)", "show_when": "Yes"},
    "Education Provider is Licensed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Course Level": {"type": "select", "options": ["Undergraduate", "Postgraduate", "PhD", "Foundation"], "required": True},
    "Course is Full-Time": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Course Start Date": {"type": "date", "required": True},
    "Course Duration (months)": {"type": "number", "required": True},
    "Meets Financial Requirement": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Funds Held for 28 Days": {"type": "select", "options": ["Yes", "No"], "required": True},
    "English Language Requirement Met": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Tuberculosis Test Results Available": {"type": "select", "options": ["Yes", "No"], "required": True},
    "ATAS Certificate Required": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "ATAS Certificate Provided": {"type": "select", "options": ["Yes", "No"], "required": False, "conditional_on": "ATAS Certificate Required", "show_when": "Yes"},
}

UK_GRADUATE_FIELDS = {
    "Currently in UK": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Current Visa Type": {"type": "select", "options": ["Student Visa", "Work Visa", "Other", "N/A"], "required": True},
    "Course Completed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Course Level Completed": {"type": "select", "options": ["Bachelor's", "Master's", "PhD"], "required": True},
    "Education Provider is Licensed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Provider Reported Completion to UKVI": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Original CAS Reference": {"type": "text", "required": False},
    "Student Visa Valid on Application Date": {"type": "select", "options": ["Yes", "No"], "required": True},
}

UK_SKILLED_WORKER_FIELDS = {
    "Job Offer Confirmed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Employer is Licensed Sponsor": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Certificate of Sponsorship Issued": {"type": "select", "options": ["Yes", "No"], "required": True},
    "CoS Reference Number": {"type": "text", "required": False, "conditional_on": "Certificate of Sponsorship Issued", "show_when": "Yes"},
    "Job Title": {"type": "text", "required": True},
    "SOC Code": {"type": "text", "required": False},
    "Job is Eligible Occupation": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Salary Offered (GBP)": {"type": "number", "required": True},
    "Meets Minimum Salary Threshold": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "English Language Requirement Met": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Criminal Record Certificate Required": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Criminal Record Certificate Provided": {"type": "select", "options": ["Yes", "No", "N/A"], "required": False, "conditional_on": "Criminal Record Certificate Required", "show_when": "Yes"},
}

UK_HEALTH_CARE_WORKER_FIELDS = {
    "Job Offer Confirmed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Employer is Licensed Healthcare Sponsor": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Certificate of Sponsorship Issued": {"type": "select", "options": ["Yes", "No"], "required": True},
    "CoS Reference Number": {"type": "text", "required": False, "conditional_on": "Certificate of Sponsorship Issued", "show_when": "Yes"},
    "Job Title": {"type": "text", "required": True},
    "SOC Code": {"type": "text", "required": False},
    "Job is Eligible Healthcare Role": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Salary Offered (GBP)": {"type": "number", "required": True},
    "Meets Healthcare Salary Rules": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "English Language Requirement Met": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Professional Registration Required": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Professional Registration Provided": {"type": "select", "options": ["Yes", "No", "N/A"], "required": False, "conditional_on": "Professional Registration Required", "show_when": "Yes"},
}

UK_VISITOR_FIELDS = {
    "Purpose of Visit": {"type": "select", "options": ["Tourism", "Business", "Family Visit", "Medical", "Other"], "required": True},
    "Purpose is Permitted Under Visitor Rules": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Stay Within 6 Months Limit": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Accommodation Arranged": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Return/Onward Travel Planned": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Intends to Leave After Visit": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Sufficient Funds for Stay": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Tuberculosis Test Results Available": {"type": "select", "options": ["Yes", "No", "N/A"], "required": True},
}

UK_VISA_FIELDS = {
    "student": UK_STUDENT_FIELDS,
    "graduate": UK_GRADUATE_FIELDS,
    "skilled_worker": UK_SKILLED_WORKER_FIELDS,
    "health_care_worker": UK_HEALTH_CARE_WORKER_FIELDS,
    "visitor": UK_VISITOR_FIELDS,
}

UK_VISA_DISPLAY_NAMES = {
    "student": "Student Visa",
    "graduate": "Graduate Visa",
    "skilled_worker": "Skilled Worker Visa",
    "health_care_worker": "Health & Care Worker Visa",
    "visitor": "Standard Visitor Visa",
}


# ══════════════════════════════════════════════════════════════════════════════
# CANADA
# ══════════════════════════════════════════════════════════════════════════════

CA_STUDENT_PERMIT_FIELDS = {
    "Acceptance Letter from DLI": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Institution Name": {"type": "text", "required": True},
    "Institution is a DLI": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Program Level": {"type": "select", "options": ["Certificate", "Diploma", "Bachelor's", "Master's", "PhD", "Language Course"], "required": True},
    "Program is Full-Time": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Program Start Date": {"type": "date", "required": True},
    "Program Duration (months)": {"type": "number", "required": True},
    "Language Requirement Met (English or French)": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Proof of Financial Support": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Funds Cover Tuition + Living (CAD)": {"type": "number", "required": True},
    "Province of Study": {"type": "select", "options": ["Ontario", "British Columbia", "Quebec", "Alberta", "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick", "Other"], "required": True},
    "Quebec Acceptance Certificate (CAQ) if Quebec": {"type": "select", "options": ["Yes", "No", "N/A"], "required": False, "conditional_on": "Province of Study", "show_when": "Quebec"},
    "Biometrics Provided": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical Exam Completed": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
}

CA_WORK_PERMIT_FIELDS = {
    "Job Offer Confirmed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "LMIA Required": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "LMIA Approved": {"type": "select", "options": ["Yes", "No", "N/A"], "required": False, "conditional_on": "LMIA Required", "show_when": "Yes"},
    "LMIA Number": {"type": "text", "required": False, "conditional_on": "LMIA Required", "show_when": "Yes"},
    "Job Title": {"type": "text", "required": True},
    "NOC Code": {"type": "text", "required": False},
    "TEER Category": {"type": "select", "options": ["TEER 0", "TEER 1", "TEER 2", "TEER 3", "TEER 4", "TEER 5", "Not Sure"], "required": True},
    "Salary Offered (CAD/year)": {"type": "number", "required": True},
    "Language Requirement Met (English or French)": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Employer Province": {"type": "select", "options": ["Ontario", "British Columbia", "Quebec", "Alberta", "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick", "Other"], "required": True},
    "Biometrics Provided": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical Exam Completed": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
}

CA_EXPRESS_ENTRY_FIELDS = {
    "Express Entry Pool": {"type": "select", "options": ["Federal Skilled Worker", "Canadian Experience Class", "Federal Skilled Trades", "Not Sure"], "required": True},
    "CRS Score (if known)": {"type": "number", "required": False},
    "Years of Skilled Work Experience": {"type": "number", "required": True},
    "Work Experience is in Canada": {"type": "select", "options": ["Yes", "No", "Partial"], "required": True},
    "Job Title": {"type": "text", "required": True},
    "NOC Code": {"type": "text", "required": False},
    "TEER Category": {"type": "select", "options": ["TEER 0", "TEER 1", "TEER 2", "TEER 3", "TEER 4", "TEER 5", "Not Sure"], "required": True},
    "Educational Credential Assessment (ECA) Completed": {"type": "select", "options": ["Yes", "No", "In Progress"], "required": True},
    "Language Test Taken": {"type": "select", "options": ["IELTS General", "CELPIP", "TEF Canada", "TCF Canada", "Not Yet"], "required": True},
    "CLB Level Achieved": {"type": "select", "options": ["CLB 4", "CLB 5", "CLB 6", "CLB 7", "CLB 8", "CLB 9", "CLB 10+", "Not Sure"], "required": True},
    "Provincial Nomination": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Province Nominating": {"type": "select", "options": ["Ontario", "British Columbia", "Alberta", "Quebec", "Other", "N/A"], "required": False, "conditional_on": "Provincial Nomination", "show_when": "Yes"},
    "Valid Job Offer in Canada": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Proof of Settlement Funds": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Biometrics Provided": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical Exam Completed": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
}

CA_VISITOR_VISA_FIELDS = {
    "Purpose of Visit": {"type": "select", "options": ["Tourism", "Family Visit", "Business", "Medical", "Transit", "Other"], "required": True},
    "eTA or Visa Required": {"type": "select", "options": ["eTA", "Visitor Visa (TRV)", "Visa-Exempt", "Not Sure"], "required": True},
    "Stay Within 6 Months Limit": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Proof of Ties to Home Country": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Sufficient Funds for Stay": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Return/Onward Travel Planned": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Biometrics Provided": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical Exam Completed": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
}

CA_PGWP_FIELDS = {
    "Canadian Study Permit Held": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Program Completed at DLI": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Program Duration (months)": {"type": "number", "required": True},
    "Program Level Completed": {"type": "select", "options": ["Certificate (8+ months)", "Diploma", "Bachelor's", "Master's", "PhD"], "required": True},
    "Transcript / Completion Letter Available": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Applying Within 180 Days of Graduation": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Currently in Canada": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Language Requirement Met (English or French)": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Biometrics Provided": {"type": "select", "options": ["Yes", "No"], "required": True},
}

CA_VISA_FIELDS = {
    "student_permit": CA_STUDENT_PERMIT_FIELDS,
    "work_permit": CA_WORK_PERMIT_FIELDS,
    "express_entry": CA_EXPRESS_ENTRY_FIELDS,
    "visitor_visa": CA_VISITOR_VISA_FIELDS,
    "post_graduation_work_permit": CA_PGWP_FIELDS,
}

CA_VISA_DISPLAY_NAMES = {
    "student_permit": "Student Permit",
    "work_permit": "Work Permit",
    "express_entry": "Express Entry (Permanent Residence)",
    "visitor_visa": "Visitor Visa / eTA",
    "post_graduation_work_permit": "Post-Graduation Work Permit (PGWP)",
}


# ══════════════════════════════════════════════════════════════════════════════
# AUSTRALIA
# ══════════════════════════════════════════════════════════════════════════════

AU_STUDENT_500_FIELDS = {
    "CoE (Confirmation of Enrolment) Issued": {"type": "select", "options": ["Yes", "No"], "required": True},
    "CoE Reference Number": {"type": "text", "required": False, "conditional_on": "CoE (Confirmation of Enrolment) Issued", "show_when": "Yes"},
    "Provider is CRICOS-Registered": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Course Level": {"type": "select", "options": ["ELICOS", "School", "Vocational (VET)", "Higher Education", "Postgraduate", "PhD", "Foundation"], "required": True},
    "Course Start Date": {"type": "date", "required": True},
    "Course Duration (months)": {"type": "number", "required": True},
    "English Proficiency (IELTS/PTE/TOEFL)": {"type": "select", "options": ["IELTS 5.5+", "PTE 42+", "TOEFL iBT 46+", "Cambridge 162+", "Not Yet Tested", "Exempt"], "required": True},
    "Genuine Temporary Entrant (GTE) Statement Ready": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Overseas Student Health Cover (OSHC) Arranged": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Financial Capacity Demonstrated": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Funds Cover Tuition + Living (AUD)": {"type": "number", "required": True},
    "Biometrics Provided": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Health Assessment Completed": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Character Assessment / Police Clearance": {"type": "select", "options": ["Yes", "No"], "required": True},
}

AU_GRAD_485_FIELDS = {
    "Currently in Australia": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Australian Study Requirement Met": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Qualification CRICOS-Registered": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Course Level Completed": {"type": "select", "options": ["Bachelor's", "Graduate Diploma", "Master's", "PhD"], "required": True},
    "Applying Within 6 Months of Graduation": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Stream Applying Under": {"type": "select", "options": ["Graduate Work Stream", "Post-Study Work Stream"], "required": True},
    "Nominated Occupation (Graduate Work Stream)": {"type": "text", "required": False, "conditional_on": "Stream Applying Under", "show_when": "Graduate Work Stream"},
    "Skills Assessment Completed (Graduate Work Stream)": {"type": "select", "options": ["Yes", "No", "N/A"], "required": False, "conditional_on": "Stream Applying Under", "show_when": "Graduate Work Stream"},
    "English Proficiency (IELTS/PTE)": {"type": "select", "options": ["IELTS 6.0+", "PTE 50+", "TOEFL iBT 64+", "Cambridge 169+", "Not Yet Tested"], "required": True},
    "Overseas Health Cover / Medicare Eligibility": {"type": "select", "options": ["Medicare Eligible", "OVHC Arranged", "Neither"], "required": True},
    "Health Assessment Completed": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Character Assessment / Police Clearance": {"type": "select", "options": ["Yes", "No"], "required": True},
}

AU_SKILLED_190_FIELDS = {
    "State/Territory Nomination Received": {"type": "select", "options": ["Yes", "No", "Applied"], "required": True},
    "Nominating State/Territory": {"type": "select", "options": ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT", "Not Yet"], "required": True},
    "Occupation on State Skilled Occupation List": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Job Title": {"type": "text", "required": True},
    "ANZSCO Code": {"type": "text", "required": False},
    "Skills Assessment Completed": {"type": "select", "options": ["Yes", "No", "In Progress"], "required": True},
    "Assessing Authority": {"type": "text", "required": False},
    "Points Score (Estimated)": {"type": "number", "required": False},
    "Age Band": {"type": "select", "options": ["18–24", "25–32", "33–39", "40–44", "45+"], "required": True},
    "English Proficiency": {"type": "select", "options": ["Competent (IELTS 6+)", "Proficient (IELTS 7+)", "Superior (IELTS 8+)", "Not Yet Tested"], "required": True},
    "Overseas Work Experience (years)": {"type": "number", "required": True},
    "Australian Work Experience (years)": {"type": "number", "required": True},
    "Australian Study Completed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Health Assessment Completed": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Character Assessment / Police Clearance": {"type": "select", "options": ["Yes", "No"], "required": True},
}

AU_TSS_482_FIELDS = {
    "Job Offer Confirmed": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Employer is Approved Sponsor": {"type": "select", "options": ["Yes", "No", "In Progress"], "required": True},
    "Nomination Lodged by Employer": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Job Title": {"type": "text", "required": True},
    "ANZSCO Code": {"type": "text", "required": False},
    "Occupation on MLTSSL or STSOL": {"type": "select", "options": ["MLTSSL (Medium/Long-term)", "STSOL (Short-term)", "Not Sure"], "required": True},
    "Stream": {"type": "select", "options": ["Short-Term (2 yrs)", "Medium-Term (4 yrs)", "Labour Agreement"], "required": True},
    "Salary Meets TSMIT (AUD 73,150+)": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Salary Offered (AUD/year)": {"type": "number", "required": True},
    "Skills Assessment Required": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Skills Assessment Completed": {"type": "select", "options": ["Yes", "No", "N/A"], "required": False, "conditional_on": "Skills Assessment Required", "show_when": "Yes"},
    "Years of Relevant Work Experience": {"type": "number", "required": True},
    "English Proficiency (IELTS/PTE)": {"type": "select", "options": ["IELTS 5.0+", "PTE 36+", "TOEFL iBT 35+", "Exempt"], "required": True},
    "Health Assessment Completed": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Character Assessment / Police Clearance": {"type": "select", "options": ["Yes", "No"], "required": True},
}

AU_VISITOR_600_FIELDS = {
    "Stream": {"type": "select", "options": ["Tourist Stream", "Business Visitor Stream", "Sponsored Family Stream", "ADS Stream"], "required": True},
    "Purpose of Visit": {"type": "select", "options": ["Tourism", "Family Visit", "Business", "Medical", "Transit", "Other"], "required": True},
    "Stay Within 3–12 Month Limit": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Genuine Temporary Entrant": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Sufficient Funds for Stay": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Return/Onward Travel Planned": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Health Assessment Completed": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
    "Character Assessment / Police Clearance": {"type": "select", "options": ["Yes", "No"], "required": True},
}

AU_VISA_FIELDS = {
    "student_visa_500": AU_STUDENT_500_FIELDS,
    "temporary_graduate_visa_485": AU_GRAD_485_FIELDS,
    "skilled_nominated_visa_190": AU_SKILLED_190_FIELDS,
    "temporary_skill_shortage_visa_482": AU_TSS_482_FIELDS,
    "visitor_visa_600": AU_VISITOR_600_FIELDS,
}

AU_VISA_DISPLAY_NAMES = {
    "student_visa_500": "Student Visa (Subclass 500)",
    "temporary_graduate_visa_485": "Temporary Graduate Visa (Subclass 485)",
    "skilled_nominated_visa_190": "Skilled Nominated Visa (Subclass 190)",
    "temporary_skill_shortage_visa_482": "Temporary Skill Shortage Visa (Subclass 482)",
    "visitor_visa_600": "Visitor Visa (Subclass 600)",
}


# ══════════════════════════════════════════════════════════════════════════════
# NEW ZEALAND
# ══════════════════════════════════════════════════════════════════════════════

NZ_STUDENT_VISA_FIELDS = {
    "Offer of Place from NZQA-Approved Provider": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Institution Name": {"type": "text", "required": True},
    "Course Level (NZQF)": {"type": "select", "options": ["Level 1–3 Certificate", "Level 4–6 Diploma", "Bachelor's (Level 7)", "Master's (Level 9)", "PhD (Level 10)"], "required": True},
    "Course is Full-Time": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Course Start Date": {"type": "date", "required": True},
    "Course Duration (months)": {"type": "number", "required": True},
    "English Language Requirement Met": {"type": "select", "options": ["Yes", "No", "Exempt"], "required": True},
    "Proof of Financial Support": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Funds Cover Fees + Living (NZD)": {"type": "number", "required": True},
    "Genuine Intention to Study": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical and X-Ray Certificates": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
    "Police Certificate": {"type": "select", "options": ["Yes", "No"], "required": True},
}

NZ_POST_STUDY_WORK_FIELDS = {
    "NZ Student Visa Held": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Study Completed at NZQA Provider": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Course Level Completed": {"type": "select", "options": ["Bachelor's", "Graduate Diploma", "Master's", "PhD"], "required": True},
    "Study Location": {"type": "select", "options": ["Auckland", "Other Region", "Not Sure"], "required": True},
    "Course Duration Was 30+ Weeks": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Applying Within 3 Months of Visa Expiry": {"type": "select", "options": ["Yes", "No"], "required": True},
    "English Language Requirement Met": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical and X-Ray Certificates": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
    "Police Certificate": {"type": "select", "options": ["Yes", "No"], "required": True},
}

NZ_SKILLED_MIGRANT_FIELDS = {
    "Expression of Interest (EOI) Submitted": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Points Score (Estimated)": {"type": "number", "required": False},
    "Job Offer in NZ": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Job Title": {"type": "text", "required": True},
    "ANZSCO Code": {"type": "text", "required": False},
    "Age Band": {"type": "select", "options": ["20–39", "40–44", "45–49", "50–55", "56+"], "required": True},
    "Qualification Level": {"type": "select", "options": ["NZ Qualification or Recognised Overseas Equivalent", "Bachelor's", "Master's", "PhD"], "required": True},
    "Years of Skilled Work Experience": {"type": "number", "required": True},
    "NZ Work Experience (years)": {"type": "number", "required": True},
    "English Language Requirement Met": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Health and Character Requirements Met": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Medical and X-Ray Certificates": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
    "Police Certificate": {"type": "select", "options": ["Yes", "No"], "required": True},
}

NZ_AEWV_FIELDS = {
    "Job Offer from Accredited Employer": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Employer Accreditation Status": {"type": "select", "options": ["Standard Accreditation", "High-volume Accreditation", "Franchisee Accreditation", "Not Sure"], "required": True},
    "Job Check Completed by Employer": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Job Token Number": {"type": "text", "required": False, "conditional_on": "Job Check Completed by Employer", "show_when": "Yes"},
    "Job Title": {"type": "text", "required": True},
    "ANZSCO Code": {"type": "text", "required": False},
    "Salary Meets Median Wage Threshold (NZD 29.66/hr+)": {"type": "select", "options": ["Yes", "No", "Not Sure"], "required": True},
    "Salary Offered (NZD/year)": {"type": "number", "required": True},
    "English Language Requirement Met": {"type": "select", "options": ["Yes", "No", "Exempt"], "required": True},
    "Settlement Funds Available (NZD 4,200)": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical and X-Ray Certificates": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
    "Police Certificate": {"type": "select", "options": ["Yes", "No"], "required": True},
}

NZ_VISITOR_VISA_FIELDS = {
    "Purpose of Visit": {"type": "select", "options": ["Tourism", "Family Visit", "Business", "Medical", "Other"], "required": True},
    "Visa or NZeTA Required": {"type": "select", "options": ["Visitor Visa", "NZeTA", "Visa-Free", "Not Sure"], "required": True},
    "Stay Within 9 Months in 18 Month Period": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Sufficient Funds for Stay": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Return/Onward Travel Planned": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Genuine Intention to Leave": {"type": "select", "options": ["Yes", "No"], "required": True},
    "Medical and X-Ray Certificates": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
    "Police Certificate": {"type": "select", "options": ["Yes", "No", "Not Required"], "required": True},
}

NZ_VISA_FIELDS = {
    "student_visa": NZ_STUDENT_VISA_FIELDS,
    "post_study_work_visa": NZ_POST_STUDY_WORK_FIELDS,
    "skilled_migrant_category": NZ_SKILLED_MIGRANT_FIELDS,
    "accredited_employer_work_visa": NZ_AEWV_FIELDS,
    "visitor_visa": NZ_VISITOR_VISA_FIELDS,
}

NZ_VISA_DISPLAY_NAMES = {
    "student_visa": "Student Visa",
    "post_study_work_visa": "Post Study Work Visa",
    "skilled_migrant_category": "Skilled Migrant Category Resident Visa",
    "accredited_employer_work_visa": "Accredited Employer Work Visa (AEWV)",
    "visitor_visa": "Visitor Visa",
}


# ══════════════════════════════════════════════════════════════════════════════
# TOP-LEVEL LOOKUP MAPS
# ══════════════════════════════════════════════════════════════════════════════

COUNTRY_VISA_FIELDS_MAP = {
    "uk": UK_VISA_FIELDS,
    "canada": CA_VISA_FIELDS,
    "australia": AU_VISA_FIELDS,
    "new_zealand": NZ_VISA_FIELDS,
}

COUNTRY_VISA_DISPLAY_NAMES = {
    "uk": UK_VISA_DISPLAY_NAMES,
    "canada": CA_VISA_DISPLAY_NAMES,
    "australia": AU_VISA_DISPLAY_NAMES,
    "new_zealand": NZ_VISA_DISPLAY_NAMES,
}


# ── Legacy aliases (keeps any code importing the old names working) ────────────

VISA_FIELDS_MAP = UK_VISA_FIELDS
VISA_DISPLAY_NAMES = UK_VISA_DISPLAY_NAMES


# ── Convenience helpers ───────────────────────────────────────────────────────

def get_visa_fields(country_code: str, visa_type: str) -> dict:
    """Return field config for a given country + visa type."""
    return COUNTRY_VISA_FIELDS_MAP.get(country_code, {}).get(visa_type, {})


def get_visa_display_name(country_code: str, visa_type: str) -> str:
    """Return human-readable label for a visa type."""
    return COUNTRY_VISA_DISPLAY_NAMES.get(country_code, {}).get(visa_type, visa_type)


def get_all_visa_display_names(country_code: str) -> dict:
    """Return {visa_type: display_name} for a country."""
    return COUNTRY_VISA_DISPLAY_NAMES.get(country_code, {})