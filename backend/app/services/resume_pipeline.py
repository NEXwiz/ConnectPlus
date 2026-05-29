import json
from app.core.openrouter_client import chat_completion
from app.core.supabase_client import get_supabase_admin

LATEX_TEMPLATE = r"""\documentclass[letterpaper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage{tabularx}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\setlength{\footskip}{4.08003pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]

\newcommand{\resumeItem}[1]{\item\small{#1\vspace{-2pt}}}
\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in,label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

%% HEADER
\begin{center}
    \textbf{\Huge \scshape <<NAME>>} \\ \vspace{1pt}
    \small <<CONTACT>>
\end{center}

%% SUMMARY
<<SUMMARY_SECTION>>

%% EXPERIENCE
<<EXPERIENCE_SECTION>>

%% PROJECTS
<<PROJECTS_SECTION>>

%% SKILLS
<<SKILLS_SECTION>>

%% EDUCATION
<<EDUCATION_SECTION>>

\end{document}
"""


def _escape_latex(text: str) -> str:
    replacements = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\^{}'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _build_summary(summary: str) -> str:
    if not summary:
        return ""
    return f"\\section{{Summary}}\n\\small{{{_escape_latex(summary)}}}"


def _build_experience(experiences: list) -> str:
    if not experiences:
        return ""
    lines = ["\\section{Experience}", "\\resumeSubHeadingListStart"]
    for exp in experiences:
        title = _escape_latex(exp.get("title", ""))
        company = _escape_latex(exp.get("company", ""))
        dates = _escape_latex(exp.get("dates", ""))
        location = _escape_latex(exp.get("location", ""))
        lines.append(f"  \\resumeSubheading{{{title}}}{{{dates}}}{{{company}}}{{{location}}}")
        if exp.get("bullets"):
            lines.append("  \\resumeItemListStart")
            for bullet in exp["bullets"]:
                lines.append(f"    \\resumeItem{{{_escape_latex(bullet)}}}")
            lines.append("  \\resumeItemListEnd")
    lines.append("\\resumeSubHeadingListEnd")
    return "\n".join(lines)


def _build_projects(projects: list) -> str:
    if not projects:
        return ""
    lines = ["\\section{Projects}", "\\resumeSubHeadingListStart"]
    for proj in projects:
        name = _escape_latex(proj.get("name", ""))
        tech = _escape_latex(proj.get("tech", ""))
        lines.append(f"  \\resumeProjectHeading{{\\textbf{{{name}}} $|$ \\emph{{{tech}}}}}{{}}")
        if proj.get("bullets"):
            lines.append("  \\resumeItemListStart")
            for bullet in proj["bullets"]:
                lines.append(f"    \\resumeItem{{{_escape_latex(bullet)}}}")
            lines.append("  \\resumeItemListEnd")
    lines.append("\\resumeSubHeadingListEnd")
    return "\n".join(lines)


def _build_skills(skills: dict) -> str:
    if not skills:
        return ""
    lines = ["\\section{Technical Skills}", "\\begin{itemize}[leftmargin=0.15in, label={}]", "  \\small{\\item{"]
    for category, items in skills.items():
        lines.append(f"    \\textbf{{{_escape_latex(category)}}}{{{_escape_latex(items)}}} \\\\")
    lines.append("  }}")
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def _build_education(education: list) -> str:
    if not education:
        return ""
    lines = ["\\section{Education}", "\\resumeSubHeadingListStart"]
    for edu in education:
        school = _escape_latex(edu.get("school", ""))
        degree = _escape_latex(edu.get("degree", ""))
        dates = _escape_latex(edu.get("dates", ""))
        lines.append(f"  \\resumeSubheading{{{school}}}{{{dates}}}{{{degree}}}{{}}")
    lines.append("\\resumeSubHeadingListEnd")
    return "\n".join(lines)


def _fill_template(data: dict) -> str:
    tex = LATEX_TEMPLATE
    tex = tex.replace("<<NAME>>", _escape_latex(data.get("name", "")))
    tex = tex.replace("<<CONTACT>>", _escape_latex(data.get("contact", "")))
    tex = tex.replace("<<SUMMARY_SECTION>>", _build_summary(data.get("summary", "")))
    tex = tex.replace("<<EXPERIENCE_SECTION>>", _build_experience(data.get("experience", [])))
    tex = tex.replace("<<PROJECTS_SECTION>>", _build_projects(data.get("projects", [])))
    tex = tex.replace("<<SKILLS_SECTION>>", _build_skills(data.get("skills", {})))
    tex = tex.replace("<<EDUCATION_SECTION>>", _build_education(data.get("education", [])))
    return tex


async def generate_tailored_resume(user_id: str, job_id: str) -> dict:
    """Generate a tailored LaTeX resume for a specific job. Returns cached if exists."""
    supabase = get_supabase_admin()

    # Check cache
    cached = supabase.table("resume_tailoring").select("*").eq("user_id", user_id).eq("job_id", job_id).limit(1).execute()
    if cached.data and cached.data[0].get("generated_tex"):
        c = cached.data[0]
        return {"tex_content": c["generated_tex"], "structured_data": c.get("analysis", {}), "job_title": c.get("job_title", ""), "job_company": c.get("job_company", "")}

    # Get user's resume text
    resumes = supabase.table("resumes").select("id, extracted_text").eq("user_id", user_id).eq("is_primary", True).limit(1).execute()
    if not resumes.data or not resumes.data[0].get("extracted_text"):
        raise ValueError("No resume uploaded. Please upload a resume first.")

    # Get job details
    job = supabase.table("jobs").select("title, company, description, requirements, tech_stack").eq("id", job_id).limit(1).execute()
    if not job.data:
        raise ValueError("Job not found.")

    resume_text = resumes.data[0]["extracted_text"]
    j = job.data[0]

    prompt = f"""You are a resume optimization expert. Given the user's current resume and a target job, restructure and rewrite the resume to maximize relevance for this specific role.

CURRENT RESUME:
{resume_text[:3000]}

TARGET JOB:
Title: {j['title']}
Company: {j['company']}
Description: {j['description']}
Requirements: {j.get('requirements', 'Not specified')}
Tech Stack: {', '.join(j.get('tech_stack', []))}

Return a JSON object with this exact structure:
{{
  "name": "Full Name",
  "contact": "email | phone | linkedin | github (pipe separated)",
  "summary": "2-3 sentence professional summary tailored to this role",
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "dates": "Start - End",
      "location": "City",
      "bullets": ["Achievement/responsibility rewritten to highlight relevance to target role"]
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "tech": "Tech1, Tech2",
      "bullets": ["What it does and why it's relevant"]
    }}
  ],
  "skills": {{
    "Languages": "Python, JavaScript, etc",
    "Frameworks": "React, FastAPI, etc",
    "Tools": "Docker, AWS, etc"
  }},
  "education": [
    {{
      "school": "University Name",
      "degree": "Degree and Major",
      "dates": "Start - End"
    }}
  ]
}}

Rules:
- Reorder and rewrite bullets to emphasize skills matching the target job
- Use strong action verbs and quantify achievements where possible
- Keep it to 1 page worth of content (max 3 experiences, 2 projects)
- Prioritize the tech stack and requirements mentioned in the job
- Do NOT fabricate experience, only restructure and reword existing content

Return ONLY valid JSON."""

    response = await chat_completion(messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=2000)

    # Parse response
    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[-1]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()

    try:
        data = json.loads(clean)
    except json.JSONDecodeError:
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(clean[start:end])
        else:
            raise ValueError("Failed to generate resume. Please try again.")

    tex_content = _fill_template(data)

    # Cache the result
    resume_id = resumes.data[0].get("id")
    if resume_id:
        supabase.table("resume_tailoring").upsert({
            "user_id": user_id,
            "job_id": job_id,
            "resume_id": resume_id,
            "analysis": data,
            "generated_tex": tex_content,
            "job_title": j["title"],
            "job_company": j["company"],
        }, on_conflict="user_id,job_id").execute()

    return {
        "tex_content": tex_content,
        "structured_data": data,
        "job_title": j["title"],
        "job_company": j["company"],
    }
