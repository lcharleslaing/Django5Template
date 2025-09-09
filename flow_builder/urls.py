from django.urls import path
from . import views

app_name = 'flow_builder'

urlpatterns = [
    path('', views.flow_list, name='flow_list'),
    path('create/', views.CreateFlowView.as_view(), name='create_flow'),
    path('flow/<int:pk>/', views.flow_detail, name='flow_detail'),
    path('flow/<int:pk>/edit/', views.FlowEditView.as_view(), name='flow_edit'),
    path('flow/<int:pk>/delete/', views.FlowDeleteView.as_view(), name='flow_delete'),
    path('flow/<int:flow_pk>/step/add/', views.StepCreateView.as_view(), name='add_step'),
    path('flow/<int:flow_pk>/step/<int:pk>/edit/', views.StepEditView.as_view(), name='edit_step'),
    path('flow/<int:flow_pk>/step/<int:step_pk>/task/add/', views.TaskCreateView.as_view(), name='add_task'),
    path('flow/<int:flow_pk>/step/<int:step_pk>/task/<int:pk>/edit/', views.TaskEditView.as_view(), name='edit_task'),
    path('task/<int:pk>/edit/', views.TaskEditView.as_view(), name='edit_task_direct'),
    path('flow/<int:flow_pk>/step/<int:pk>/start/', views.start_step, name='start_step'),
    path('flow/<int:flow_pk>/step/<int:pk>/complete/', views.complete_step, name='complete_step'),
]
