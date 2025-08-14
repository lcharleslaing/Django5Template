from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
import json


class Survey(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('CLOSED', 'Closed'),
        ('ARCHIVED', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publish_start = models.DateTimeField()
    publish_end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_surveys')
    k_threshold = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('surveys:survey_detail', kwargs={'pk': self.pk})
    
    @property
    def is_active(self):
        now = timezone.now()
        return (self.status == 'PUBLISHED' and 
                self.publish_start <= now <= self.publish_end)
    
    @property
    def response_count(self):
        return self.responses.count()
    
    @property
    def sections_count(self):
        return self.sections.count()


class Section(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['survey', 'order']
    
    def __str__(self):
        return f"{self.survey.title} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('surveys:section_detail', kwargs={'pk': self.pk})


class Question(models.Model):
    QUESTION_TYPES = [
        ('LIKERT', 'Likert Scale'),
        ('MULTI', 'Multiple Choice'),
        ('SINGLE', 'Single Choice'),
        ('MATRIX', 'Matrix Question'),
        ('SHORT_TEXT', 'Short Text'),
        ('LONG_TEXT', 'Long Text'),
        ('NPS', 'Net Promoter Score'),
        ('RANK', 'Ranking'),
        ('DATE', 'Date'),
        ('NUMBER', 'Number'),
    ]
    
    ANONYMITY_MODES = [
        ('ANONYMOUS', 'Anonymous'),
        ('ESCROW', 'Private (Escrow)'),
        ('SIGNED', 'Signed'),
    ]
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    prompt = models.TextField()
    help_text = models.TextField(blank=True)
    required = models.BooleanField(default=True)
    options_json = models.JSONField(default=dict, blank=True)  # For choices, matrix options, etc.
    scale_min = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    scale_max = models.IntegerField(default=5, validators=[MaxValueValidator(10)])
    order = models.IntegerField(default=0)
    logic_json = models.JSONField(default=dict, blank=True)  # For conditional logic
    anonymity_mode = models.CharField(max_length=20, choices=ANONYMITY_MODES, default='ESCROW')
    
    class Meta:
        ordering = ['order']
        unique_together = ['section', 'order']
    
    def __str__(self):
        return f"{self.section.title} - {self.prompt[:50]}..."
    
    def get_absolute_url(self):
        return reverse('surveys:question_detail', kwargs={'pk': self.pk})
    
    @property
    def options(self):
        """Get options as a list, handling both list and dict formats"""
        if isinstance(self.options_json, list):
            return self.options_json
        elif isinstance(self.options_json, dict):
            return self.options_json.get('choices', [])
        return []
    
    @property
    def is_scale_question(self):
        """Check if this is a scale-based question (Likert, NPS, Number)"""
        return self.type in ['LIKERT', 'NPS', 'NUMBER']

    @property
    def scale_values(self):
        """List of integer options for scale questions."""
        try:
            start = int(self.scale_min)
            end = int(self.scale_max)
            if end < start:
                start, end = end, start
            return list(range(start, end + 1))
        except Exception:
            return []


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    identity_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='survey_responses')
    submitted_at = models.DateTimeField(auto_now_add=True)
    cohort_json = models.JSONField(default=dict, blank=True)  # For demographic/cohort data
    meta_json = models.JSONField(default=dict, blank=True)  # For additional metadata
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['survey', 'identity_user']  # One response per user per survey
    
    def __str__(self):
        user_id = self.identity_user.username if self.identity_user else 'Anonymous'
        return f"{self.survey.title} - {user_id} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_absolute_url(self):
        return reverse('surveys:response_detail', kwargs={'pk': self.pk})
    
    @property
    def is_anonymous(self):
        """Check if this response is completely anonymous"""
        return self.identity_user is None
    
    @property
    def answers_count(self):
        return self.answers.count()


class Answer(models.Model):
    MODERATION_STATUS = [
        ('OK', 'OK'),
        ('FLAGGED', 'Flagged for Review'),
        ('REDACTED', 'Redacted'),
    ]
    
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    value_text = models.TextField(blank=True)
    value_number = models.FloatField(null=True, blank=True)
    value_json = models.JSONField(default=dict, blank=True)  # For complex answers (matrix, ranking, etc.)
    is_signed = models.BooleanField(default=False)
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signed_answers')
    followup_opt_in = models.BooleanField(default=False)
    preferred_contact = models.TextField(blank=True)
    moderation_status = models.CharField(max_length=20, choices=MODERATION_STATUS, default='OK')
    flags_json = models.JSONField(default=dict, blank=True)  # For moderation flags
    
    class Meta:
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"{self.question.prompt[:30]}... - {self.response}"
    
    def get_absolute_url(self):
        return reverse('surveys:answer_detail', kwargs={'pk': self.pk})
    
    @property
    def display_value(self):
        """Get the display value based on question type"""
        if self.question.type in ['SHORT_TEXT', 'LONG_TEXT']:
            return self.value_text
        elif self.question.type in ['LIKERT', 'NPS', 'NUMBER']:
            return self.value_number
        elif self.question.type in ['MULTI', 'SINGLE', 'RANK']:
            return self.options.get('selected', [])
        elif self.question.type == 'DATE':
            return self.value_json.get('date')
        elif self.question.type == 'MATRIX':
            return self.value_json.get('matrix_data', {})
        return "N/A"
    
    @property
    def is_anonymous_answer(self):
        """Check if this answer should be treated as anonymous in reports"""
        if self.question.anonymity_mode == 'ANONYMOUS':
            return True
        elif self.question.anonymity_mode == 'ESCROW':
            return not self.followup_opt_in
        return False


class Invite(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='invites')
    email = models.EmailField(null=True, blank=True)  # Optional for anonymous surveys
    token = models.CharField(max_length=100, unique=True)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    meta_json = models.JSONField(default=dict, blank=True)  # For additional invite metadata
    
    class Meta:
        ordering = ['-expires_at']
    
    def __str__(self):
        email = self.email or 'Anonymous'
        return f"{self.survey.title} - {email} - {self.token[:8]}..."
    
    def get_absolute_url(self):
        return reverse('surveys:invite_detail', kwargs={'pk': self.pk})
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_used(self):
        return self.used_at is not None
    
    @property
    def is_valid(self):
        return not self.is_expired and not self.is_used


class ReportSnapshot(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='report_snapshots')
    computed_at = models.DateTimeField(auto_now_add=True)
    aggregates_json = models.JSONField(default=dict)  # For storing computed aggregates
    
    class Meta:
        ordering = ['-computed_at']
    
    def __str__(self):
        return f"{self.survey.title} - {self.computed_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_absolute_url(self):
        return reverse('surveys:report_snapshot_detail', kwargs={'pk': self.pk})
    
    @property
    def response_rate(self):
        """Calculate response rate as percentage"""
        total_invites = self.survey.invites.count()
        if total_invites == 0:
            return 0
        return (self.survey.response_count / total_invites) * 100
    
    @property
    def enps_score(self):
        """Calculate eNPS score from NPS questions"""
        nps_answers = Answer.objects.filter(
            question__type='NPS',
            response__survey=self.survey
        ).values_list('value_number', flat=True)
        
        if not nps_answers:
            return 0
        
        promoters = sum(1 for score in nps_answers if score >= 9)
        detractors = sum(1 for score in nps_answers if score <= 6)
        total = len(nps_answers)
        
        if total == 0:
            return 0
        
        return ((promoters - detractors) / total) * 100
