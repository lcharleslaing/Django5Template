from django.utils import timezone
from django.contrib.auth.models import User
from .models import Survey, Section, Question


def create_survey_from_json(data, creator: User, publish_days: int = 14) -> Survey:
    now = timezone.now()
    survey = Survey.objects.create(
        title=data["title"],
        description=data.get("description", ""),
        publish_start=now,
        publish_end=now + timezone.timedelta(days=publish_days),
        status="DRAFT",
        created_by=creator,
        k_threshold=5,
    )

    section_order = 0
    for s in data.get("sections", []):
        section_order += 1
        section = Section.objects.create(
            survey=survey,
            title=s["title"],
            description=s.get("description", ""),
            order=section_order,
        )
        q_order = 0
        for q in s.get("questions", []):
            q_order += 1
            qtype = q["type"]
            options = q.get("options") or []
            Question.objects.create(
                section=section,
                type=qtype,
                prompt=q["prompt"],
                help_text=q.get("help_text", ""),
                required=bool(q.get("required", True)),
                options_json={"choices": options} if options else {},
                scale_min=int(q.get("scale_min", 1 if qtype in ("LIKERT", "NUMBER") else 0)),
                scale_max=int(q.get("scale_max", 5 if qtype == "LIKERT" else (10 if qtype == "NPS" else 5))),
                order=q_order,
                logic_json={},
                anonymity_mode=q.get("anonymity_mode", "ESCROW"),
            )
    return survey


