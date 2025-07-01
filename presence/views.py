                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            # presence/views.py
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout as auth_logout
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
import csv
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
from django import forms
from django.db.models import Count
from .models import Employee, ActivityLog, AbsenceReport, Message, Presence, Notification
from .utils import calculate_monthly_stats
from .forms import MessageForm, AbsenceReportForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Employee.objects.create(user=user, department='', position='', name=user.username)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'presence/register.html', {'form': form})

from django.db.models import Q

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('presence:home')
    return render(request, 'presence/landing_page.html')

@login_required
def home(request):
    context = {}
    
    # Vérifier que l'utilisateur a un profil employee
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'Profil employé non trouvé')
        return redirect('logout')  # Redirige vers la déconnexion pour forcer la mise à jour du profil
    
    employee = request.user.employee
    context['employee'] = employee
    
    # Récupérer les messages récents
    recent_messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')[:5]
    context['recent_messages'] = recent_messages
    
    # Données pour les managers
    if employee.role == 'manager':
        team = Employee.objects.filter(department=employee.department)
        absences_today = AbsenceReport.objects.filter(
            employee__in=team, 
            date=date.today(),
            justified=False  # Ne montrer que les absences non justifiées
        )
        context.update({
            'team_absences_today': absences_today,
            'team': team,
            'absence_count': absences_today.count()
        })
    
    # Données pour les RH
    elif employee.role == 'rh':
        total_absences = AbsenceReport.objects.count()
        unjustified_absences = AbsenceReport.objects.filter(justified=False).count()
        context.update({
            'total_absences': total_absences,
            'unjustified_absences': unjustified_absences,
            'justification_rate': round(((total_absences - unjustified_absences) / total_absences * 100), 2) if total_absences > 0 else 100
        })
    
    # Données communes à tous les utilisateurs
    user_absences = AbsenceReport.objects.filter(employee=employee).order_by('-date')[:5]
    context['recent_absences'] = user_absences
    
    return render(request, 'presence/home.html', context)

class JustifyAbsenceForm(forms.ModelForm):
    class Meta:
        model = AbsenceReport
        fields = ['justification']

def custom_login(request):
    # Si l'utilisateur est déjà connecté, rediriger selon son rôle
    if request.user.is_authenticated:
        if hasattr(request.user, 'employee'):
            if request.user.employee.role == 'rh':
                return redirect('presence:rh_dashboard')
            elif request.user.employee.role == 'manager':
                return redirect('presence:manager_dashboard')
        return redirect('presence:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Vérifier si l'utilisateur a un profil employé
            if not hasattr(user, 'employee'):
                messages.error(request, 'Aucun profil employé associé à ce compte.')
                return redirect('presence:login')
                
            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username}!')
            
            # Redirection selon le rôle
            if user.employee.role == 'rh':
                return redirect('presence:rh_dashboard')
            elif user.employee.role == 'manager':
                return redirect('presence:manager_dashboard')
            return redirect('presence:home')
        else:
            messages.error(request, 'Identifiants invalides. Veuillez réessayer.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'presence/login.html', {
        'form': form,
        'title': 'Connexion'
    })

@login_required
def manager_dashboard(request):
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'manager':
        return redirect('home')
    if request.user.employee.role != 'manager':
        messages.error(request, 'Accès non autorisé - Rôle Manager requis')
        return redirect('home')
    
    # Récupérer les absences de l'équipe du manager
    team_absences = AbsenceReport.objects.filter(
        employee__department=request.user.employee.department
    ).select_related('employee').order_by('-date')
    
    return render(request, 'presence/manager_dashboard.html', {
        'absences': team_absences,
        'notifications': request.user.notifications.all()[:5]  # Afficher les 5 dernières notifications
    })

@login_required
def team_dashboard(request):
    # Vérifier que l'utilisateur a un profil employee et le bon rôle
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'Profil employé non trouvé')
        return redirect('home')
    if request.user.employee.role != 'manager':
        messages.error(request, 'Accès non autorisé - Rôle Manager requis')
        return redirect('home')
    
    # Récupérer les données de l'équipe
    team = Employee.objects.filter(department=request.user.employee.department)
    
    # Mettre à jour les statuts des employés en fonction de leurs absences justifiées
    today = timezone.now().date()
    for employee in team:
        # Vérifier si l'employé a une absence justifiée aujourd'hui
        has_justified_absence = AbsenceReport.objects.filter(
            employee=employee,
            date=today,
            justified=True,
            status='present'
        ).exists()
        
        if has_justified_absence and employee.status != 'present':
            employee.status = 'present'
            employee.save()
    
    # Mettre à jour la liste des statuts de l'équipe
    team = Employee.objects.filter(department=request.user.employee.department)
    team_status = [{'emp': emp, 'status': emp.status} for emp in team]
    
    # Récupérer uniquement les absences non justifiées d'aujourd'hui
    absences_today = AbsenceReport.objects.filter(
        employee__in=team,
        date=today,
        justified=False  # Ne montrer que les absences non justifiées
    ).select_related('employee')
    
    absence_count_today = absences_today.count()
    
    return render(request, 'presence/manager.html', {
        'absences': absences_today,
        'team_status': team_status,
        'absence_count_today': absence_count_today,
        'notifications': request.user.notifications.filter(is_read=False)
    })

@login_required
def rh_dashboard(request):
    # Vérifier que l'utilisateur a un profil employee et le bon rôle
    if not hasattr(request.user, 'employee'):
        messages.error(request, 'Profil employé non trouvé')
        return redirect('home')
    if request.user.employee.role != 'rh':
        messages.error(request, 'Accès non autorisé - Rôle RH requis')
        return redirect('home')
    
    # Statistiques de présence par jour
    presences = Presence.objects.values('date').annotate(count=Count('id')).order_by('date')
    presence_data = {
        'labels': [p['date'].strftime('%d/%m') for p in presences],
        'values': [p['count'] for p in presences]
    }
    # Statistiques par statut
    status_counts = Employee.objects.values('status').annotate(count=Count('id'))
    status_data = {
        'labels': [s['status'] for s in status_counts],
        'values': [s['count'] for s in status_counts]
    }
    return render(request, 'presence/rh.html', {
        'presence_data': presence_data,
        'status_data': status_data,
    })

@login_required
def send_message(request, recipient_id=None):
    """
    Vue pour envoyer un message à un utilisateur spécifique.
    Si un recipient_id est fourni, le formulaire sera pré-rempli avec ce destinataire.
    Si aucun recipient_id n'est fourni, l'utilisateur pourra sélectionner un destinataire.
    """
    recipient = None
    
    # Récupérer le destinataire si l'ID est fourni
    if recipient_id:
        try:
            recipient = User.objects.get(id=recipient_id)
            # Vérifier que l'utilisateur ne s'envoie pas de message à lui-même
            if recipient == request.user:
                messages.error(request, "Vous ne pouvez pas vous envoyer un message à vous-même.")
                return redirect('presence:inbox')
        except (User.DoesNotExist, ValueError):
            messages.error(request, 'Destinataire introuvable.')
            return redirect('presence:inbox')
    
    # Traitement du formulaire
    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                messages.success(request, 'Votre message a été envoyé avec succès.')
                return redirect('presence:inbox')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de l\'envoi du message : {str(e)}')
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        # Initialiser le formulaire avec le destinataire s'il est spécifié
        initial = {}
        if recipient:
            initial = {'recipient': recipient}
        form = MessageForm(user=request.user, initial=initial)
    
    context = {
        'form': form,
        'recipient': recipient,
        'page_title': 'Nouveau message',
    }
    
    return render(request, 'presence/send_message.html', context)

@login_required
def inbox(request):
    # Récupérer les messages reçus par l'utilisateur connecté
    received_messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    # Récupérer les messages envoyés par l'utilisateur connecté
    sent_messages = Message.objects.filter(sender=request.user).order_by('-sent_at')
    
    return render(request, 'presence/inbox.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })

@csrf_exempt
@login_required
def log_activity(request):
    if request.method == 'POST':
        ActivityLog.objects.create(
            employee=request.user.employee,
            activity_type='mouse'
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
@login_required
def update_status(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        new_status = data.get('status')
        if new_status in dict(Employee.STATUS_CHOICES):
            employee = request.user.employee
            employee.status = new_status
            employee.save()
            return JsonResponse({'status': 'updated'})
        return JsonResponse({'error': 'Invalid status'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='RH').exists())
def export_absences(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="absences.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Département', 'Date', 'Heure début', 'Heure fin', 'Justifié'])
    absences = AbsenceReport.objects.select_related('employee__user').all()
    for absence in absences:
        writer.writerow([
            absence.employee.user.get_full_name(),
            absence.employee.department,
            absence.date,
            absence.start_time,
            absence.end_time,
            'Oui' if absence.justified else 'Non'
        ])
    return response

@login_required
@user_passes_test(lambda u: u.groups.filter(name='RH').exists())
def export_absences_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="absences.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Département', 'Statut', 'Date'])
    for presence in Presence.objects.all():
        writer.writerow([
            presence.employee.name,
            presence.employee.department,
            presence.employee.status,
            presence.date.strftime('%d/%m/%Y')
        ])
    return response

@login_required
def justify_absence(request):
    # Vérifier que l'utilisateur est un employé (pas RH ni manager)
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'employe':
        messages.error(request, 'Seuls les employés peuvent justifier des absences.')
        return redirect('home')
        
    employee = request.user.employee
    absences = AbsenceReport.objects.filter(
        employee=employee,
        justified=False
    ).order_by('-date')
    
    if request.method == 'POST':
        absence_id = request.POST.get('absence_id')
        justification_file = request.FILES.get('justification_file')
        
        if absence_id and justification_file:
            # Vérifier que le fichier est un PDF
            if not justification_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Veuillez téléverser un fichier PDF valide.')
                return redirect('justify_absence')
                
            # Vérifier la taille du fichier (max 5MB)
            if justification_file.size > 5 * 1024 * 1024:
                messages.error(request, 'La taille du fichier ne doit pas dépasser 5 Mo.')
                return redirect('justify_absence')
                
            try:
                absence = AbsenceReport.objects.get(id=absence_id, employee=employee)
                absence.justification_file = justification_file
                absence.justified = True
                absence.save()
                messages.success(request, 'Justificatif téléversé avec succès')
                
                # Envoyer une notification au manager
                manager = User.objects.filter(
                    employee__department=employee.department,
                    employee__role='manager'
                ).first()
                
                if manager:
                    Notification.objects.create(
                        user=manager,
                        title=f'Nouvelle justification d\'absence',
                        message=f'{employee.user.get_full_name()} a justifié une absence du {absence.date}',
                        link=f'/manager/absences/'
                    )
                    
            except AbsenceReport.DoesNotExist:
                messages.error(request, 'Absence introuvable')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue: {str(e)}')
                
            return redirect('justify_absence')
        else:
            messages.error(request, 'Veuillez sélectionner un fichier PDF')
            
    return render(request, 'presence/justify_absence.html', {
        'absences': absences
    })

@login_required
def declare_absence(request):
    # Vérifier que l'utilisateur est un employé (pas RH ni manager)
    if not hasattr(request.user, 'employee') or request.user.employee.role != 'employe':
        messages.error(request, 'Seuls les employés peuvent déclarer des absences.')
        return redirect('home')
        
    if request.method == 'POST':
        form = AbsenceReportForm(request.POST)
        if form.is_valid():
            absence = form.save(commit=False)
            absence.employee = request.user.employee
            absence.save()
            # Mettre à jour le statut de l'employé à 'absent'
            employee = request.user.employee
            employee.status = 'absent'
            employee.save()
            messages.success(request, 'Votre absence a été enregistrée avec succès.')
            return redirect('home')
    else:
        form = AbsenceReportForm()
    return render(request, 'presence/declare_absence.html', {'form': form})

@login_required
def custom_logout(request):
    employee = getattr(request.user, 'employee', None)
    if employee:
        from django.utils import timezone
        employee.last_logout = timezone.now()
        employee.save()
    auth_logout(request)
    return redirect('presence:login')

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .models import AbsenceReport

@login_required
def export_absence_pdf(request, absence_id):
    # Vérifier si l'utilisateur est un manager
    if hasattr(request.user, 'employee') and request.user.employee.role == 'manager':
        # Si c'est un manager, il peut voir les justificatifs de son équipe
        absence = get_object_or_404(
            AbsenceReport, 
            id=absence_id,
            employee__department=request.user.employee.department
        )
    else:
        # Sinon, vérifier que l'absence appartient bien à l'utilisateur
        absence = get_object_or_404(AbsenceReport, id=absence_id, employee=request.user.employee)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="absence_{absence.date}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    data = [
        ['Justificatif d\'Absence'],
        ['Date:', absence.date.strftime('%d/%m/%Y')],
        ['Employé:', f"{absence.employee.user.first_name} {absence.employee.user.last_name}"],
        ['Période:', f"{absence.start_time} - {absence.end_time}"],
        ['Statut:', 'Justifié'],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    # Mise à jour du statut
    absence.status = 'present'
    absence.justified = True
    absence.save()

    # Notifier les managers et RH
    managers = User.objects.filter(groups__name__in=['Manager', 'RH'])
    notification = Notification.objects.create(
        title=f"Justification d'absence",
        message=f"L'employé {absence.employee.user.get_full_name()} a justifié son absence du {absence.date}",
        link=f"/admin/presence/absencereport/{absence.id}/change/"
    )
    notification.users.set(managers)

    return response

@login_required
def get_rh_data(request):
    # Vérifier que l'utilisateur a un profil employee et le bon rôle
    if not hasattr(request.user, 'employee'):
        return JsonResponse({'error': 'Profil employé non trouvé'}, status=403)
    if request.user.employee.role != 'rh':
        return JsonResponse({'error': 'Accès non autorisé - Rôle RH requis'}, status=403)
    
    # Statistiques de présence par jour
    presences = Presence.objects.values('date').annotate(count=Count('id')).order_by('date')
    presence_data = {
        'labels': [p['date'].strftime('%d/%m') for p in presences],
        'values': [p['count'] for p in presences]
    }
    
    # Statistiques par statut
    status_counts = Employee.objects.values('status').annotate(count=Count('id'))
    status_data = {
        'labels': [s['status'] for s in status_counts],
        'values': [s['count'] for s in status_counts]
    }
    
    return JsonResponse({
        'presence_data': presence_data,
        'status_data': status_data,
        'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@login_required
def justify_absence_view(request):
    if request.method == 'POST' and 'absence_id' in request.POST:
        try:
            absence = AbsenceReport.objects.get(
                id=request.POST['absence_id'],
                employee__department=request.user.employee.department
            )
            
            # Mettre à jour l'absence
            absence.justified = True
            absence.status = 'present'
            absence.save()
            
            # Mettre à jour le statut de l'employé
            employee = absence.employee
            employee.status = 'present'
            employee.save()
            
            # Créer une entrée de présence
            Presence.objects.update_or_create(
                employee=employee,
                date=timezone.now().date(),
                defaults={'status': 'present'}
            )
            
            messages.success(request, f"L'absence de {employee.name} a été justifiée avec succès.")
        except AbsenceReport.DoesNotExist:
            messages.error(request, "Absence non trouvée ou vous n'avez pas les droits nécessaires.")
    
    return redirect('team_dashboard')

