"""
Unit tests for the Transcript Parser.
"""

from app.services.parser import parse_transcript, parse_interview_guide


def test_parse_transcript_header_and_turns():
    sample_text = """Expert: Dr. Jean Martin
Role: Head of Urology, Centre Hospitalier Universitaire de Bordeaux
Country: France
Topic: European Robotic Surgery Market — France
Date: 2024-03-15

00:00
Interviewer: Welcome, Dr. Martin. Could you give us a brief overview of the robotic surgery landscape in France?

00:45
Dr. Martin: Robotics has definitely moved from an exploratory technology to an expected standard of care in French university hospitals.
"""
    parsed = parse_transcript(sample_text, "test_france.txt")
    assert parsed.expert_name == "Dr. Jean Martin"
    assert "Urology" in parsed.expert_role
    assert parsed.country == "France"
    assert len(parsed.turns) == 2
    assert "Interviewer" in parsed.turns[0].speaker
    assert "Dr. Martin" in parsed.turns[1].speaker
    assert parsed.turns[1].timestamp == "00:45"
    assert "standard of care" in parsed.turns[1].text


def test_parse_interview_guide():
    guide_text = """Interview Guide: European Robotic Surgery Market

Questions:
1. What is the current adoption rate and stage of robotic surgery in your country?
2. What are the key drivers pushing hospitals to acquire surgical robots?
3. What are the primary barriers to wider adoption?
4. How do reimbursement systems affect the economics of robotic surgery?
5. Who are the dominant robotic system vendors, and how is competition evolving?
6. What is your 3-5 year outlook for the robotic surgery market?
"""
    questions = parse_interview_guide(guide_text)
    assert len(questions) == 6
    assert "adoption rate" in questions[0]
    assert "outlook" in questions[5]


def test_parse_markdown_transcript_italy():
    sample_md = """# Expert 4 — Italy

**Expert name:** Dr. Marco Rossi
**Role:** Director of Urology, Regional Teaching Hospital
**Country:** Italy
**Interview Topic:** European Robotic Surgery Market
**Transcript Type:** Synthetic test transcript for evaluation

---

**[00:00] Interviewer:** Could you describe the current adoption of robotic surgery in Italian hospitals?

**[00:18] Dr. Marco Rossi:** Adoption is increasing, but it is still concentrated in larger teaching hospitals and private centres.
"""
    parsed = parse_transcript(sample_md, "transcript_3_test_Italy.txt")
    assert parsed.expert_name == "Dr. Marco Rossi"
    assert parsed.country == "Italy"
    assert "Urology" in parsed.expert_role
    assert len(parsed.turns) == 2
    assert parsed.turns[0].speaker == "Interviewer"
    assert parsed.turns[0].timestamp == "00:00"
    assert parsed.turns[1].speaker == "Dr. Marco Rossi"
    assert parsed.turns[1].timestamp == "00:18"
    assert "teaching hospitals" in parsed.turns[1].text

