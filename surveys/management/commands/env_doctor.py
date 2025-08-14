from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Check required environment variables for AI Survey Builder."

    def handle(self, *args, **opts):
        ok = True
        key = getattr(settings, "OPENAI_API_KEY", "") or ""
        model = getattr(settings, "OPENAI_MODEL", "") or "gpt-4o-mini"
        base = getattr(settings, "OPENAI_BASE_URL", "") or ""
        if not key:
            ok = False
            self.stderr.write("⚠ OPENAI_API_KEY is NOT set. Add it to .env")
        else:
            self.stdout.write("✓ OPENAI_API_KEY is set")
        self.stdout.write(f"Model: {model}")
        self.stdout.write(f"Base URL: {base or '(default)'}")
        if not ok:
            self.stderr.write("Create .env from .env.example and set OPENAI_API_KEY.")
            self.stderr.write("Then run: python manage.py check && python manage.py env_doctor")

