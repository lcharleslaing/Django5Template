from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Avg, Min, Max
from django.utils import timezone
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from datetime import timedelta

from .models import Survey, Section, Question, Response, Answer, Invite, ReportSnapshot
from .forms import (
    SurveyForm, SectionForm, QuestionForm, ResponseForm, AnswerForm,
    InviteForm, BulkInviteForm, SurveyReportForm
)


def is_survey_admin(user):
    """Check if user has admin permissions for surveys"""
    return user.is_staff or user.has_perm('surveys.change_survey')


def is_survey_creator(user):
    """Check if user can create surveys"""
    return user.is_staff or user.has_perm('surveys.add_survey')


def is_survey_analyst(user):
    """Check if user can view survey reports"""
    return user.is_staff or user.has_perm('surveys.view_response')


def index(request):
    return redirect('surveys:list')


def my_invites(request):
    invites = []
    if request.user.is_authenticated:
        now = timezone.now()
        invites = Invite.objects.filter(email__iexact=request.user.email, used_at__isnull=True, expires_at__gt=now)
    return render(request, 'surveys/my_invites.html', {
        'invites': invites,
        'page_title': 'My Survey Invites',
    })


def results_index(request):
    surveys = Survey.objects.filter(status='PUBLISHED')
    return render(request, 'surveys/results_index.html', {
        'surveys': surveys,
        'page_title': 'Survey Results',
    })


def export_report(request, pk, format):
    # Placeholder: return HTTP response; later implement CSV/XLSX/PDF
    return HttpResponse(f"Export for survey {pk} as {format}")


def action_note(request, pk):
    # Placeholder page for manager action notes
    survey = get_object_or_404(Survey, pk=pk)
    return render(request, 'surveys/action_note.html', {
        'survey': survey,
        'page_title': 'Post-Survey Action Note',
    })


# Public Views
def survey_list(request):
    """Public view of published surveys"""
    surveys = Survey.objects.filter(
        status='PUBLISHED',
        publish_start__lte=timezone.now(),
        publish_end__gte=timezone.now()
    ).order_by('-publish_start')
    
    context = {
        'surveys': surveys,
        'page_title': 'Available Surveys'
    }
    return render(request, 'surveys/survey_list.html', context)


def survey_detail(request, pk):
    """Public view of survey details"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if not survey.is_active:
        messages.error(request, 'This survey is not currently active.')
        return redirect('surveys:survey_list')
    
    context = {
        'survey': survey,
        'page_title': survey.title
    }
    return render(request, 'surveys/survey_detail.html', context)


def survey_response(request, survey_pk, token=None):
    """Handle survey response submission"""
    survey = get_object_or_404(Survey, pk=survey_pk)
    
    if not survey.is_active:
        messages.error(request, 'This survey is not currently active.')
        return redirect('surveys:survey_list')
    
    # Check if user already responded
    if request.user.is_authenticated:
        existing_response = Response.objects.filter(
            survey=survey,
            identity_user=request.user
        ).first()
        if existing_response:
            messages.info(request, 'You have already completed this survey.')
            return redirect('surveys:response_detail', pk=existing_response.pk)
    
    # Handle token-based access
    invite = None
    if token:
        invite = get_object_or_404(Invite, token=token, survey=survey)
        if not invite.is_valid:
            messages.error(request, 'This invite link has expired or been used.')
            return redirect('surveys:survey_list')
    
    if request.method == 'POST':
        # Process survey response
        try:
            # Create or get response
            if request.user.is_authenticated:
                response, created = Response.objects.get_or_create(
                    survey=survey,
                    identity_user=request.user
                )
            else:
                # For anonymous responses, create without user
                response = Response.objects.create(survey=survey)
            
            # Process answers
            for section in survey.sections.all():
                for question in section.questions.all():
                    field_name = f'question_{question.pk}'
                    if field_name in request.POST:
                        value = request.POST[field_name]
                        
                        # Create answer based on question type
                        answer = Answer.objects.create(
                            response=response,
                            question=question
                        )
                        
                        if question.type in ['SHORT_TEXT', 'LONG_TEXT']:
                            answer.value_text = value
                            # Handle anonymity-specific fields
                            if question.anonymity_mode == 'ESCROW':
                                answer.followup_opt_in = request.POST.get(f'{field_name}_followup', False)
                                answer.preferred_contact = request.POST.get(f'{field_name}_contact', '')
                            if question.anonymity_mode in ['ESCROW', 'SIGNED']:
                                answer.is_signed = request.POST.get(f'{field_name}_signed', False)
                                if answer.is_signed and request.user.is_authenticated:
                                    answer.signed_by = request.user
                        
                        elif question.type in ['LIKERT', 'NPS', 'NUMBER']:
                            answer.value_number = float(value)
                        
                        elif question.type in ['MULTI', 'SINGLE', 'RANK']:
                            if question.type == 'MULTI':
                                # Handle multiple values
                                values = request.POST.getlist(field_name)
                                answer.value_json = {'selected': values}
                            else:
                                answer.value_json = {'selected': [value]}
                        
                        elif question.type == 'DATE':
                            answer.value_json = {'date': value}
                        
                        answer.save()
            
            # Mark invite as used if applicable
            if invite:
                invite.used_at = timezone.now()
                invite.save()
            
            messages.success(request, 'Thank you for completing the survey!')
            return redirect('surveys:response_complete', pk=response.pk)
            
        except Exception as e:
            messages.error(request, f'Error saving response: {str(e)}')
    
    # Get first question for initial display
    first_section = survey.sections.first()
    first_question = first_section.questions.first() if first_section else None
    
    context = {
        'survey': survey,
        'first_question': first_question,
        'invite': invite,
        'page_title': f'Complete: {survey.title}'
    }
    return render(request, 'surveys/survey_response.html', context)


def response_complete(request, pk):
    """Show completion message after survey response"""
    response = get_object_or_404(Response, pk=pk)
    
    context = {
        'response': response,
        'page_title': 'Survey Complete'
    }
    return render(request, 'surveys/response_complete.html', context)


# Admin Views
@login_required
@user_passes_test(is_survey_admin)
def survey_admin_list(request):
    """Admin view of all surveys"""
    surveys = Survey.objects.all().order_by('-created_at')
    
    context = {
        'surveys': surveys,
        'page_title': 'Survey Administration'
    }
    return render(request, 'surveys/admin/survey_list.html', context)


@login_required
@user_passes_test(is_survey_creator)
def survey_create(request):
    """Create new survey"""
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            messages.success(request, 'Survey created successfully!')
            return redirect('surveys:survey_edit', pk=survey.pk)
    else:
        form = SurveyForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Survey'
    }
    return render(request, 'surveys/admin/survey_form.html', context)


@login_required
@user_passes_test(is_survey_creator)
def survey_edit(request, pk):
    """Edit existing survey"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            messages.success(request, 'Survey updated successfully!')
            return redirect('surveys:survey_admin_list')
    else:
        form = SurveyForm(instance=survey)
    
    context = {
        'form': form,
        'survey': survey,
        'page_title': f'Edit: {survey.title}'
    }
    return render(request, 'surveys/admin/survey_form.html', context)


@login_required
@user_passes_test(is_survey_admin)
def survey_publish(request, pk):
    """Publish or unpublish a survey"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'publish':
            survey.status = 'PUBLISHED'
            survey.save()
            messages.success(request, 'Survey published successfully!')
        elif action == 'unpublish':
            survey.status = 'DRAFT'
            survey.save()
            messages.success(request, 'Survey unpublished successfully!')
        elif action == 'close':
            survey.status = 'CLOSED'
            survey.save()
            messages.success(request, 'Survey closed successfully!')
    
    return redirect('surveys:survey_admin_list')


@login_required
@user_passes_test(is_survey_admin)
def survey_invites(request, pk):
    """Manage survey invites"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        form = BulkInviteForm(request.POST)
        if form.is_valid():
            # Process bulk invites
            invite_type = form.cleaned_data['invite_type']
            expires_in_days = form.cleaned_data['expires_in_days']
            expires_at = timezone.now() + timedelta(days=expires_in_days)
            
            if invite_type == 'all_users':
                users = User.objects.filter(is_active=True)
                for user in users:
                    token = str(uuid.uuid4())
                    Invite.objects.create(
                        survey=survey,
                        email=user.email,
                        token=token,
                        expires_at=expires_at
                    )
                messages.success(request, f'Invites sent to {users.count()} users.')
            
            elif invite_type == 'manual_list':
                email_list = form.cleaned_data['email_list']
                emails = [email.strip() for email in email_list.split('\n') if email.strip()]
                for email in emails:
                    token = str(uuid.uuid4())
                    Invite.objects.create(
                        survey=survey,
                        email=email,
                        token=token,
                        expires_at=expires_at
                    )
                messages.success(request, f'Invites sent to {len(emails)} email addresses.')
            
            return redirect('surveys:survey_invites', pk=survey.pk)
    else:
        form = BulkInviteForm()
    
    invites = survey.invites.all().order_by('-expires_at')
    
    context = {
        'survey': survey,
        'form': form,
        'invites': invites,
        'page_title': f'Manage Invites: {survey.title}'
    }
    return render(request, 'surveys/admin/survey_invites.html', context)


# Reporting Views
@login_required
@user_passes_test(is_survey_analyst)
def survey_reports(request, pk):
    """View survey reports and analytics"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method == 'POST':
        form = SurveyReportForm(request.POST)
        if form.is_valid():
            # Generate report based on form data
            report_data = generate_survey_report(survey, form.cleaned_data)
            context = {
                'survey': survey,
                'report_data': report_data,
                'form': form,
                'page_title': f'Reports: {survey.title}'
            }
            return render(request, 'surveys/reports/survey_report.html', context)
    else:
        form = SurveyReportForm()
    
    # Basic stats
    total_responses = survey.response_count
    response_rate = 0
    if survey.invites.count() > 0:
        response_rate = (total_responses / survey.invites.count()) * 100
    
    context = {
        'survey': survey,
        'form': form,
        'total_responses': total_responses,
        'response_rate': response_rate,
        'page_title': f'Reports: {survey.title}'
    }
    return render(request, 'surveys/reports/survey_reports.html', context)


def generate_survey_report(survey, options):
    """Generate survey report data based on options"""
    report_data = {
        'summary': {},
        'questions': [],
        'cohorts': {},
        'sentiment': {}
    }
    
    # Get responses based on date filters
    responses = survey.responses.all()
    if options.get('date_from'):
        responses = responses.filter(submitted_at__gte=options['date_from'])
    if options.get('date_to'):
        responses = responses.filter(submitted_at__lte=options['date_to'])
    
    # Summary statistics
    report_data['summary'] = {
        'total_responses': responses.count(),
        'response_rate': (responses.count() / survey.invites.count() * 100) if survey.invites.count() > 0 else 0,
        'date_range': {
            'from': options.get('date_from'),
            'to': options.get('date_to')
        }
    }
    
    # Question-level analysis
    for section in survey.sections.all():
        for question in section.questions.all():
            question_data = {
                'question': question,
                'answers': [],
                'stats': {}
            }
            
            answers = Answer.objects.filter(
                question=question,
                response__in=responses
            )
            
            if question.type in ['LIKERT', 'NPS', 'NUMBER']:
                numeric_answers = [a.value_number for a in answers if a.value_number is not None]
                if numeric_answers:
                    question_data['stats'] = {
                        'count': len(numeric_answers),
                        'mean': sum(numeric_answers) / len(numeric_answers),
                        'median': sorted(numeric_answers)[len(numeric_answers) // 2],
                        'min': min(numeric_answers),
                        'max': max(numeric_answers)
                    }
            
            elif question.type in ['MULTI', 'SINGLE']:
                choice_counts = {}
                for answer in answers:
                    selected = answer.value_json.get('selected', [])
                    for choice in selected:
                        choice_counts[choice] = choice_counts.get(choice, 0) + 1
                question_data['stats'] = choice_counts
            
            question_data['answers'] = list(answers)
            report_data['questions'].append(question_data)
    
    return report_data


# HTMX Views for dynamic updates
@require_http_methods(["POST"])
@csrf_exempt
def reorder_sections(request, survey_pk):
    """HTMX endpoint for reordering sections"""
    if not request.user.is_authenticated or not is_survey_admin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        section_orders = data.get('section_orders', [])
        
        for item in section_orders:
            section_id = item.get('id')
            new_order = item.get('order')
            if section_id and new_order is not None:
                Section.objects.filter(id=section_id).update(order=new_order)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def reorder_questions(request, section_pk):
    """HTMX endpoint for reordering questions"""
    if not request.user.is_authenticated or not is_survey_admin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        question_orders = data.get('question_orders', [])
        
        for item in question_orders:
            question_id = item.get('id')
            new_order = item.get('order')
            if question_id and new_order is not None:
                Question.objects.filter(id=question_id).update(order=new_order)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# API Views for mobile/JS consumption
def survey_api_detail(request, pk):
    """API endpoint for survey details"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if not survey.is_active:
        return JsonResponse({'error': 'Survey not active'}, status=400)
    
    data = {
        'id': survey.pk,
        'title': survey.title,
        'description': survey.description,
        'sections': []
    }
    
    for section in survey.sections.all():
        section_data = {
            'id': section.pk,
            'title': section.title,
            'description': section.description,
            'order': section.order,
            'questions': []
        }
        
        for question in section.questions.all():
            question_data = {
                'id': question.pk,
                'type': question.type,
                'prompt': question.prompt,
                'help_text': question.help_text,
                'required': question.required,
                'anonymity_mode': question.anonymity_mode,
                'order': question.order
            }
            
            if question.is_scale_question:
                question_data.update({
                    'scale_min': question.scale_min,
                    'scale_max': question.scale_max
                })
            
            if question.options:
                question_data['options'] = question.options
            
            section_data['questions'].append(question_data)
        
        data['sections'].append(section_data)
    
    return JsonResponse(data)
