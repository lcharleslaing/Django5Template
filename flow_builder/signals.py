from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Step, Flow, Task
import datetime


@receiver(post_save, sender=Step)
def propagate_completion(sender, instance: Step, **kwargs):
    if instance.actual_end_date and not kwargs.get('created', False):  # Only on update with actual end set
        # Recalc dependents
        for dependent in instance.dependents.filter(flow=instance.flow):
            # Dependent's planned/actual start = max(its current, this instance's actual end)
            new_start = max(dependent.planned_start_date or instance.flow.start_date, instance.actual_end_date)
            dependent.planned_start_date = new_start
            dependent.planned_end_date = new_start + datetime.timedelta(days=dependent.time_allotted_days)
            dependent.save(skip_recalc=True)  # Skip recalc to prevent recursion


@receiver(post_save, sender=Task)
def update_step_progress(sender, instance: Task, **kwargs):
    """Update step progress when a task is completed or created."""
    if instance.step:
        # If task was just completed, set completion tracking
        if instance.is_completed and not instance.completed_at:
            instance.completed_at = timezone.now()
            instance.save(update_fields=['completed_at'], skip_recalc=True)
        
        instance.step.update_progress()
        instance.step.save(update_fields=['progress_percentage', 'is_completed', 'actual_end_date'], skip_recalc=True)
        
        # If step is now complete, trigger flow recalculation
        if instance.step.is_completed:
            instance.step.flow.recalculate_dates()


@receiver(pre_save, sender=Task)
def set_task_due_date(sender, instance: Task, **kwargs):
    """Set task due date based on step's planned end date if not already set."""
    if not instance.due_date and instance.step and instance.step.planned_end_date:
        instance.due_date = instance.step.planned_end_date
