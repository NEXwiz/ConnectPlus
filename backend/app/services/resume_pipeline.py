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


async def _step1_analyze_gap(resume_text: str, job: dict) -> dict:
    """Step 1: Classify the gap between resume and job as close_match or career_pivot."""
    prompt = f"""Analyze the gap between this resume and target job. Return JSON only.

RESUME (summary):
{resume_text[:1500]}

TARGET JOB:
Title: {job['title']}
Tech Stack: {', '.join(job.get('tech_stack', []))}
Requirements: {job.get('requirements', 'Not specified')}

Return:
{{
  "gap_type": "close_match" or "career_pivot",
  "confidence": 0.0-1.0,
  "transferable_skills": ["skills from resume relevant to target"],
  "missing_skills": ["skills needed but not in resume"],
  "reasoning": "one sentence why"
}}

Rules:
- "close_match" = same domain, overlapping tech, just needs reframing
- "career_pivot" = different domain, <30% tech overlap, needs significant restructuring

Return ONLY valid JSON."""

    response = await chat_completion(messages=[{"role": "user", "content": prompt}], temperature=0.2, max_tokens=500)
    clean = _parse_json_response(response)
    return clean


def _parse_json_response(response: str) -> dict:
    """Parse JSON from LLM response, handling markdown fences."""
    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[-1]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(clean[start:end])
        raise ValueError("Failed to parse LLM response.")


async def _step2_generate_close_match(resume_text: str, job: dict) -> dict:
    """Step 2a: Generate resume for close match — rewrite and reorder existing content."""
    prompt = f"""You are a resume optimization expert. Restructure this resume for the target role.

CURRENT RESUME:
{resume_text[:3000]}

TARGET JOB:
Title: {job['title']}
Company: {job['company']}
Description: {job['description']}
Requirements: {job.get('requirements', 'Not specified')}
Tech Stack: {', '.join(job.get('tech_stack', []))}

Return a JSON object:
{{
  "name": "Full Name",
  "contact": "email | phone | linkedin | github",
  "summary": "2-3 sentence summary tailored to this role",
  "experience": [{{"title": "", "company": "", "dates": "", "location": "", "bullets": [""]}}],
  "projects": [{{"name": "", "tech": "", "bullets": [""]}}],
  "skills": {{"Languages": "", "Frameworks": "", "Tools": ""}},
  "education": [{{"school": "", "degree": "", "dates": ""}}]
}}

Rules:
- Reorder and rewrite bullets to emphasize relevance to target job
- Use action verbs and quantify achievements
- Max 3 experiences, 2 projects (1 page)
- Do NOT fabricate, only restructure existing content

Return ONLY valid JSON."""

    response = await chat_completion(messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=2000)
    return _parse_json_response(response)


async def _step2_generate_career_pivot(resume_text: str, job: dict, gap: dict) -> dict:
    """Step 2b: Generate resume for career pivot — highlight transferable skills + suggest projects."""
    transferable = ", ".join(gap.get("transferable_skills", []))
    missing = ", ".join(gap.get("missing_skills", []))

    prompt = f"""You are a resume expert helping someone pivot careers. Their background doesn't directly match the target role, so focus on transferable skills and suggest projects they should build.

CURRENT RESUME:
{resume_text[:3000]}

TARGET JOB:
Title: {job['title']}
Company: {job['company']}
Description: {job['description']}
Tech Stack: {', '.join(job.get('tech_stack', []))}

TRANSFERABLE SKILLS: {transferable}
MISSING SKILLS: {missing}

Return a JSON object:
{{
  "name": "Full Name",
  "contact": "email | phone | linkedin | github",
  "summary": "2-3 sentence summary emphasizing transferable skills and career direction",
  "experience": [{{"title": "", "company": "", "dates": "", "location": "", "bullets": ["rewritten to highlight transferable aspects"]}}],
  "projects": [
    {{"name": "[SUGGESTED] Project Name", "tech": "relevant tech", "bullets": ["Description of what to build — user should complete this project"]}},
    {{"name": "[SUGGESTED] Project Name 2", "tech": "relevant tech", "bullets": ["Another project idea to demonstrate missing skills"]}}
  ],
  "skills": {{"Languages": "", "Frameworks": "", "Tools": ""}},
  "education": [{{"school": "", "degree": "", "dates": ""}}],
  "pivot_notes": {{
    "message": "This resume has significant gaps for this role. Complete the suggested projects before applying.",
    "suggested_learning": ["course or resource 1", "course or resource 2"]
  }}
}}

Rules:
- Experience bullets should emphasize transferable skills ({transferable})
- Projects marked [SUGGESTED] are ideas the user should build to fill gaps
- Skills section should include both current and target skills (mark target ones they need to learn)
- Be honest about gaps, don't fabricate experience

Return ONLY valid JSON."""

    response = await chat_completion(messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=2000)
    return _parse_json_response(response)


async def generate_tailored_resume(user_id: str, job_id: str) -> dict:
    """Agentic resume pipeline: analyze gap → generate based on gap type."""
    supabase = get_supabase_admin()

    # Check cache
    cached = supabase.table("resume_tailoring").select("*").eq("user_id", user_id).eq("job_id", job_id).limit(1).execute()
    if cached.data and cached.data[0].get("generated_tex"):
        c = cached.data[0]
        return {
            "tex_content": c["generated_tex"],
            "structured_data": c.get("analysis", {}),
            "gap_analysis": c.get("analysis", {}).get("gap_analysis"),
            "job_title": c.get("job_title", ""),
            "job_company": c.get("job_company", ""),
        }

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

    # Step 1: Analyze gap
    gap = await _step1_analyze_gap(resume_text, j)

    # Step 2: Generate based on gap type
    if gap.get("gap_type") == "career_pivot":
        data = await _step2_generate_career_pivot(resume_text, j, gap)
    else:
        data = await _step2_generate_close_match(resume_text, j)

    # Attach gap analysis to output
    data["gap_analysis"] = gap

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
        "gap_analysis": gap,
        "job_title": j["title"],
        "job_company": j["company"],
    }
