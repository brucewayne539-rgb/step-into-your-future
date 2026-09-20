"""Curated CHS 2025–26 catalog-backed prototype matches; not a full catalog transcription."""
COURSES = [('Intro to Engineering', 9, 9, 'Engineering / Technology', 'Engineering design and problem-solving; 9th-grade choice in Pre-Engineering & Robotics CTE.', 27, ['engineering', 'architecture', 'technology', 'construction', 'design']), ('Robotics 1', 10, 10, 'Pre-Engineering & Robotics', 'Build and test robotic systems; 10th-grade course in the CTE sequence.', 27, ['engineering', 'robotics', 'technology', 'manufacturing']), ('CAD', 10, 12, 'Pre-Engineering & Robotics', 'Computer-aided design; one of the pathway options after the introductory sequence.', 27, ['engineering', 'architecture', 'construction', 'design', 'manufacturing']), ('Mechatronics', 10, 12, 'Pre-Engineering & Robotics', 'Mechanical and electronic systems; an option within the engineering sequence.', 27, ['engineering', 'robotics', 'technology', 'manufacturing']), ('CAD 3D Printing & Robotics 2', 10, 12, 'Pre-Engineering & Robotics', 'Advanced design, fabrication and robotics pathway option.', 27, ['engineering', 'architecture', 'robotics', 'design', 'manufacturing']), ('Engineering Design & Development for Robotics/Pre-Engineering', 12, 12, 'Pre-Engineering & Robotics', 'Grade 12 engineering capstone; plan prerequisites with a counselor.', 27, ['engineering', 'architecture', 'robotics', 'design', 'manufacturing']), ('Chemistry (CP or H)', 9, 12, 'Science', 'Science foundation included in the Pre-Engineering & Robotics pathway.', 27, ['engineering', 'health', 'medicine', 'science', 'chemistry', 'pharmacy', 'environment']), ('Physics (Honors or AP)', 10, 12, 'Science', 'Physics option in the Pre-Engineering & Robotics pathway; confirm placement.', 27, ['engineering', 'architecture', 'science', 'physics', 'aviation']), ('Pre-Calculus', 10, 12, 'Mathematics', 'Math course included in the Pre-Engineering & Robotics pathway.', 27, ['engineering', 'architecture', 'math', 'science', 'computer', 'finance']), ('Principles of Biomedical Science', 9, 9, 'PLTW Biomedical CTE', 'First course in the biomedical sequence, designated for grade 9.', 20, ['health', 'medicine', 'physical therap', 'nurs', 'biomed', 'science', 'pharmacy', 'dental']), ('Human Body Systems', 10, 10, 'PLTW Biomedical CTE', 'Second biomedical sequence course, designated for grade 10.', 20, ['health', 'medicine', 'physical therap', 'nurs', 'biomed', 'science', 'pharmacy', 'dental']), ('Medical Interventions', 11, 11, 'PLTW Biomedical CTE', 'Third biomedical sequence course, designated for grade 11.', 20, ['health', 'medicine', 'physical therap', 'nurs', 'biomed', 'science', 'pharmacy', 'dental']), ('Biomedical Innovations', 12, 12, 'PLTW Biomedical CTE', 'Grade 12 biomedical sequence course.', 20, ['health', 'medicine', 'physical therap', 'nurs', 'biomed', 'science', 'pharmacy', 'dental']), ('Anatomy & Physiology (CP/H)', 10, 12, 'Sports Medicine / Science', 'Listed in Sports Medicine and as an optional Biomedical CTE elective; check prerequisites.', 33, ['health', 'medicine', 'physical therap', 'nurs', 'biomed', 'science', 'pharmacy', 'sports', 'fitness']), ('Introduction to Sports Medicine', 9, 12, 'Sports Medicine', 'Introduction to patient care and sports medical settings.', 33, ['health', 'medicine', 'physical therap', 'sports', 'fitness', 'athletic']), ('Fitness & Conditioning I & II', 9, 12, 'Physical Education / Sports Medicine', 'Fitness and conditioning courses within the Sports Medicine pathway.', 33, ['physical therap', 'sports', 'fitness', 'athletic', 'health']), ('Leadership in Athletics', 9, 12, 'Sports Medicine', 'Athletics leadership course in the Sports Medicine pathway.', 33, ['physical therap', 'sports', 'fitness', 'athletic', 'health'])]

def chs_for_grade(career, grade, path="explore", priority="Doing work I enjoy"):
    grade=int(grade)
    name=career.lower()
    # Explicit occupational families: specialist names need educational meaning,
    # not a substring coincidence (e.g. neurosurgeon -> biomedical sciences).
    medical_titles = (
        "neurosurgeon", "surgeon", "physician", "doctor", "neurologist",
        "cardiologist", "pediatrician", "anesthesiologist", "psychiatrist",
        "nurse", "medical", "dentist", "dental", "pharmacist", "pharmacy",
        "physical therapist", "occupational therapist", "physician assistant",
        "health services", "healthcare", "caregiver", "paramedic", "emt",
    )
    if any(t in name for t in medical_titles):
        name += " medicine biomed health science chemistry"
    name=name.replace("engineer", "engineering").replace("architect", "architecture").replace("robotic", "robotics")
    tokens={part for part in __import__("re").split(r"[^a-z]+",name) if len(part)>3}
    hits=[]
    for title,lo,hi,dept,why,page,keys in COURSES:
        score=sum(5 if k in name else 0 for k in keys)
        if any(k in tokens for k in keys): score+=3
        if score: hits.append((score, title,lo,hi,dept,why,page))
    hits.sort(key=lambda x:(-x[0],x[2],x[1]))
    # Never silently assign unrelated electives when there is no supported mapping.
    def card(r):
        score,title,lo,hi,dept,why,page=r
        return dict(name=title,why=why,grades=str(lo) if lo==hi else f"{lo}–{hi}",department=dept,page=page,planned=grade<lo,prerequisite="Confirm entry requirements and current availability with CHS counseling.")
    now=[card(r) for r in hits if r[2]<=grade<=r[3]][:5]
    later=[card(r) for r in hits if r[2]>grade][:5]
    return dict(grade_note=f"Grade {grade}: suggestions are based on the CHS 2025–26 Program of Studies, not a confirmed 2026–27 schedule.",
      primary_course_details=now, supporting_course_details=[],future_course_details=later,
      experience="Ask a CHS counselor about relevant clubs, job shadowing, work-based learning and available CTE or Learning Academy pathways.",
      good="CHS CTE sequences have course order and eligibility requirements. A listed elective is not a promise of enrollment or current-year availability.",
      next="Review the current CHS program of studies and your four-year plan with your counselor.",
      reflection="What interests you most about this career?",source="CHS 2025–26 Program of Studies",
      programs=[dict(name="Pre-Engineering & Robotics CTE",detail="Intro to Engineering → Robotics 1 → pathway option → Grade 12 capstone; catalog p. 27") ] if any(k in name for k in ("engineer","architect","robot","design")) else ([dict(name="PLTW Biomedical CTE",detail="Principles of Biomedical Science → Human Body Systems → Medical Interventions → Biomedical Innovations; catalog p. 20"),dict(name="Sports Medicine Learning Academy",detail="Introduction to Sports Medicine, Fitness & Conditioning, Anatomy & Physiology and Leadership in Athletics; catalog p. 33")] if any(k in name for k in ("health","physical therap","medic","nurs","athlet","sport","surgeon","physician")) else []))
