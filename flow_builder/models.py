from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_date
import datetime
from typing import List, Optional


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='persons')

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Flow(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)  # Overall flow start
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Flag to prevent recursion during recalculation
    _recalculating = False

    def __str__(self):
        return self.name

    def get_steps_in_order(self) -> List['Step']:
        """Topological sort of steps based on dependencies to get execution order."""
        steps = list(self.steps.all())
        visited = set()
        rec_stack = set()
        order = []

        def visit(step):
            if step in rec_stack:
                raise ValidationError(f"Cycle detected in dependencies involving step: {step.title}")
            if step not in visited:
                visited.add(step)
                rec_stack.add(step)
                for dep in step.dependencies.all():
                    if dep.flow == self:  # Only intra-flow deps
                        visit(dep)
                rec_stack.remove(step)
                order.append(step)

        for step in steps:
            if step not in visited:
                visit(step)

        return order

    def recalculate_dates(self):
        """Recalculate all planned dates for steps based on start_date, deps, and time_allotted.
        Call this after creating/updating steps or flow start_date."""
        # Prevent recursion
        if self._recalculating:
            return
        self._recalculating = True
        
        try:
            ordered_steps = self.get_steps_in_order()
            current_date = self.start_date

            for step in ordered_steps:
                # Planned start: max of flow start or latest dep actual/planned end
                dep_end = current_date
                for dep in step.dependencies.all():
                    if dep.flow == self:
                        # Use actual end date if available, otherwise planned end date
                        dep_end_date = dep.actual_end_date or dep.planned_end_date or current_date
                        dep_end = max(dep_end, dep_end_date)

                # If step has actual start date, use it as the base
                if step.actual_start_date:
                    step.planned_start_date = step.actual_start_date
                    step.planned_end_date = step.actual_start_date + datetime.timedelta(days=step.time_allotted_days)
                else:
                    step.planned_start_date = dep_end
                    step.planned_end_date = dep_end + datetime.timedelta(days=step.time_allotted_days)

                # If step has actual end date, use it as the planned end date
                if step.actual_end_date:
                    step.planned_end_date = step.actual_end_date

                # If no actual end yet, but planned is set, that's fine; actuals will trigger updates
                step.save(update_fields=['planned_start_date', 'planned_end_date'], skip_recalc=True)
                current_date = step.planned_end_date + datetime.timedelta(days=1)  # Assume 1 day buffer if sequential
        finally:
            self._recalculating = False

    def save(self, *args, **kwargs):
        # Check if this is a new instance or if start_date changed
        is_new = self.pk is None
        if not is_new:
            # Get the old instance to compare
            old_instance = Flow.objects.get(pk=self.pk)
            start_date_changed = old_instance.start_date != self.start_date
        else:
            start_date_changed = False
        
        # Save the instance first
        super().save(*args, **kwargs)
        
        # Only recalculate dates if it's a new flow or start_date changed
        if not self._recalculating and (is_new or start_date_changed):
            self.recalculate_dates()


class Step(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_allotted_days = models.PositiveIntegerField(default=1, help_text="Days allotted for this step")
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents', help_text="Steps that must complete before this one starts")

    # Dates: Planned based on flow/deps; Actual set by user on completion
    planned_start_date = models.DateField(null=True, blank=True)
    planned_end_date = models.DateField(null=True, blank=True)
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0, help_text="Percentage complete based on tasks")

    class Meta:
        unique_together = ['flow', 'title']  # Prevent duplicate titles per flow

    def __str__(self):
        return f"{self.title} in {self.flow.name}"

    def save(self, *args, **kwargs):
        # Extract custom arguments
        skip_recalc = kwargs.pop('skip_recalc', False)
        
        # Check if this is a recursive call from recalculate_dates or signals
        if kwargs.get('update_fields') or skip_recalc:
            # This is a call from recalculate_dates or signals, don't trigger it again
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            if self.flow:
                self.flow.recalculate_dates()  # Trigger recalc on save

    def calculate_progress(self):
        """Calculate progress percentage based on completed tasks."""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(is_completed=True).count()
        return int((completed_tasks / total_tasks) * 100)
    
    def update_progress(self):
        """Update progress percentage and check if step should be marked complete."""
        self.progress_percentage = self.calculate_progress()
        
        # If all tasks are complete, mark the step as complete
        if self.progress_percentage == 100 and not self.is_completed:
            self.is_completed = True
            if not self.actual_end_date:
                self.actual_end_date = timezone.now().date()
        
        # If not all tasks are complete, unmark completion
        elif self.progress_percentage < 100 and self.is_completed:
            self.is_completed = False
            self.actual_end_date = None

    def get_status(self):
        today = timezone.now().date()
        if self.is_completed:
            return "Completed"
        elif self.actual_start_date and not self.actual_end_date:
            return "In Progress"
        elif self.planned_start_date and today >= self.planned_end_date:
            return "Overdue"
        elif self.planned_start_date and today >= self.planned_start_date:
            return "Due Soon"
        else:
            return "Not Started"


class Task(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    responsible_person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_tasks')
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.step.title})"
    
    def can_be_completed_by(self, user):
        """Check if the given user can complete this task."""
        if not user.is_authenticated:
            return False
        # Admin can complete any task
        if user.is_staff:
            return True
        # Assigned person can complete their task
        if self.responsible_person and hasattr(user, 'profile') and user.profile.person == self.responsible_person:
            return True
        # If no one is assigned, anyone can complete it
        if not self.responsible_person:
            return True
        return False