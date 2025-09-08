from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Step, Flow
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
            dependent.save()  # This will trigger further propagation via the model's save()
