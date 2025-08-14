from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from surveys.ai_survey_generator import generate_survey_json
from surveys.services import create_survey_from_json


class Command(BaseCommand):
    help = "Generate a survey via AI"

    def add_arguments(self, parser):
        parser.add_argument("--topic", required=True)
        parser.add_argument("--creator", required=True, help="username or email")
        parser.add_argument("--publish-days", type=int, default=14)
        parser.add_argument("--auto-publish", action="store_true")

    def handle(self, *args, **opts):
        user = User.objects.filter(username=opts["creator"]).first() or \
               User.objects.filter(email=opts["creator"]).first()
        if not user:
            self.stderr.write("Creator not found.")
            return
        data = generate_survey_json(topic=opts["topic"])
        survey = create_survey_from_json(data, user, publish_days=opts["publish-days"])
        if opts["auto-publish"]:
            survey.status = "PUBLISHED"; survey.save()
        self.stdout.write(f"Created survey: {survey.title} (id={survey.id})")


