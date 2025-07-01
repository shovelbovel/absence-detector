from django.urls import path, include
from . import views
from .views import (
    register, custom_login, home, custom_logout,
    manager_dashboard, team_dashboard, rh_dashboard,
    export_absences, export_absences_csv, send_message,
    inbox, log_activity, update_status, justify_absence,
    declare_absence, export_absence_pdf, get_rh_data,
    justify_absence_view, landing_page
)

app_name = 'presence'  # Namespace de l'application

urlpatterns = [
    # Authentification
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    
    # Pages principales
    path('', landing_page, name='landing_page'),
    path('home/', home, name='home'),
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('team/', team_dashboard, name='team_dashboard'),
    path('rh/', rh_dashboard, name='rh_dashboard'),
    
    # Gestion des absences
    path('justify-absence/', justify_absence, name='justify_absence'),
    path('declare-absence/', declare_absence, name='declare_absence'),
    path('justify-absence/action/', justify_absence_view, name='justify_absence_action'),
    
    # Exports
    path('export-absences/', export_absences, name='export_absences'),
    path('export-absences-csv/', export_absences_csv, name='export_absences_csv'),
    path('export-absence-pdf/<int:absence_id>/', export_absence_pdf, name='export_absence_pdf'),
    
    # Messagerie
    path('messaging/inbox/', inbox, name='inbox'),
    path('messaging/send/<int:recipient_id>/', send_message, name='send_message'),
    
    # API
    path('api/activity/', log_activity, name='log_activity'),
    path('api/status/', update_status, name='update_status'),
    path('api/rh-data/', get_rh_data, name='get_rh_data'),
    # path('api/notifications/', include('presence.api.urls')),  # À implémenter si besoin
]