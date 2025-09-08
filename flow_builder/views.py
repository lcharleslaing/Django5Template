from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from .models import Flow, Step, Task, Person
from .forms import FlowForm, StepForm, TaskForm


class CreateFlowView(CreateView):
    model = Flow
    form_class = FlowForm
    template_name = 'flow_builder/flow_form.html'
    success_url = reverse_lazy('flow_builder:flow_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['step_form'] = StepForm()
        return context

    def form_valid(self, form):
        self.object = form.save()
        self.object.recalculate_dates()
        return super().form_valid(form)


def flow_list(request):
    flows = Flow.objects.all()
    return render(request, 'flow_builder/flow_list.html', {'flows': flows})


def flow_detail(request, pk):
    flow = get_object_or_404(Flow, pk=pk)
    ordered_steps = flow.get_steps_in_order()
    context = {'flow': flow, 'steps': ordered_steps}
    return render(request, 'flow_builder/flow_detail.html', context)


class FlowEditView(UpdateView):
    model = Flow
    form_class = FlowForm
    template_name = 'flow_builder/flow_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('flow_builder:flow_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        self.object = form.save()
        self.object.recalculate_dates()
        messages.success(self.request, 'Flow updated successfully!')
        return super().form_valid(form)


class StepCreateView(CreateView):
    model = Step
    form_class = StepForm
    template_name = 'flow_builder/step_form.html'
    
    def get_flow(self):
        return get_object_or_404(Flow, pk=self.kwargs['flow_pk'])
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['flow'] = self.get_flow()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flow'] = self.get_flow()
        context['people'] = Person.objects.all()
        return context
    
    def form_valid(self, form):
        form.instance.flow = self.get_flow()
        self.object = form.save()
        self.object.flow.recalculate_dates()
        messages.success(self.request, 'Step added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('flow_builder:flow_detail', kwargs={'pk': self.get_flow().pk})


class StepEditView(UpdateView):
    model = Step
    form_class = StepForm
    template_name = 'flow_builder/step_form.html'
    
    def get_flow(self):
        return get_object_or_404(Flow, pk=self.kwargs['flow_pk'])
    
    def get_object(self):
        return get_object_or_404(Step, pk=self.kwargs['pk'], flow=self.get_flow())
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['flow'] = self.get_flow()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flow'] = self.get_flow()
        context['step'] = self.get_object()
        context['people'] = Person.objects.all()
        return context
    
    def form_valid(self, form):
        self.object = form.save()
        self.object.flow.recalculate_dates()
        messages.success(self.request, 'Step updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('flow_builder:flow_detail', kwargs={'pk': self.get_flow().pk})


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'flow_builder/task_form.html'
    
    def get_flow(self):
        return get_object_or_404(Flow, pk=self.kwargs['flow_pk'])
    
    def get_step(self):
        return get_object_or_404(Step, pk=self.kwargs['step_pk'], flow=self.get_flow())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flow'] = self.get_flow()
        context['step'] = self.get_step()
        context['task'] = None  # No task for create view
        return context
    
    def form_valid(self, form):
        form.instance.step = self.get_step()
        self.object = form.save()
        messages.success(self.request, 'Task added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('flow_builder:flow_detail', kwargs={'pk': self.get_flow().pk})


class TaskEditView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'flow_builder/task_form.html'
    
    def get_flow(self):
        return get_object_or_404(Flow, pk=self.kwargs['flow_pk'])
    
    def get_step(self):
        return get_object_or_404(Step, pk=self.kwargs['step_pk'], flow=self.get_flow())
    
    def get_object(self):
        return get_object_or_404(Task, pk=self.kwargs['pk'], step=self.get_step())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flow'] = self.get_flow()
        context['step'] = self.get_step()
        context['task'] = self.get_object()
        return context
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('flow_builder:flow_detail', kwargs={'pk': self.get_flow().pk})


def start_step(request, flow_pk, pk):
    step = get_object_or_404(Step, pk=pk, flow_id=flow_pk)
    if not step.actual_start_date:
        step.actual_start_date = timezone.now().date()
        step.save()
        messages.success(request, f'Step "{step.title}" started!')
    else:
        messages.info(request, f'Step "{step.title}" was already started.')
    return redirect('flow_builder:flow_detail', pk=flow_pk)


def complete_step(request, flow_pk, pk):
    step = get_object_or_404(Step, pk=pk, flow_id=flow_pk)
    if not step.actual_end_date:
        step.actual_end_date = timezone.now().date()
        step.is_completed = True
        step.save()
        messages.success(request, f'Step "{step.title}" completed!')
    else:
        messages.info(request, f'Step "{step.title}" was already completed.')
    return redirect('flow_builder:flow_detail', pk=flow_pk)