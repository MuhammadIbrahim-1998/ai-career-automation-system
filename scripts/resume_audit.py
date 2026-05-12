import re
from pathlib import Path
import pdfplumber


def extract_text_from_pdf(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"

    return text


def read_resume(file_path):
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(file_path)

    return file_path.read_text(encoding="utf-8")


def load_keywords(keywords_file_path):
    keywords_path = Path(keywords_file_path)

    return [
        line.strip()
        for line in keywords_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def extract_keywords(resume_text, keyword_list):
    found_keywords = []

    for keyword in keyword_list:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

        if re.search(pattern, resume_text.lower()):
            found_keywords.append(keyword)

    return found_keywords


def audit_resume(resume_path, keywords_file_path):
    resume_text = read_resume(resume_path)
    keywords = load_keywords(keywords_file_path)

    found_keywords = extract_keywords(resume_text, keywords)
    missing_keywords = [keyword for keyword in keywords if keyword not in found_keywords]

    score = round((len(found_keywords) / len(keywords)) * 100, 2) if keywords else 0

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    report_path = output_dir / "resume_audit_report.txt"

    report = f"""
ATS Resume Audit Report
=======================

Total Keywords: {len(keywords)}
Keywords Found: {len(found_keywords)}
Missing Keywords: {len(missing_keywords)}
ATS Keyword Score: {score}%

Found Keywords:
{", ".join(found_keywords) if found_keywords else "None"}

Missing Keywords:
{", ".join(missing_keywords) if missing_keywords else "None"}
"""

    report_path.write_text(report.strip(), encoding="utf-8")

    print(report)
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    audit_resume(
        resume_path="data/resume.txt",
        keywords_file_path="data/ats_keywords.txt"
    )