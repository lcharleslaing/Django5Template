from django.contrib import admin
from .models import Department, Person, Flow, Step, Task


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_filter = ['department']


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


class StepInline(admin.TabularInline):
    model = Step
    extra = 1
    inlines = [TaskInline]


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    inlines = [StepInline]
    list_display = ['name', 'start_date', 'is_active']
    actions = ['recalculate_dates']

    def recalculate_dates(self, request, queryset):
        for flow in queryset:
            flow.recalculate_dates()
        self.message_user(request, "Dates recalculated.")
    recalculate_dates.short_description = "Recalculate dates for selected flows"


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_filter = ['flow', 'is_completed']
    list_display = ['title', 'flow', 'get_status', 'planned_end_date', 'actual_end_date']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_filter = ['step__flow', 'is_completed']