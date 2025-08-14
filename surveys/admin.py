from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Survey, Section, Question, Response, Answer, Invite, ReportSnapshot


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['type', 'prompt', 'anonymity_mode', 'required', 'order']
    ordering = ['order']


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ['title', 'description', 'order']
    ordering = ['order']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_by', 'publish_start', 'publish_end', 'response_count', 'is_active_display']
    list_filter = ['status', 'created_by', 'publish_start', 'publish_end']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'response_count', 'sections_count']
    inlines = [SectionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Publishing', {
            'fields': ('status', 'publish_start', 'publish_end', 'k_threshold')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_display.short_description = 'Status'
    
    def response_count(self, obj):
        return obj.response_count
    response_count.short_description = 'Responses'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'survey', 'order', 'questions_count']
    list_filter = ['survey']
    search_fields = ['title', 'survey__title']
    ordering = ['survey', 'order']
    inlines = [QuestionInline]
    
    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['prompt_short', 'section', 'type', 'anonymity_mode', 'required', 'order']
    list_filter = ['type', 'anonymity_mode', 'required', 'section__survey']
    search_fields = ['prompt', 'section__title', 'section__survey__title']
    ordering = ['section', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('section', 'type', 'prompt', 'help_text', 'required', 'order')
        }),
        ('Anonymity & Logic', {
            'fields': ('anonymity_mode', 'logic_json')
        }),
        ('Options & Scales', {
            'fields': ('options_json', 'scale_min', 'scale_max'),
            'classes': ('collapse',)
        }),
    )
    
    def prompt_short(self, obj):
        return obj.prompt[:50] + "..." if len(obj.prompt) > 50 else obj.prompt
    prompt_short.short_description = 'Prompt'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'display_value', 'is_signed', 'moderation_status']
    fields = ['question', 'display_value', 'is_signed', 'moderation_status']
    
    def display_value(self, obj):
        return obj.display_value
    display_value.short_description = 'Value'


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'identity_display', 'submitted_at', 'answers_count', 'is_anonymous_display']
    list_filter = ['survey', 'submitted_at', 'survey__status']
    search_fields = ['survey__title', 'identity_user__username', 'identity_user__email']
    readonly_fields = ['submitted_at', 'answers_count']
    inlines = [AnswerInline]
    
    fieldsets = (
        ('Response Information', {
            'fields': ('survey', 'identity_user', 'submitted_at')
        }),
        ('Metadata', {
            'fields': ('cohort_json', 'meta_json'),
            'classes': ('collapse',)
        }),
    )
    
    def identity_display(self, obj):
        if obj.identity_user:
            return obj.identity_user.username
        return 'Anonymous'
    identity_display.short_description = 'Respondent'
    
    def is_anonymous_display(self, obj):
        if obj.is_anonymous:
            return format_html('<span style="color: orange;">Anonymous</span>')
        else:
            return format_html('<span style="color: blue;">Identified</span>')
    is_anonymous_display.short_description = 'Anonymity'
    
    def answers_count(self, obj):
        return obj.answers_count
    answers_count.short_description = 'Answers'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question_short', 'response', 'display_value', 'question_anonymity_mode', 'moderation_status']
    list_filter = ['question__type', 'question__anonymity_mode', 'moderation_status', 'is_signed']
    search_fields = ['question__prompt', 'response__survey__title', 'value_text']
    readonly_fields = ['response', 'question', 'display_value']
    
    fieldsets = (
        ('Answer Information', {
            'fields': ('response', 'question', 'display_value')
        }),
        ('Values', {
            'fields': ('value_text', 'value_number', 'value_json'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_signed', 'signed_by', 'followup_opt_in', 'preferred_contact')
        }),
        ('Moderation', {
            'fields': ('moderation_status', 'flags_json'),
            'classes': ('collapse',)
        }),
    )
    
    def question_short(self, obj):
        return obj.question.prompt[:50] + "..." if len(obj.question.prompt) > 50 else obj.question.prompt
    question_short.short_description = 'Question'
    
    def question_anonymity_mode(self, obj):
        return obj.question.anonymity_mode
    question_anonymity_mode.short_description = 'Anonymity Mode'
    
    def display_value(self, obj):
        return obj.display_value
    display_value.short_description = 'Value'


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['survey', 'email_display', 'token_short', 'expires_at', 'status_display']
    list_filter = ['survey', 'expires_at', 'used_at']
    search_fields = ['survey__title', 'email', 'token']
    readonly_fields = ['token', 'status_display']
    
    fieldsets = (
        ('Invite Information', {
            'fields': ('survey', 'email', 'token', 'expires_at')
        }),
        ('Usage', {
            'fields': ('used_at', 'meta_json'),
            'classes': ('collapse',)
        }),
    )
    
    def email_display(self, obj):
        return obj.email or 'Anonymous'
    email_display.short_description = 'Email'
    
    def token_short(self, obj):
        return obj.token[:8] + "..."
    token_short.short_description = 'Token'
    
    def status_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.is_used:
            return format_html('<span style="color: orange;">Used</span>')
        else:
            return format_html('<span style="color: green;">Valid</span>')
    status_display.short_description = 'Status'


@admin.register(ReportSnapshot)
class ReportSnapshotAdmin(admin.ModelAdmin):
    list_display = ['survey', 'computed_at', 'response_rate', 'enps_score']
    list_filter = ['survey', 'computed_at']
    search_fields = ['survey__title']
    readonly_fields = ['computed_at', 'response_rate', 'enps_score']
    
    fieldsets = (
        ('Snapshot Information', {
            'fields': ('survey', 'computed_at')
        }),
        ('Aggregates', {
            'fields': ('aggregates_json',),
            'classes': ('collapse',)
        }),
    )
    
    def response_rate(self, obj):
        return f"{obj.response_rate:.1f}%"
    response_rate.short_description = 'Response Rate'
    
    def enps_score(self, obj):
        return f"{obj.enps_score:.1f}"
    enps_score.short_description = 'eNPS Score'
