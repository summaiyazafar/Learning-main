"""
Resume Template Engine
AI Resume Tailoring System

Provides modern, ATS-friendly templates with:
- HTML/CSS preview generation for live interactive display
- Styling parameters for PDF and DOCX generators
- 4 Distinct Curated Templates:
    1. Modern Executive (Navy / Slate Blue)
    2. Harvard ATS Classic (Monochrome / High ATS)
    3. Silicon Valley Tech (Teal / Cyan)
    4. Creative Indigo (Indigo / Violet)
"""

from typing import Dict, Any, List
import re
from xml.sax.saxutils import escape

AVAILABLE_TEMPLATES = {
    "modern_executive": {
        "id": "modern_executive",
        "name": "Modern Executive",
        "badge": "👔 Executive Choice",
        "description": "Clean navy accents, balanced structure, refined typography. Ideal for Executive & Leadership roles.",
        "primary_color": "#1E3A8A",
        "secondary_color": "#2563EB",
        "accent_bg": "#EFF6FF",
        "border_color": "#BFDBFE",
        "text_color": "#1F2937",
        "meta_color": "#4B5563",
        "font_family": "'Inter', 'Segoe UI', -apple-system, sans-serif",
    },
    "harvard_ats": {
        "id": "harvard_ats",
        "name": "Harvard ATS Classic",
        "badge": "🏛️ Maximum ATS Score",
        "description": "Timeless single-column layout, charcoal palette, strict ATS compliance for Workday/Taleo.",
        "primary_color": "#111827",
        "secondary_color": "#374151",
        "accent_bg": "#F9FAFB",
        "border_color": "#E5E7EB",
        "text_color": "#111827",
        "meta_color": "#4B5563",
        "font_family": "'Georgia', 'Times New Roman', serif",
    },
    "silicon_valley": {
        "id": "silicon_valley",
        "name": "Silicon Valley Tech",
        "badge": "⚡ Modern Tech Stack",
        "description": "Deep emerald & cyan accents, skills badge chips, tech stack highlights. Perfect for AI/ML & SWE.",
        "primary_color": "#0F766E",
        "secondary_color": "#0D9488",
        "accent_bg": "#F0FDFA",
        "border_color": "#99F6E4",
        "text_color": "#0F172A",
        "meta_color": "#334155",
        "font_family": "'Outfit', 'Inter', 'Segoe UI', sans-serif",
    },
    "creative_indigo": {
        "id": "creative_indigo",
        "name": "Creative Indigo",
        "badge": "🎨 High-Impact Visual",
        "description": "Vibrant indigo styling, elegant section borders, crisp headers. Great for Data Scientists & Consultants.",
        "primary_color": "#4338CA",
        "secondary_color": "#6366F1",
        "accent_bg": "#EEF2FF",
        "border_color": "#C7D2FE",
        "text_color": "#1E1B4B",
        "meta_color": "#4338CA",
        "font_family": "'Plus Jakarta Sans', 'Inter', sans-serif",
    }
}

def clean(text: Any) -> str:
    """Helper to clean string input."""
    if text is None:
        return ""
    return str(text).strip()

def safe_html(text: Any) -> str:
    """Escape text for HTML safety."""
    return escape(clean(text))

def strip_bullet(text: Any) -> str:
    """Strip bullet markers or numbers from the start of a line."""
    if text is None:
        return ""
    return re.sub(r"^(?:[•●▪◦*-]|\d+[\.\)])\s*", "", str(text)).strip()

def clean_job_title(title: str) -> str:
    """Sanitize job title string by stripping raw metadata labels. Preserves full title with seniority prefixes."""
    if not title:
        return "Target Position"
    # Insert space before concatenated metadata labels
    title = re.sub(
        r"(?i)(engineer|developer|analyst|scientist|manager|lead|architect|specialist)"
        r"(Location|Job|Type|Description|Department|About|Salary|Responsibilities|Requirements|Qualifications)",
        r"\1 \2", title
    )
    split_pattern = r"(?i)(?:location|job\s*type|job\s*description|about\s+the\s+job|department|salary|experience|responsibilities|requirements|qualifications|overview|mode|hybrid|full-time|part-time|remote|onsite|islamabad|karachi|lahore|rawalpindi)"
    title = re.split(split_pattern, title)[0].strip()
    title = re.sub(r"^[:\-–—\s,|]+|[:\-–—\s,|]+$", "", title).strip()
    # Remove seniority/level prefixes (Senior, Junior, Lead, etc.)
    title = re.sub(
        r"(?i)^(?:senior|sr\.?|junior|jr\.?|lead|principal|staff|associate|chief|head|director|entry[\s-]*level)\s+",
        "", title
    ).strip()
    return title if title else "Target Position"

def render_html_preview(resume: Dict[str, Any], template_id: str = "modern_executive") -> str:
    """
    Renders the tailored resume in a rich, responsive, print-styled HTML container.
    """
    tmpl = AVAILABLE_TEMPLATES.get(template_id, AVAILABLE_TEMPLATES["modern_executive"])

    name = safe_html(resume.get("name") or "Candidate Name")
    raw_job_title = resume.get("job_title") or resume.get("target_position") or "Target Position"
    job_title = safe_html(clean_job_title(raw_job_title))
    
    # Contact items
    contact_items = []
    if resume.get("email"):
        contact_items.append(f'<span>📧 {safe_html(resume.get("email"))}</span>')
    if resume.get("phone"):
        contact_items.append(f'<span>📱 {safe_html(resume.get("phone"))}</span>')
    if resume.get("location"):
        contact_items.append(f'<span>📍 {safe_html(resume.get("location"))}</span>')
    if resume.get("linkedin"):
        li = clean(resume.get("linkedin"))
        contact_items.append(f'<span>🔗 <a href="{safe_html(li)}" target="_blank" style="color:{tmpl["primary_color"]};text-decoration:none;">LinkedIn</a></span>')
    if resume.get("github"):
        gh = clean(resume.get("github"))
        contact_items.append(f'<span>💻 <a href="{safe_html(gh)}" target="_blank" style="color:{tmpl["primary_color"]};text-decoration:none;">GitHub</a></span>')
    if resume.get("kaggle"):
        kg = clean(resume.get("kaggle"))
        contact_items.append(f'<span>📊 <a href="{safe_html(kg)}" target="_blank" style="color:{tmpl["primary_color"]};text-decoration:none;">Kaggle</a></span>')

    contact_html = " &bull; ".join(contact_items)

    # Professional Summary
    summary = clean(resume.get("professional_summary") or resume.get("summary") or "")

    # Skills
    skills_data = resume.get("skills", [])
    skills_html = ""
    if isinstance(skills_data, dict):
        for cat, slist in skills_data.items():
            if slist:
                s_badges = "".join([f'<span class="skill-chip">{safe_html(s)}</span>' for s in slist if s])
                skills_html += f"""
                <div class="skill-cat-row">
                    <span class="skill-cat-title">{safe_html(cat)}:</span>
                    <div class="skill-chip-wrap">{s_badges}</div>
                </div>
                """
    elif isinstance(skills_data, list):
        s_badges = "".join([f'<span class="skill-chip">{safe_html(s)}</span>' for s in skills_data if s])
        skills_html = f'<div class="skill-chip-wrap">{s_badges}</div>'

    # Experience
    exp_data = resume.get("experience", [])
    exp_html = ""
    if isinstance(exp_data, list):
        for item in exp_data:
            if isinstance(item, dict):
                title = safe_html(item.get("title") or item.get("role") or "")
                company = safe_html(item.get("company") or "")
                dates = safe_html(item.get("dates") or item.get("duration") or "")
                loc = safe_html(item.get("location") or "")
                bullets = item.get("bullets", [])
                if isinstance(bullets, str):
                    bullets = [b.strip() for b in bullets.splitlines() if b.strip()]
                b_html = "".join([f"<li>{safe_html(strip_bullet(b))}</li>" for b in bullets if b])
                
                exp_html += f"""
                <div class="entry-block">
                    <div class="entry-header">
                        <div>
                            <span class="entry-title">{title}</span>
                            {f'<span class="entry-company"> | {company}</span>' if company else ''}
                        </div>
                        <div class="entry-meta">
                            {f'<span>{dates}</span>' if dates else ''}
                            {f'<span class="meta-sep">&bull;</span><span>{loc}</span>' if loc else ''}
                        </div>
                    </div>
                    {f'<ul class="bullet-list">{b_html}</ul>' if b_html else ''}
                </div>
                """
            else:
                line = safe_html(strip_bullet(item))
                exp_html += f'<div class="simple-bullet">• {line}</div>'

    # Projects
    proj_data = resume.get("projects", [])
    proj_html = ""
    if isinstance(proj_data, list):
        for proj in proj_data:
            if isinstance(proj, dict):
                pname = safe_html(proj.get("name") or proj.get("title") or "")
                desc = safe_html(proj.get("description") or "")
                tech = proj.get("technologies") or proj.get("tech_stack") or []
                if isinstance(tech, str):
                    tech = [t.strip() for t in tech.split(",") if t.strip()]
                tech_badges = " ".join([f'<span class="tech-tag">{safe_html(t)}</span>' for t in tech if t])
                
                proj_html += f"""
                <div class="entry-block">
                    <div class="entry-header">
                        <span class="entry-title">{pname}</span>
                        {f'<div class="tech-wrap">{tech_badges}</div>' if tech_badges else ''}
                    </div>
                    {f'<div class="entry-desc">{desc}</div>' if desc else ''}
                </div>
                """
            else:
                line = safe_html(strip_bullet(proj))
                proj_html += f'<div class="simple-bullet">• {line}</div>'

    # Education
    edu_data = resume.get("education", [])
    edu_html = ""
    if isinstance(edu_data, list):
        for edu in edu_data:
            if isinstance(edu, dict):
                deg = safe_html(edu.get("degree") or "")
                inst = safe_html(edu.get("institution") or "")
                dates = safe_html(edu.get("dates") or "")
                edu_html += f"""
                <div class="entry-block">
                    <div class="entry-header">
                        <span class="entry-title">{deg}</span>
                        <span class="entry-meta">{dates}</span>
                    </div>
                    {f'<div class="entry-company">{inst}</div>' if inst else ''}
                </div>
                """
            else:
                edu_html += f'<div class="simple-bullet">• {safe_html(edu)}</div>'
    elif edu_data:
        for line in str(edu_data).splitlines():
            if line.strip():
                edu_html += f'<div class="simple-bullet">• {safe_html(line.strip())}</div>'

    # Certifications
    cert_data = resume.get("certifications", [])
    cert_html = ""
    if isinstance(cert_data, list):
        for c in cert_data:
            if c:
                cert_html += f'<div class="simple-bullet">🏆 {safe_html(c)}</div>'
    elif cert_data:
        for line in str(cert_data).splitlines():
            if line.strip():
                cert_html += f'<div class="simple-bullet">🏆 {safe_html(line.strip())}</div>'

    # Assemble HTML document
    return f"""
    <div class="resume-paper template-{template_id}">
        <style>
            .resume-paper {{
                background: #ffffff;
                color: {tmpl["text_color"]};
                font-family: {tmpl["font_family"]};
                max-width: 820px;
                margin: 0 auto;
                padding: 38px 45px;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05);
                border: 1px solid #E2E8F0;
                line-height: 1.5;
            }}
            .resume-header {{
                text-align: center;
                border-bottom: 2px solid {tmpl["primary_color"]};
                padding-bottom: 16px;
                margin-bottom: 20px;
            }}
            .resume-name {{
                font-size: 26px;
                font-weight: 800;
                color: {tmpl["primary_color"]};
                letter-spacing: -0.5px;
                margin: 0 0 4px 0;
            }}
            .resume-target-title {{
                font-size: 14px;
                font-weight: 600;
                color: {tmpl["secondary_color"]};
                text-transform: uppercase;
                letter-spacing: 1.2px;
                margin-bottom: 8px;
            }}
            .resume-contact {{
                font-size: 11.5px;
                color: {tmpl["meta_color"]};
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 8px 12px;
            }}
            .resume-section {{
                margin-bottom: 20px;
            }}
            .section-title {{
                font-size: 12.5px;
                font-weight: 800;
                color: {tmpl["primary_color"]};
                text-transform: uppercase;
                letter-spacing: 1px;
                border-bottom: 1.5px solid {tmpl["border_color"]};
                padding-bottom: 4px;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
            }}
            .summary-text {{
                font-size: 12px;
                color: {tmpl["text_color"]};
                text-align: justify;
                line-height: 1.6;
            }}
            .skill-cat-row {{
                margin-bottom: 8px;
            }}
            .skill-cat-title {{
                font-weight: 700;
                font-size: 12px;
                color: {tmpl["primary_color"]};
                margin-right: 6px;
            }}
            .skill-chip-wrap {{
                display: inline-flex;
                flex-wrap: wrap;
                gap: 5px;
                vertical-align: middle;
            }}
            .skill-chip {{
                background: {tmpl["accent_bg"]};
                color: {tmpl["primary_color"]};
                border: 1px solid {tmpl["border_color"]};
                font-size: 11px;
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 6px;
            }}
            .tech-tag {{
                background: #F1F5F9;
                color: #334155;
                font-size: 10px;
                font-weight: 600;
                padding: 1px 6px;
                border-radius: 4px;
                margin-left: 4px;
            }}
            .entry-block {{
                margin-bottom: 12px;
            }}
            .entry-header {{
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                margin-bottom: 3px;
            }}
            .entry-title {{
                font-weight: 700;
                font-size: 12.5px;
                color: {tmpl["text_color"]};
            }}
            .entry-company {{
                font-weight: 600;
                font-size: 12px;
                color: {tmpl["secondary_color"]};
            }}
            .entry-meta {{
                font-size: 11px;
                color: {tmpl["meta_color"]};
                font-style: italic;
            }}
            .meta-sep {{
                margin: 0 4px;
            }}
            .entry-desc {{
                font-size: 11.5px;
                color: {tmpl["text_color"]};
                margin-top: 2px;
            }}
            .bullet-list {{
                margin: 4px 0 0 0;
                padding-left: 18px;
                font-size: 11.5px;
                color: {tmpl["text_color"]};
            }}
            .bullet-list li {{
                margin-bottom: 3px;
                line-height: 1.5;
            }}
            .simple-bullet {{
                font-size: 11.5px;
                margin-bottom: 4px;
                color: {tmpl["text_color"]};
            }}
        </style>

        <!-- HEADER -->
        <div class="resume-header">
            <h1 class="resume-name">{name}</h1>
            <div class="resume-target-title">{job_title}</div>
            <div class="resume-contact">{contact_html}</div>
        </div>

        <!-- SUMMARY -->
        {f'''
        <div class="resume-section">
            <div class="section-title">Professional Summary</div>
            <div class="summary-text">{safe_html(summary)}</div>
        </div>
        ''' if summary else ''}

        <!-- SKILLS -->
        {f'''
        <div class="resume-section">
            <div class="section-title">Technical Competencies & Skills</div>
            {skills_html}
        </div>
        ''' if skills_html else ''}

        <!-- EXPERIENCE -->
        {f'''
        <div class="resume-section">
            <div class="section-title">Professional Experience</div>
            {exp_html}
        </div>
        ''' if exp_html else ''}

        <!-- PROJECTS -->
        {f'''
        <div class="resume-section">
            <div class="section-title">Key Projects & Implementations</div>
            {proj_html}
        </div>
        ''' if proj_html else ''}

        <!-- EDUCATION -->
        {f'''
        <div class="resume-section">
            <div class="section-title">Education</div>
            {edu_html}
        </div>
        ''' if edu_html else ''}

        <!-- CERTIFICATIONS -->
        {f'''
        <div class="resume-section">
            <div class="section-title">Certifications & Credentials</div>
            {cert_html}
        </div>
        ''' if cert_html else ''}
    </div>
    """
