"""One-off generator for the CareerPilot demo job catalog (UK-focused)."""
import json
from collections import Counter
from pathlib import Path

OUT = Path("backend/data/demo_jobs.json")

SYNTHETIC = "Synthetic demo value; not an employer claim"


def J(job_id, title, company, location, category, experience_level, work_mode, employment_type,
      salary, description, requirements, responsibilities, required_skills, preferred_skills,
      sponsorship=None, eligibility=None, deadline=None, education=None, experience=None):
    return {
        "job_id": job_id,
        "title": title,
        "company": company,
        "location": location,
        "employment_type": employment_type,
        "salary": salary,
        "deadline": deadline,
        "source_url": f"https://demo.careerpilot.local/jobs/{job_id}",
        "description": description,
        "requirements": requirements,
        "responsibilities": responsibilities,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "eligibility": eligibility or "Demo listing; verify eligibility with the employer.",
        "sponsorship_information": sponsorship,
        "education": education,
        "experience": experience,
        "provenance": {
            "source_url": f"https://demo.careerpilot.local/jobs/{job_id}",
            "source_name": "CareerPilot demo dataset",
            "salary_source": SYNTHETIC,
            "deadline_source": "Synthetic demo deadline; not an employer claim" if deadline else None,
            "requirements_source": SYNTHETIC,
            "sponsorship_source": SYNTHETIC if sponsorship else None,
        },
        "category": category,
        "experience_level": experience_level,
        "work_mode": work_mode,
        "source_domain": "demo.careerpilot.local",
    }


jobs = []

jobs.append(J("demo-data-001", "Graduate Data Analyst", "Northstar Analytics (Demo)", "London, United Kingdom",
    "DATA", "GRADUATE", "HYBRID", "Full-time", "GBP 30,000-35,000",
    "Support reporting and analysis for product and client teams in a growing London analytics consultancy.",
    ["Bachelor's degree in a quantitative discipline", "0-2 years of analytical experience"],
    ["Build recurring reports", "Explain trends to stakeholders", "Support ad-hoc data requests"],
    ["SQL", "Excel", "Python"], ["Power BI", "Tableau"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Bachelor's degree (or equivalent) in a quantitative or STEM discipline.",
    experience="0-2 years; internships and placement years count.", deadline="2026-10-31",
    eligibility="Open to UK graduates; verification of right to work required."))

jobs.append(J("demo-data-002", "Junior Data Scientist", "Blue Cedar Labs (Demo)", "Edinburgh, United Kingdom",
    "DATA", "GRADUATE", "HYBRID", "Full-time", "GBP 31,000-36,000",
    "Develop experiments and models for customer behaviour insights in a Scottish data science studio.",
    ["Degree in computer science, statistics, or a related field", "Experience with applied analysis"],
    ["Prepare datasets", "Evaluate model performance", "Communicate findings to product teams"],
    ["Python", "SQL", "Machine learning"], ["scikit-learn", "Cloud platforms"],
    sponsorship="Candidates must have the right to work in the UK; we do not sponsor for this role.",
    education="Degree in computer science, statistics, mathematics, or a related field.",
    experience="0-2 years; university research or project work is relevant.", deadline="2026-11-15"))

jobs.append(J("demo-data-005", "Business Intelligence Analyst", "Harbor Metrics (Demo)", "Bristol, United Kingdom",
    "DATA", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Turn operational and customer data into BI dashboards for a Bristol-based retail analytics studio.",
    ["Degree in business, economics, or a related field", "Strong written communication"],
    ["Maintain BI dashboards", "Analyse campaign and sales data", "Document reporting logic"],
    ["SQL", "Excel", "Data visualisation"], ["Power BI", "Python"],
    education="Degree in a business, economics, or quantitative discipline.",
    experience="0-2 years of business analysis or reporting experience.", deadline="2026-12-01"))
jobs.append(J("demo-data-008", "Product Data Intern", "Signal Grove (Demo)", "Remote - United Kingdom",
    "DATA", "INTERNSHIP", "REMOTE", "Internship (12 weeks)", "GBP 24,000 pro-rata",
    "Support a remote analytics team with data quality checks, experimentation tracking, and analysis.",
    ["Currently studying a quantitative or STEM degree (penultimate or final year)"],
    ["Maintain experiment logs", "Clean and validate datasets", "Summarise weekly product metrics"],
    ["SQL", "Excel", "Python"], ["A/B testing", "Git"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Currently studying a quantitative or STEM degree (penultimate or final year).",
    experience="No prior work experience required.", deadline="2027-01-15",
    eligibility="Open to current students eligible to work in the UK."))

jobs.append(J("demo-data-010", "Research Data Assistant", "Prairie Insights (Demo)", "Sheffield, United Kingdom",
    "DATA", "ENTRY_LEVEL", "ON_SITE", "Full-time", None,
    "Assist a market research team with survey data preparation, cleaning, and summary reporting.",
    ["Degree in any discipline with strong numeracy", "Careful attention to detail"],
    ["Prepare survey datasets", "Run quality checks", "Produce summary tables and charts"],
    ["Excel", "SQL", "Data analysis"], ["SPSS", "R"],
    sponsorship="Candidates must have the right to work in the UK; we do not sponsor for this role.",
    education="Any degree with demonstrable numeracy.", experience="Entry level; graduate and placement experience welcome.",
    deadline="2026-11-30"))

jobs.append(J("demo-data-012", "Data Platform Associate", "Lakehouse Works (Demo)", "Glasgow, United Kingdom",
    "DATA", "GRADUATE", "HYBRID", "Full-time", "GBP 29,000-34,000",
    "Help maintain and grow the data platform behind a fast-moving Scottish analytics firm.",
    ["Degree in computer science or a related field", "Database fundamentals"],
    ["Maintain documentation", "Support data pipelines", "Triage platform alerts"],
    ["SQL", "Python", "Git"], ["dbt", "Airflow", "AWS"],
    sponsorship="We will sponsor eligible candidates for this role.",
    education="Degree in computer science or a closely related field.",
    experience="0-2 years or strong placement/project evidence.", deadline="2026-12-15"))
jobs.append(J("demo-uk-data-016", "Graduate Data Analyst", "Thameswick Analytics (Demo)", "London, United Kingdom",
    "DATA", "GRADUATE", "HYBRID", "Full-time", "GBP 30,000-35,000",
    "Join a Thames-side analytics team turning client data into decisions across finance and retail.",
    ["Degree in a quantitative or STEM discipline", "Comfortable working with SQL and spreadsheets"],
    ["Build recurring reporting", "Support ad-hoc data requests", "Present insights to non-technical stakeholders"],
    ["SQL", "Excel", "Python"], ["Power BI", "Tableau"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in a quantitative or STEM discipline.",
    experience="0-2 years; internships and placement years count.", deadline="2026-10-15"))

jobs.append(J("demo-uk-data-020", "Data Science Intern", "London Insight Labs (Demo)", "London, United Kingdom",
    "DATA", "INTERNSHIP", "ON_SITE", "Internship (10 weeks)", "GBP 23,500 pro-rata",
    "A summer internship on a data science team working on recommendation and forecasting models.",
    ["Currently studying computer science, data science, or a related field"],
    ["Clean datasets", "Run experiments", "Present findings to the lab"],
    ["Python", "SQL", "Machine learning"], ["scikit-learn", "pandas"],
    sponsorship="Sponsorship will be considered on a case-by-case basis for strong candidates.",
    education="Currently studying a quantitative or STEM degree.",
    experience="No prior work experience required; academic projects are relevant.", deadline="2027-02-01"))

jobs.append(J("demo-uk-data-021", "Graduate Data Engineer", "Northern Fintech Co. (Demo)", "Leeds, United Kingdom",
    "DATA", "GRADUATE", "HYBRID", "Full-time", "GBP 30,000-35,000",
    "Build and maintain the data pipelines behind a Leeds-based fintech's analytics platform.",
    ["Degree in computer science or a related field", "Experience with SQL and Python"],
    ["Build and monitor pipelines", "Maintain the data warehouse schema", "Document data lineage"],
    ["Python", "SQL", "Git"], ["dbt", "Airflow", "Snowflake"],
    sponsorship="We will sponsor eligible candidates.",
    education="Degree in computer science or a related technical field.",
    experience="0-2 years; placement and project evidence welcome.", deadline="2026-11-30"))
jobs.append(J("demo-uk-data-022", "Junior Data Scientist - Healthcare", "Edinburgh Health Analytics (Demo)", "Edinburgh, United Kingdom",
    "DATA", "GRADUATE", "ON_SITE", "Full-time", "GBP 31,000-36,000",
    "Analyse anonymised health data to improve service planning for public-sector healthcare partners.",
    ["Degree in statistics, data science, or a related field", "Familiarity with healthcare data and governance"],
    ["Build predictive models", "Run analysis on anonymised datasets", "Present to non-technical clinical stakeholders"],
    ["Python", "SQL", "Statistics"], ["R", "Machine learning", "Data governance"],
    education="Degree in statistics, data science, mathematics, or a related field.",
    experience="0-2 years; academic research on health/medical data is relevant.", deadline="2026-12-10"))

jobs.append(J("demo-uk-data-023", "Graduate Data Analyst", "Manchester Tech Analytics (Demo)", "Manchester, United Kingdom",
    "DATA", "GRADUATE", "HYBRID", "Full-time", "GBP 28,000-33,000",
    "Support data analysis and reporting for a growing Manchester fintech and its client teams.",
    ["Degree in a quantitative or STEM discipline", "Comfortable working with SQL and spreadsheets"],
    ["Build recurring reporting", "Support ad-hoc data requests", "Document analysis methods"],
    ["SQL", "Excel", "Python"], ["Power BI", "Tableau"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in a quantitative or STEM discipline.",
    experience="0-2 years; internships and placement years count.", deadline="2026-11-15"))

jobs.append(J("demo-uk-data-024", "Junior Data Analyst", "Birmingham Consulting Partners (Demo)", "Birmingham, United Kingdom",
    "DATA", "GRADUATE", "ON_SITE", "Full-time", "GBP 26,000-31,000",
    "Support business intelligence and data reporting for Midlands client projects.",
    ["Degree in business, economics, or a related field", "Strong written communication"],
    ["Prepare client-ready analysis", "Support project delivery", "Maintain internal BI dashboards"],
    ["SQL", "Excel", "Data analysis"], ["Power BI", "Python"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in business, economics, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-01"))
# ------------------------------------------------------------------ IT_SOFTWARE (9)
jobs.append(J("demo-tech-003", "Software Engineer, New Grad", "Maple Stack (Demo)", "Cambridge, United Kingdom",
    "IT_SOFTWARE", "GRADUATE", "HYBRID", "Full-time", "GBP 32,000-38,000",
    "Build reliable web services for a Cambridge developer-platform company alongside a supportive engineering team.",
    ["Computer science degree or equivalent experience", "Strong programming fundamentals"],
    ["Ship backend features", "Write and review tests", "Participate in design reviews"],
    ["Python", "TypeScript", "Git", "SQL"], ["React", "Docker", "AWS"],
    sponsorship="We will sponsor eligible candidates.",
    education="Computer science degree or equivalent practical experience.",
    experience="0-2 years; final-year project evidence welcome.", deadline="2026-10-20"))

jobs.append(J("demo-tech-004", "Backend Developer", "Orbit Commerce (Demo)", "Bristol, United Kingdom",
    "IT_SOFTWARE", "GRADUATE", "HYBRID", "Full-time", "GBP 29,000-35,000",
    "Develop APIs and integrations for an e-commerce platform serving independent UK retailers.",
    ["Degree in computer science or related field", "Working knowledge of at least one backend language"],
    ["Build REST APIs", "Debug production issues", "Improve API test coverage"],
    ["Python", "SQL", "Git"], ["PostgreSQL", "Redis", "Docker"],
    education="Degree in computer science or a related field.",
    experience="0-2 years; strong project portfolio acceptable.", deadline="2026-11-05"))

jobs.append(J("demo-tech-006", "Frontend Engineer", "Pinecone Studio (Demo)", "Manchester, United Kingdom",
    "IT_SOFTWARE", "GRADUATE", "HYBRID", "Full-time", "GBP 28,000-33,000",
    "Build accessible, fast customer-facing interfaces for a Manchester digital product studio.",
    ["Degree in computer science or related field", "Strong HTML/CSS/JavaScript fundamentals"],
    ["Implement UI components", "Fix accessibility issues", "Collaborate with designers"],
    ["JavaScript", "React", "HTML/CSS"], ["TypeScript", "Tailwind CSS", "Figma"],
    sponsorship="Candidates must have the right to work in the UK; we do not sponsor for this role.",
    education="Degree in computer science or a related field, or equivalent portfolio.",
    experience="0-2 years; personal projects count.", deadline="2026-12-05"))
jobs.append(J("demo-cloud-007", "Cloud Operations Associate", "Summit Systems (Demo)", "Glasgow, United Kingdom",
    "IT_SOFTWARE", "ENTRY_LEVEL", "ON_SITE", "Full-time", "GBP 26,000-30,000",
    "Monitor and support cloud infrastructure for public and private sector customers of a Scottish systems firm.",
    ["Technical degree or equivalent infrastructure experience", "Interest in Linux and networking"],
    ["Monitor platform health", "Triage incidents", "Maintain runbooks"],
    ["Linux", "Networking", "Bash"], ["AWS", "Terraform", "Docker"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Technical degree, apprenticeship, or equivalent hands-on experience.",
    experience="Entry level; placements and lab work welcome.", deadline="2026-11-20"))

jobs.append(J("demo-tech-009", "QA Automation Engineer", "Clearpath Software (Demo)", "Leeds, United Kingdom",
    "IT_SOFTWARE", "GRADUATE", "ON_SITE", "Full-time", "GBP 27,000-32,000",
    "Automate regression testing for a Leeds software house serving logistics customers.",
    ["Degree in computer science or a related field", "Familiarity with software testing concepts"],
    ["Write automated test suites", "Maintain test environments", "Report quality metrics"],
    ["Python", "Selenium", "Git"], ["Playwright", "CI/CD", "SQL"],
    education="Degree in computer science or a related field.",
    experience="0-2 years; testing coursework and projects welcome.", deadline="2026-12-12"))

jobs.append(J("demo-tech-011", "Full Stack Developer", "Redwood Digital (Demo)", "London, United Kingdom",
    "IT_SOFTWARE", "GRADUATE", "HYBRID", "Full-time", "GBP 32,000-38,000",
    "Deliver end-to-end features across frontend and backend for a London digital agency's client portfolio.",
    ["Degree in computer science or a related field", "Experience building web applications"],
    ["Deliver full-stack features", "Write automated tests", "Support client demos"],
    ["JavaScript", "React", "Node.js", "SQL"], ["TypeScript", "PostgreSQL", "Docker"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in computer science or a related field.",
    experience="0-2 years; portfolio projects are strong evidence.", deadline="2026-11-01"))
jobs.append(J("demo-tech-013", "Mobile Software Developer", "Northwind Apps (Demo)", "Nottingham, United Kingdom",
    "IT_SOFTWARE", "GRADUATE", "REMOTE", "Full-time", "GBP 27,000-33,000",
    "Build cross-platform mobile apps for a remote-first Nottingham application studio.",
    ["Degree in computer science or a related field", "Fundamentals of mobile development"],
    ["Implement mobile features", "Write unit tests", "Triage app store feedback"],
    ["JavaScript", "React Native", "Git"], ["iOS", "Android", "Figma"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in computer science or a related field.",
    experience="0-2 years; app projects and hackathons welcome.", deadline="2026-11-25"))

jobs.append(J("demo-tech-015", "Software Engineering Co-op", "Vector Harbor (Demo)", "Cambridge, United Kingdom",
    "IT_SOFTWARE", "PLACEMENT", "ON_SITE", "Fixed Term (12 months)", "GBP 25,000",
    "A 12-month industrial placement on a data-engineering team that regularly converts to a graduate offer.",
    ["Penultimate-year computer science or related degree", "Academic exposure to programming"],
    ["Support platform migrations", "Automate internal tooling", "Shadow senior engineers"],
    ["Python", "Git", "SQL"], ["TypeScript", "Docker"],
    education="Penultimate-year computer science or related degree.",
    experience="Placement year; prior work experience not required.", deadline="2027-01-10"))

jobs.append(J("demo-uk-it-017", "Junior Software Developer", "Nottingham Forge Systems (Demo)", "Nottingham, United Kingdom",
    "IT_SOFTWARE", "GRADUATE", "ON_SITE", "Full-time", "GBP 26,000-31,000",
    "Develop business systems for manufacturing clients of a long-established Nottingham software house.",
    ["Degree in computer science or equivalent experience", "Working knowledge of a backend language"],
    ["Build business modules", "Fix bugs with senior review", "Document APIs"],
    ["Java", "SQL", "Git"], ["Spring", "JavaScript", "Docker"],
    sponsorship="We will sponsor eligible candidates.",
    education="Degree in computer science or equivalent experience.",
    experience="0-2 years; placement and project evidence welcome.", deadline="2026-10-31"))
# ------------------------------------------------------------------ BUSINESS (8)
jobs.append(J("demo-uk-biz-018", "Graduate Business Analyst", "Birmingham Consulting Partners (Demo)", "Birmingham, United Kingdom",
    "BUSINESS", "GRADUATE", "ON_SITE", "Full-time", "GBP 27,000-32,000",
    "Work on client projects capturing requirements and turning business problems into deliverable solutions.",
    ["Degree in business, economics, or a related field", "Strong analytical and written communication"],
    ["Capture requirements", "Facilitate workshops", "Produce process documentation"],
    ["Excel", "Stakeholder management", "Data analysis"],
    ["SQL", "Power BI", "Visio"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in business, economics, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-11-10"))

jobs.append(J("demo-uk-biz-025", "Graduate Business Analyst", "Humber Business Group (Demo)", "Leeds, United Kingdom",
    "BUSINESS", "GRADUATE", "HYBRID", "Full-time", "GBP 27,000-32,000",
    "Support process improvement and systems projects for Yorkshire-based industrial clients.",
    ["Degree in business, management, or a related field", "Confident working with spreadsheets"],
    ["Map current processes", "Run requirements sessions", "Support testing and rollout"],
    ["Excel", "Process mapping", "Communication"],
    ["SQL", "Power BI", "Jira"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in business, management, or a related field.",
    experience="0-2 years; internships and placement years count.", deadline="2026-11-28"))

jobs.append(J("demo-uk-biz-026", "Junior Business Operations Analyst", "Trent Mercantile Co. (Demo)", "Nottingham, United Kingdom",
    "BUSINESS", "GRADUATE", "ON_SITE", "Full-time", "GBP 25,000-30,000",
    "Analyses trading and operations data for a Nottingham merchant business to support daily decisions.",
    ["Degree in business, economics, or a related field", "High numeracy"],
    ["Prepare margin reports", "Track KPIs", "Support budgeting cycles"],
    ["Excel", "Data analysis", "Attention to detail"],
    ["SQL", "Power BI", "SAP"],
    sponsorship=None,
    education="Degree in business, economics, accounting, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-08"))
jobs.append(J("demo-uk-biz-027", "Graduate Strategy Analyst", "Clyde & Merrick Consultants (Demo)", "Glasgow, United Kingdom",
    "BUSINESS", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Support strategy and market analysis for Scottish public and private sector organisations.",
    ["Degree in economics, business, or a related field", "Clear written communication"],
    ["Research markets", "Build financial models", "Support board-level presentations"],
    ["Excel", "Financial modelling", "Research"],
    ["Python", "Power BI", "SQL"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in economics, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-15"))

jobs.append(J("demo-uk-biz-028", "Business Graduate Programme", "Avon & Lang (Demo)", "Bristol, United Kingdom",
    "BUSINESS", "GRADUATE", "HYBRID", "Graduate scheme (24 months)", "GBP 28,000-33,000",
    "Rotate through commercial, operations, and project teams in a Bristol business services firm.",
    ["Degree in any discipline", "Strong communication and initiative"],
    ["Complete three six-month rotations", "Own a commercial workstream", "Present outcomes to leadership"],
    ["Excel", "Communication", "Problem solving"],
    ["SQL", "Power BI", "Project management"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in any discipline (2:1 or equivalent).",
    experience="Graduate entry; internships welcome.", deadline="2027-01-08"))

jobs.append(J("demo-uk-biz-029", "Sales Operations Analyst", "Peak District Retail Group (Demo)", "Sheffield, United Kingdom",
    "BUSINESS", "GRADUATE", "ON_SITE", "Full-time", "GBP 25,000-29,000",
    "Analyse sales performance and support the retail planning cycle for a Sheffield-based retail group.",
    ["Degree in business, marketing, or a related field", "Comfortable with spreadsheets"],
    ["Maintain sales dashboards", "Analyse promotions", "Support monthly reviews"],
    ["Excel", "Data analysis", "Retail KPIs"],
    ["Power BI", "SQL", "Tableau"],
    sponsorship=None,
    education="Degree in business, marketing, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-11-20"))
jobs.append(J("demo-uk-biz-030", "Commercial Graduate Analyst", "Caledonian Ventures (Demo)", "Edinburgh, United Kingdom",
    "BUSINESS", "GRADUATE", "ON_SITE", "Full-time", "GBP 27,000-32,000",
    "Support valuation and market analysis for the investment team of an Edinburgh venture firm.",
    ["Degree in business, finance, or economics", "Strong numeracy"],
    ["Prepare company research", "Build valuation models", "Track portfolio metrics"],
    ["Excel", "Financial modelling", "Research"],
    ["SQL", "Power BI", "Python"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in business, finance, or economics.",
    experience="0-2 years; placement years count.", deadline="2026-12-20"))

jobs.append(J("demo-uk-biz-031", "Business Insights Assistant", "Fenland Consumer Group (Demo)", "Cambridge, United Kingdom",
    "BUSINESS", "ENTRY_LEVEL", "HYBRID", "Full-time", "GBP 26,000-30,000",
    "Support consumer research and insights reporting for a Cambridge consumer goods group.",
    ["Degree in any discipline with strong research skills", "Excellent organisation"],
    ["Clean survey data", "Prepare insight summaries", "Maintain research libraries"],
    ["Excel", "Data analysis", "Written communication"],
    ["SPSS", "Power BI", "Python"],
    sponsorship="Candidates must have the right to work in the UK; we do not sponsor for this role.",
    education="Degree in any discipline with demonstrable research skills.",
    experience="Entry level; placement and internship experience welcome.", deadline="2027-01-15"))
# ------------------------------------------------------------------ HR (8)
jobs.append(J("demo-uk-hr-019", "HR Graduate Scheme Associate", "Manchester People Group (Demo)", "Manchester, United Kingdom",
    "HR", "GRADUATE", "ON_SITE", "Graduate scheme (18 months)", "GBP 26,000-30,000",
    "Rotate across recruitment, employee relations, and people analytics in a Manchester HR services firm.",
    ["Degree in any discipline", "An interest in people and employment practices"],
    ["Support recruitment campaigns", "Assist with onboarding", "Prepare people dashboards"],
    ["Communication", "Excel", "Attention to detail"],
    ["HR systems", "Data analysis", "Employment law awareness"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in any discipline (2:1 or equivalent).",
    experience="Graduate entry; internships welcome.", deadline="2026-11-10"))

jobs.append(J("demo-uk-hr-032", "HR Assistant (Graduate)", "Thames People Partners (Demo)", "London, United Kingdom",
    "HR", "GRADUATE", "HYBRID", "Full-time", "GBP 28,000-32,000",
    "Provide HR operational support across recruitment, contracts, and employee records for a London firm.",
    ["Degree in HR, business, or a related field", "High attention to detail"],
    ["Maintain employee records", "Support recruitment processes", "Respond to employee queries"],
    ["Communication", "Excel", "Organisation"],
    ["HR systems", "Employment law awareness"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in HR, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-11-25"))

jobs.append(J("demo-uk-hr-033", "Graduate Talent Acquisition Associate", "Northbridge People (Demo)", "Leeds, United Kingdom",
    "HR", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-30,000",
    "Support end-to-end graduate and early-career recruitment for a Yorkshire professional services firm.",
    ["Degree in any discipline", "Strong interpersonal skills"],
    ["Screen applications", "Coordinate interview days", "Analyse hiring funnel data"],
    ["Communication", "Excel", "Organisation"],
    ["ATS", "Data analysis", "Social recruiting"],
    sponsorship=None,
    education="Degree in any discipline.",
    experience="0-2 years; internships and placement years count.", deadline="2026-12-05"))
jobs.append(J("demo-uk-hr-034", "People Operations Graduate", "Caledonia People Group (Demo)", "Edinburgh, United Kingdom",
    "HR", "GRADUATE", "ON_SITE", "Full-time", "GBP 26,000-31,000",
    "Support employee lifecycle operations from onboarding to performance review cycles in a Scottish services firm.",
    ["Degree in HR, business, or a related field", "Organised and discreet"],
    ["Manage onboarding", "Maintain HRIS records", "Support performance review cycles"],
    ["Communication", "HRIS", "Excel"],
    ["Data protection awareness", "Employment law awareness"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in HR, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-12"))

jobs.append(J("demo-uk-hr-035", "HR Data & Systems Assistant", "Midlands People Services (Demo)", "Birmingham, United Kingdom",
    "HR", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-30,000",
    "Keep HR systems and people data accurate across a multi-site Midlands employer.",
    ["Degree in any discipline", "Comfortable with spreadsheets and systems"],
    ["Maintain HRIS data", "Produce monthly headcount reports", "Support system upgrades"],
    ["Excel", "Data analysis", "Attention to detail"],
    ["SQL", "Power BI", "HRIS"],
    sponsorship=None,
    education="Degree in any discipline.",
    experience="0-2 years; placement and internship welcome."))

jobs.append(J("demo-uk-hr-036", "Learning & Development Graduate", "Severn People Consultancy (Demo)", "Bristol, United Kingdom",
    "HR", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-31,000",
    "Support the design and delivery of training programmes for a Bristol people consultancy's clients.",
    ["Degree in any discipline", "Strong facilitation and writing skills"],
    ["Design learning materials", "Coordinate training events", "Evaluate feedback surveys"],
    ["Communication", "Course design", "Excel"],
    ["LMS", "Power BI", "Survey tools"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in any discipline.",
    experience="0-2 years; internships welcome.", deadline="2026-11-30"))
jobs.append(J("demo-uk-hr-037", "HR Graduate Internship", "Clyde People Co. (Demo)", "Glasgow, United Kingdom",
    "HR", "INTERNSHIP", "HYBRID", "Internship (12 weeks)", "GBP 24,000 pro-rata",
    "A summer internship supporting the full HR lifecycle for a Glasgow people-services firm.",
    ["Currently studying HR, business, or a related degree"],
    ["Support recruitment admin", "Update employee records", "Help prepare HR reports"],
    ["Communication", "Excel", "Organisation"],
    ["HRIS", "Data analysis"],
    sponsorship=None,
    education="Currently studying HR, business, or a related degree.",
    experience="No prior work experience required.", deadline="2027-02-15"))

jobs.append(J("demo-uk-hr-038", "People Analytics Assistant", "Riverside People Data (Demo)", "Nottingham, United Kingdom",
    "HR", "ENTRY_LEVEL", "HYBRID", "Full-time", "GBP 25,000-29,000",
    "Turn people data into reports that guide hiring, retention, and engagement decisions.",
    ["Degree in any discipline with strong numeracy", "Comfortable analysing datasets"],
    ["Prepare people dashboards", "Clean HR datasets", "Answer ad-hoc data requests"],
    ["Excel", "SQL", "Data analysis"],
    ["Power BI", "Python"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in any discipline with demonstrable numeracy.",
    experience="Entry level; placement and internship experience welcome.", deadline="2026-12-01"))
# ------------------------------------------------------------------ FINANCE (8)
jobs.append(J("demo-uk-fin-039", "Graduate Financial Analyst", "Avonbrook Asset Management (Demo)", "Bristol, United Kingdom",
    "FINANCE", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-34,000",
    "Support fund performance reporting and investment research for a Bristol asset manager.",
    ["Degree in finance, economics, accounting, or a related field", "Strong Excel skills"],
    ["Prepare fund reports", "Run performance calculations", "Support investment research"],
    ["Excel", "Financial analysis", "Attention to detail"],
    ["Bloomberg", "Python", "SQL"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in finance, economics, accounting, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-11-18"))

jobs.append(J("demo-uk-fin-040", "Finance Graduate Scheme", "Calder & Wade Finance (Demo)", "London, United Kingdom",
    "FINANCE", "GRADUATE", "HYBRID", "Graduate scheme (24 months)", "GBP 30,000-36,000",
    "Rotate across corporate finance, risk, and client reporting in a London financial services firm.",
    ["Degree in any discipline with strong numeracy", "Interest in financial markets"],
    ["Rotate across finance teams", "Support financial reporting", "Obtain professional qualifications (e.g., CIMA/CFA Pathway)"],
    ["Excel", "Financial analysis", "Communication"],
    ["SQL", "Power BI", "Python"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in any discipline with demonstrable numeracy (2:1 or equivalent).",
    experience="Graduate entry; internships welcome.", deadline="2026-11-05"))

jobs.append(J("demo-uk-fin-041", "Graduate Risk Analyst", "Pennine Risk Partners (Demo)", "Leeds, United Kingdom",
    "FINANCE", "GRADUATE", "HYBRID", "Full-time", "GBP 27,000-32,000",
    "Support credit and operational risk reporting for a Leeds-based financial services group.",
    ["Degree in finance, economics, mathematics, or a related field", "Analytical mindset"],
    ["Prepare risk reports", "Monitor risk limits", "Support stress-testing exercises"],
    ["Excel", "Risk analysis", "Data analysis"],
    ["SQL", "Python", "Power BI"],
    sponsorship=None,
    education="Degree in finance, economics, mathematics, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-10"))
jobs.append(J("demo-uk-fin-042", "Treasury & Accounting Graduate", "Meridian Trust Bank (Demo)", "Edinburgh, United Kingdom",
    "FINANCE", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Support treasury operations and management accounting for a Scottish banking group.",
    ["Degree in accounting, finance, or a related field", "High attention to detail"],
    ["Prepare reconciliation reports", "Support cash flow forecasting", "Assist month-end close"],
    ["Excel", "Accounting", "Reconciliation"],
    ["SQL", "SAP", "Power BI"],
    sponsorship="We will sponsor eligible candidates.",
    education="Degree in accounting, finance, or a related field (or studying towards a professional qualification).",
    experience="0-2 years; placement years count.", deadline="2026-11-22"))

jobs.append(J("demo-uk-fin-043", "Credit Analyst (Graduate)", "Clyde Capital (Demo)", "Glasgow, United Kingdom",
    "FINANCE", "GRADUATE", "ON_SITE", "Full-time", "GBP 27,000-32,000",
    "Assess credit applications and support portfolio monitoring for a Glasgow commercial lender.",
    ["Degree in finance, economics, business, or a related field", "Strong analytical writing"],
    ["Prepare credit memos", "Monitor covenant compliance", "Support portfolio reviews"],
    ["Excel", "Financial analysis", "Written communication"],
    ["SQL", "Credit risk tools", "Power BI"],
    sponsorship=None,
    education="Degree in finance, economics, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-14"))

jobs.append(J("demo-uk-fin-044", "Finance Operations Graduate", "Welland Finance Group (Demo)", "Nottingham, United Kingdom",
    "FINANCE", "ENTRY_LEVEL", "HYBRID", "Full-time", "GBP 25,000-30,000",
    "Keep day-to-day finance operations running across billing, collections, and reporting.",
    ["Degree in any discipline with strong numeracy", "Organised and process-driven"],
    ["Process invoices and payments", "Reconcile accounts", "Support audit preparation"],
    ["Excel", "Accounting", "Attention to detail"],
    ["ERP", "SQL", "Power BI"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in any discipline with demonstrable numeracy.",
    experience="Entry level; placement and internship experience welcome.", deadline="2026-12-20"))
jobs.append(J("demo-uk-fin-045", "Banking Graduate Programme", "Trent Valley Bank (Demo)", "Birmingham, United Kingdom",
    "FINANCE", "GRADUATE", "HYBRID", "Graduate scheme (18 months)", "GBP 27,000-32,000",
    "Rotate across retail banking, credit, and finance operations for a Midlands bank.",
    ["Degree in any discipline", "Strong customer and numeracy skills"],
    ["Rotate across banking teams", "Support credit decisions", "Learn regulatory basics (SM&CR)"],
    ["Excel", "Communication", "Financial analysis"],
    ["SQL", "Power BI", "Risk awareness"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in any discipline (2:1 or equivalent).",
    experience="Graduate entry; internships welcome.", deadline="2026-12-05"))

jobs.append(J("demo-uk-fin-046", "Investment Operations Intern", "Sheffield Mercantile Finance (Demo)", "Sheffield, United Kingdom",
    "FINANCE", "INTERNSHIP", "HYBRID", "Internship (12 weeks)", "GBP 24,000 pro-rata",
    "A summer internship supporting investment operations, trade settlement, and client reporting.",
    ["Currently studying finance, economics, or a related degree"],
    ["Support trade confirmations", "Reconcile client statements", "Assist with KYC checks"],
    ["Excel", "Attention to detail", "Financial basics"],
    ["Bloomberg", "SQL"],
    sponsorship=None,
    education="Currently studying finance, economics, or a related degree.",
    experience="No prior work experience required.", deadline="2027-02-20"))
# ------------------------------------------------------------------ MARKETING (8)
jobs.append(J("demo-data-014", "Marketing Data Analyst", "Brightline Research (Demo)", "London, United Kingdom",
    "MARKETING", "GRADUATE", "HYBRID", "Full-time", "GBP 28,000-33,000",
    "Analyse campaign and brand performance to guide media spend for a London marketing research firm.",
    ["Degree in marketing, business, statistics, or a related field", "Comfortable with analytics tools"],
    ["Measure campaign performance", "Build marketing dashboards", "Run segmentation analyses"],
    ["Excel", "Data analysis", "Google Analytics"],
    ["SQL", "Power BI", "Python"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in marketing, business, statistics, or a related field.",
    experience="0-2 years; internships and placement years count.", deadline="2026-11-27"))

jobs.append(J("demo-uk-mkt-047", "Graduate Marketing Executive", "Thameside Marketing Co. (Demo)", "London, United Kingdom",
    "MARKETING", "GRADUATE", "ON_SITE", "Full-time", "GBP 27,000-32,000",
    "Support campaign planning, content coordination, and agency briefs for a London marketing company.",
    ["Degree in marketing, communications, or a related field", "Strong written communication"],
    ["Coordinate campaign assets", "Draft marketing copy", "Track campaign calendars"],
    ["Communication", "Content writing", "Organisation"],
    ["SEO", "Google Ads", "Canva"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in marketing, communications, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-11-12"))

jobs.append(J("demo-uk-mkt-048", "Junior Digital Marketing Analyst", "Northbank Digital (Demo)", "Manchester, United Kingdom",
    "MARKETING", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-31,000",
    "Measure paid media and website performance for a Manchester digital marketing agency.",
    ["Degree in marketing, business, or a related field", "Interest in digital channels"],
    ["Report on PPC performance", "Monitor website analytics", "Support A/B test readouts"],
    ["Excel", "Google Analytics", "Data analysis"],
    ["SQL", "Power BI", "GA4"],
    sponsorship=None,
    education="Degree in marketing, business, or a related field.",
    experience="0-2 years; internships welcome.", deadline="2026-12-08"))
jobs.append(J("demo-uk-mkt-049", "Marketing & Communications Graduate", "Yorkshire Made (Demo)", "Leeds, United Kingdom",
    "MARKETING", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-30,000",
    "Support brand campaigns and internal communications for a Yorkshire-based consumer brand.",
    ["Degree in marketing, communications, or a related field", "Creative and organised"],
    ["Draft brand content", "Coordinate photoshoots", "Measure campaign feedback"],
    ["Communication", "Content writing", "Organisation"],
    ["Canva", "SEO", "Google Analytics"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in marketing, communications, or a related field.",
    experience="0-2 years; placements welcome.", deadline="2026-11-30"))

jobs.append(J("demo-uk-mkt-050", "Social Media & Content Graduate", "Caledonian Media Group (Demo)", "Edinburgh, United Kingdom",
    "MARKETING", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-30,000",
    "Grow branded channels and produce content for a Scottish media group's portfolio.",
    ["Degree in marketing, media, or a related field", "Strong written and visual communication"],
    ["Plan content calendars", "Produce social posts", "Report channel performance"],
    ["Communication", "Content writing", "Canva"],
    ["Social media tools", "Google Analytics", "SEO"],
    sponsorship=None,
    education="Degree in marketing, media, or a related field.",
    experience="0-2 years; internships welcome.", deadline="2026-12-15"))

jobs.append(J("demo-uk-mkt-051", "Brand Marketing Assistant", "Midlands Retail Group (Demo)", "Birmingham, United Kingdom",
    "MARKETING", "GRADUATE", "ON_SITE", "Full-time", "GBP 25,000-29,000",
    "Support national retail brand campaigns, store signage, and promotional compliance.",
    ["Degree in marketing, business, or a related field", "Organised and detail-oriented"],
    ["Coordinate campaign rollouts", "Brief stores on promotions", "Track campaign assets"],
    ["Communication", "Organisation", "Excel"],
    ["Canva", "SEO", "Google Analytics"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in marketing, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-01"))
jobs.append(J("demo-uk-mkt-052", "Growth Marketing Intern", "Severn Startups (Demo)", "Bristol, United Kingdom",
    "MARKETING", "INTERNSHIP", "HYBRID", "Internship (12 weeks)", "GBP 23,500 pro-rata",
    "Run experiments across acquisition channels for a portfolio of Bristol startup clients.",
    ["Currently studying marketing, business, or a related degree"],
    ["Run channel experiments", "Monitor campaign metrics", "Document what worked"],
    ["Communication", "Excel", "Google Analytics"],
    ["SQL", "SEO", "Social media tools"],
    sponsorship=None,
    education="Currently studying marketing, business, or a related degree.",
    experience="No prior work experience required.", deadline="2027-02-10"))

jobs.append(J("demo-uk-mkt-053", "Campaign Analytics Assistant", "Clyde Media (Demo)", "Glasgow, United Kingdom",
    "MARKETING", "ENTRY_LEVEL", "HYBRID", "Full-time", "GBP 25,000-29,000",
    "Turn campaign results into clear reporting for a Glasgow media planning agency.",
    ["Degree in any discipline with strong numeracy", "Comfortable with analytics dashboards"],
    ["Compile campaign reports", "Refresh dashboards", "Answer data requests"],
    ["Excel", "Data analysis", "Google Analytics"],
    ["Power BI", "SQL"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in any discipline with demonstrable numeracy.",
    experience="Entry level; placement and internship experience welcome.", deadline="2027-01-18"))
# ------------------------------------------------------------------ OPERATIONS (8)
jobs.append(J("demo-uk-ops-054", "Graduate Operations Analyst", "Humber Logistics Group (Demo)", "Leeds, United Kingdom",
    "OPERATIONS", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-31,000",
    "Analyse delivery performance and support fleet planning for a Yorkshire logistics operator.",
    ["Degree in any discipline with strong numeracy", "Comfortable with data and spreadsheets"],
    ["Model delivery routes", "Report on-time performance", "Support cost analysis"],
    ["Excel", "Data analysis", "Problem solving"],
    ["SQL", "Power BI", "Python"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in any discipline with demonstrable numeracy.",
    experience="0-2 years; placement years count.", deadline="2026-11-24"))

jobs.append(J("demo-uk-ops-055", "Supply Chain Graduate", "Trent Distribution Co. (Demo)", "Nottingham, United Kingdom",
    "OPERATIONS", "GRADUATE", "ON_SITE", "Full-time", "GBP 26,000-30,000",
    "Support planning, purchasing, and stock control across a Midlands distribution business.",
    ["Degree in business, logistics, or a related field", "Organised and analytical"],
    ["Plan stock replenishment", "Track supplier performance", "Support continuous improvement"],
    ["Excel", "Supply chain basics", "Communication"],
    ["SQL", "ERP", "Power BI"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in business, logistics, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-03"))

jobs.append(J("demo-uk-ops-056", "Operations Graduate Programme", "Caledonian Rail Services (Demo)", "Glasgow, United Kingdom",
    "OPERATIONS", "GRADUATE", "ON_SITE", "Graduate scheme (18 months)", "GBP 27,000-31,000",
    "Rotate across scheduling, customer operations, and performance teams for a Scottish rail services firm.",
    ["Degree in any discipline", "Interest in service operations"],
    ["Rotate across operations teams", "Support performance reporting", "Help with incident reviews"],
    ["Excel", "Communication", "Problem solving"],
    ["Power BI", "SQL", "Lean basics"],
    sponsorship=None,
    education="Degree in any discipline (2:1 or equivalent).",
    experience="Graduate entry; internships welcome.", deadline="2026-12-12"))
jobs.append(J("demo-uk-ops-057", "Junior Procurement Analyst", "Pennine Procurement Partners (Demo)", "Sheffield, United Kingdom",
    "OPERATIONS", "ENTRY_LEVEL", "ON_SITE", "Full-time", "GBP 25,000-29,000",
    "Support category sourcing and spend analysis for a Sheffield-based procurement consultancy.",
    ["Degree in any discipline", "Strong spreadsheet skills"],
    ["Analyse spend data", "Prepare tender documentation", "Support supplier reviews"],
    ["Excel", "Data analysis", "Communication"],
    ["SQL", "Power BI", "e-Procurement tools"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in any discipline.",
    experience="Entry level; placement and internship experience welcome.", deadline="2026-12-18"))

jobs.append(J("demo-uk-ops-058", "Service Operations Graduate", "Thames Health Operations (Demo)", "London, United Kingdom",
    "OPERATIONS", "GRADUATE", "ON_SITE", "Full-time", "GBP 29,000-34,000",
    "Support service improvement projects within the operations team of a health services provider.",
    ["Degree in any discipline", "Interest in service improvement and public sector"],
    ["Support improvement projects", "Collect service metrics", "Prepare board reports"],
    ["Excel", "Communication", "Problem solving"],
    ["Power BI", "SQL", "Lean/improvement methods"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in any discipline.",
    experience="0-2 years; placements welcome.", deadline="2026-12-20"))

jobs.append(J("demo-uk-ops-059", "Warehouse & Logistics Graduate", "Manchester Freight Group (Demo)", "Manchester, United Kingdom",
    "OPERATIONS", "GRADUATE", "ON_SITE", "Full-time", "GBP 26,000-30,000",
    "Support inbound, outbound, and transport planning for a large Manchester freight operation.",
    ["Degree in any discipline", "Practical and organised"],
    ["Plan transport schedules", "Track warehouse KPIs", "Support shift handovers"],
    ["Excel", "Communication", "Problem solving"],
    ["WMS", "ERP", "Power BI"],
    sponsorship=None,
    education="Degree in any discipline.",
    experience="0-2 years; placement years count.", deadline="2026-11-15"))
jobs.append(J("demo-uk-ops-060", "Project Operations Assistant", "Birmingham Facilities Group (Demo)", "Birmingham, United Kingdom",
    "OPERATIONS", "GRADUATE", "HYBRID", "Full-time", "GBP 26,000-30,000",
    "Support project coordination and facilities service delivery for a Birmingham estates firm.",
    ["Degree in any discipline", "Organised and proactive"],
    ["Coordinate project schedules", "Track service requests", "Maintain project logs"],
    ["Excel", "Communication", "Organisation"],
    ["Project management", "Power BI", "SQL"],
    sponsorship=None,
    education="Degree in any discipline.",
    experience="0-2 years; placement years count.", deadline="2027-01-05"))

jobs.append(J("demo-uk-ops-061", "Operations Internship", "Bristol Port Logistics (Demo)", "Bristol, United Kingdom",
    "OPERATIONS", "INTERNSHIP", "ON_SITE", "Internship (12 weeks)", "GBP 23,500 pro-rata",
    "A summer internship across port operations, planning, and customer service for a Bristol logistics business.",
    ["Currently studying logistics, business, or a related degree"],
    ["Shadow planning teams", "Help with KPI reporting", "Support customer enquiries"],
    ["Excel", "Communication", "Problem solving"],
    ["Power BI", "ERP"],
    sponsorship=None,
    education="Currently studying logistics, business, or a related degree.",
    experience="No prior work experience required.", deadline="2027-02-05"))
# ------------------------------------------------------------------ CONSULTING (8)
jobs.append(J("demo-uk-con-062", "Graduate Consulting Analyst", "Ashford & Blythe Consulting (Demo)", "London, United Kingdom",
    "CONSULTING", "GRADUATE", "HYBRID", "Full-time", "GBP 30,000-36,000",
    "Deliver analysis and research for strategy projects across retail, healthcare, and technology clients.",
    ["Degree in any discipline with strong analytical skills", "Excellent communication"],
    ["Build client deliverables", "Run market research", "Support workshop facilitation"],
    ["Excel", "Communication", "Research"],
    ["SQL", "Power BI", "Python"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in any discipline (2:1 or equivalent) with strong analytical content.",
    experience="0-2 years; internships and placement years count.", deadline="2026-11-20"))

jobs.append(J("demo-uk-con-063", "Graduate Technology Consultant", "Meridian Consulting Group (Demo)", "Edinburgh, United Kingdom",
    "CONSULTING", "GRADUATE", "HYBRID", "Full-time", "GBP 29,000-34,000",
    "Advise clients on technology strategy, digital transformation, and system selection for a Scottish consulting firm.",
    ["Degree in computer science, business, or a related field", "Curious and client-focused"],
    ["Assess client technology needs", "Draft recommendations", "Support implementations"],
    ["Communication", "Data analysis", "Excel"],
    ["SQL", "Process mapping", "Cloud awareness"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in computer science, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-11-30"))

jobs.append(J("demo-uk-con-064", "Business Consulting Graduate", "Manchester Advisory Partners (Demo)", "Manchester, United Kingdom",
    "CONSULTING", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Work on transformation and efficiency projects for northern public and private sector clients.",
    ["Degree in business, economics, or a related field", "Strong analytical writing"],
    ["Analyse business processes", "Prepare recommendations", "Support client presentations"],
    ["Excel", "Communication", "Problem solving"],
    ["SQL", "Power BI", "Process mapping"],
    sponsorship=None,
    education="Degree in business, economics, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-07"))
jobs.append(J("demo-uk-con-065", "Consulting Analyst (Data)", "Birmingham Advisory Partners (Demo)", "Birmingham, United Kingdom",
    "CONSULTING", "GRADUATE", "HYBRID", "Full-time", "GBP 28,000-33,000",
    "Help Midlands clients use their data better through audits, dashboards, and analysis projects.",
    ["Degree in a quantitative or business discipline", "Comfortable with data tools"],
    ["Audit client data", "Build insight dashboards", "Support data strategy"],
    ["SQL", "Excel", "Data analysis"],
    ["Python", "Power BI", "Tableau"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in a quantitative or business discipline.",
    experience="0-2 years; placement years count.", deadline="2026-12-10"))

jobs.append(J("demo-uk-con-066", "Graduate Strategy Consultant", "Yorkshire Consulting Group (Demo)", "Leeds, United Kingdom",
    "CONSULTING", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Support strategy reviews and market analysis for Yorkshire manufacturing and retail clients.",
    ["Degree in economics, business, or a related field", "Clear written communication"],
    ["Research markets", "Build strategy models", "Support board presentations"],
    ["Excel", "Research", "Communication"],
    ["Power BI", "Python", "SQL"],
    sponsorship=None,
    education="Degree in economics, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-11-28"))

jobs.append(J("demo-uk-con-067", "Junior Management Consultant", "Clyde Advisory (Demo)", "Glasgow, United Kingdom",
    "CONSULTING", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Support client engagements across process improvement and operating model design in Scotland.",
    ["Degree in any discipline", "Strong analytical and collaborative skills"],
    ["Support engagement delivery", "Analyse processes", "Prepare client workshops"],
    ["Excel", "Communication", "Problem solving"],
    ["SQL", "Process mapping", "Power BI"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in any discipline (2:1 or equivalent).",
    experience="0-2 years; internships welcome.", deadline="2026-12-18"))
jobs.append(J("demo-uk-con-068", "Consulting Insights Intern", "Severn Advisory (Demo)", "Bristol, United Kingdom",
    "CONSULTING", "INTERNSHIP", "HYBRID", "Internship (12 weeks)", "GBP 23,500 pro-rata",
    "A summer internship producing research and data insights for consulting projects in Bristol.",
    ["Currently studying business, economics, or a related degree"],
    ["Research client industries", "Prepare insight packs", "Support analyst teams"],
    ["Excel", "Research", "Communication"],
    ["Power BI", "SQL"],
    sponsorship=None,
    education="Currently studying business, economics, or a related degree.",
    experience="No prior work experience required.", deadline="2027-02-08"))

jobs.append(J("demo-uk-con-069", "Operations Consulting Graduate", "Peak Consult Partners (Demo)", "Sheffield, United Kingdom",
    "CONSULTING", "GRADUATE", "ON_SITE", "Full-time", "GBP 27,000-32,000",
    "Support efficiency and cost-reduction projects for manufacturing and public sector clients in the North.",
    ["Degree in engineering, business, or a related field", "Analytical and structured"],
    ["Map operating models", "Analyse cost drivers", "Support change workshops"],
    ["Excel", "Process mapping", "Communication"],
    ["SQL", "Power BI", "Lean basics"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="Degree in engineering, business, or a related field.",
    experience="0-2 years; placement years count.", deadline="2026-12-15"))
# ------------------------------------------------------------------ ENGINEERING (8)
jobs.append(J("demo-uk-eng-070", "Graduate Structural Engineer", "Trent Bridge Engineering (Demo)", "Nottingham, United Kingdom",
    "ENGINEERING", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Support design and site-inspection work for bridges and infrastructure projects in the Midlands.",
    ["MEng/BEng (Hons) in civil or structural engineering", "Willingness to work towards chartership"],
    ["Prepare design calculations", "Support site inspections", "Draft technical reports"],
    ["AutoCAD", "Structural analysis", "Technical writing"],
    ["Revit", "Python", "Project management"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="MEng/BEng (Hons) in civil or structural engineering.",
    experience="0-2 years; placement year counts.", deadline="2026-11-18"))

jobs.append(J("demo-uk-eng-071", "Graduate Systems Engineer", "Cambridge Systems Engineering (Demo)", "Cambridge, United Kingdom",
    "ENGINEERING", "GRADUATE", "HYBRID", "Full-time", "GBP 30,000-36,000",
    "Work on requirements, system integration, and verification for a Cambridge engineering consultancy.",
    ["Degree in engineering, physics, or computer science", "Systems-thinking mindset"],
    ["Maintain requirements", "Support system integration", "Write verification plans"],
    ["Engineering fundamentals", "Technical writing", "Python"],
    ["Model-based systems engineering", "Jira", "SQL"],
    sponsorship="We will sponsor eligible candidates.",
    education="Degree in engineering, physics, or computer science.",
    experience="0-2 years; group projects and internships welcome.", deadline="2026-12-01"))

jobs.append(J("demo-uk-eng-072", "Graduate Mechanical Engineer", "Clyde Engineering Works (Demo)", "Glasgow, United Kingdom",
    "ENGINEERING", "GRADUATE", "ON_SITE", "Full-time", "GBP 29,000-34,000",
    "Support design, testing, and manufacturing handover for heavy engineering products in Glasgow.",
    ["MEng/BEng (Hons) in mechanical engineering", "Interest in manufacturing"],
    ["Produce CAD models", "Run test procedures", "Support manufacturing handover"],
    ["CAD", "Mechanical fundamentals", "Technical writing"],
    ["SolidWorks", "MATLAB", "Project management"],
    sponsorship=None,
    education="MEng/BEng (Hons) in mechanical engineering.",
    experience="0-2 years; placement years count.", deadline="2026-11-28"))
jobs.append(J("demo-uk-eng-073", "Junior Controls Engineer", "Camley Automation Co. (Demo)", "Cambridge, United Kingdom",
    "ENGINEERING", "ENTRY_LEVEL", "ON_SITE", "Full-time", "GBP 27,000-32,000",
    "Support PLC and control-system commissioning for automation projects at a Cambridge engineering firm.",
    ["Degree in electrical, electronic, or control engineering", "Hands-on and methodical"],
    ["Support panel builds", "Run commissioning tests", "Document control schematics"],
    ["Electrical fundamentals", "PLC basics", "Technical writing"],
    ["MATLAB", "Python", "SCADA"],
    sponsorship="We may consider sponsorship for exceptional candidates.",
    education="Degree in electrical, electronic, or control engineering.",
    experience="Entry level; placement and lab work welcome.", deadline="2027-01-12"))

jobs.append(J("demo-uk-eng-074", "Graduate Civil Engineer", "Leeds Infrastructure Partners (Demo)", "Leeds, United Kingdom",
    "ENGINEERING", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Support highway and drainage design packages for Yorkshire infrastructure projects.",
    ["MEng/BEng (Hons) in civil engineering", "Geotechnical or highways interest"],
    ["Prepare design packages", "Liaise with contractors", "Draft technical reports"],
    ["AutoCAD", "Civil engineering fundamentals", "Technical writing"],
    ["Revit", "MicroStation", "Project management"],
    sponsorship="We are able to sponsor eligible candidates for this role.",
    education="MEng/BEng (Hons) in civil engineering.",
    experience="0-2 years; placement year counts.", deadline="2026-11-25"))

jobs.append(J("demo-uk-eng-075", "Engineering Graduate Programme", "Bristol Engineering Group (Demo)", "Bristol, United Kingdom",
    "ENGINEERING", "GRADUATE", "ON_SITE", "Graduate scheme (24 months)", "GBP 29,000-34,000",
    "Rotate across design, project, and manufacturing teams for a multi-discipline Bristol engineering group.",
    ["MEng/BEng (Hons) in any engineering discipline", "Willingness to rotate across teams"],
    ["Rotate across engineering teams", "Own a design workstream", "Support project reporting"],
    ["Engineering fundamentals", "Communication", "CAD"],
    ["Project management", "Python", "Technical writing"],
    sponsorship=None,
    education="MEng/BEng (Hons) in any engineering discipline.",
    experience="Graduate entry; placements welcome.", deadline="2026-12-05"))
jobs.append(J("demo-uk-eng-076", "Graduate Manufacturing Engineer", "Manchester Precision Works (Demo)", "Manchester, United Kingdom",
    "ENGINEERING", "GRADUATE", "ON_SITE", "Full-time", "GBP 28,000-33,000",
    "Support process improvement and new-product introduction on a Manchester precision manufacturing site.",
    ["MEng/BEng (Hons) in mechanical, manufacturing, or industrial engineering", "Lean mindset"],
    ["Support NPI projects", "Run process audits", "Support lean improvement activities"],
    ["Manufacturing fundamentals", "CAD", "Problem solving"],
    ["Lean methods", "Python", "Project management"],
    sponsorship="We will sponsor eligible candidates.",
    education="MEng/BEng (Hons) in mechanical, manufacturing, or industrial engineering.",
    experience="0-2 years; placement year counts.", deadline="2026-12-20"))

jobs.append(J("demo-uk-eng-077", "Engineering Placement (Year in Industry)", "Forth Engineering (Demo)", "Edinburgh, United Kingdom",
    "ENGINEERING", "PLACEMENT", "ON_SITE", "Fixed Term (12 months)", "GBP 24,000",
    "A 12-month placement supporting design and testing for a Scottish engineering consultancy.",
    ["Penultimate-year engineering degree", "Academic exposure to engineering design"],
    ["Support design work", "Help with testing", "Shadow senior engineers"],
    ["Engineering fundamentals", "CAD", "Technical writing"],
    ["MATLAB", "Python"],
    sponsorship=None,
    education="Penultimate-year engineering degree.",
    experience="Placement year; prior work experience not required.", deadline="2027-01-20"))

# ------------------------------------------------------------------ save & validate
REQUIRED_CITIES = ["London", "Manchester", "Birmingham", "Leeds", "Edinburgh",
                   "Nottingham", "Bristol", "Glasgow", "Sheffield", "Cambridge"]
MIN_PER_CATEGORY = 5

ids = [job["job_id"] for job in jobs]
urls = [job["source_url"] for job in jobs]
assert len(ids) == len(set(ids)), "duplicate job ids"
assert len(urls) == len(set(urls)), "duplicate source urls"
assert all(job["location"].endswith(", United Kingdom") or job["location"].startswith("Remote") for job in jobs), "non-UK location"

counts = Counter(job["category"] for job in jobs)
for category in ["DATA", "IT_SOFTWARE", "BUSINESS", "HR", "FINANCE", "MARKETING", "OPERATIONS", "CONSULTING", "ENGINEERING"]:
    assert counts[category] >= MIN_PER_CATEGORY, f"{category} only has {counts[category]}"

city_counts = Counter()
for job in jobs:
    for city in REQUIRED_CITIES:
        if city in job["location"]:
            city_counts[city] += 1
            break
for city in REQUIRED_CITIES:
    assert city_counts[city] >= 5, f"{city} only has {city_counts[city]} jobs"

# default demo flow: each target category must have >=5 GRADUATE jobs so the
# location-relaxed default search (London + GRADUATE) returns enough roles.
for category in counts:
    grad = sum(1 for job in jobs if job["category"] == category and job["experience_level"] == "GRADUATE")
    assert grad >= 5, f"{category} has only {grad} GRADUATE jobs"

assert any(job["salary"] is None for job in jobs), "expected at least one salary-undisclosed demo job"
assert any(job["deadline"] is None for job in jobs), "expected at least one open-deadline demo job"

print("job count:", len(jobs))
print("categories:", dict(counts))
print("cities:", dict(city_counts))
print("GRADUATE per category:", {
    cat: sum(1 for job in jobs if job["category"] == cat and job["experience_level"] == "GRADUATE")
    for cat in counts})

OUT.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
print("written:", OUT.resolve())