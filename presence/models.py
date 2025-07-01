from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.utils import timezone

ROLE_CHOICES = (
    ('employe', 'Employé'),
    ('manager', 'Manager'),
    ('rh', 'RH'),
)

class Employee(models.Model):
    STATUS_CHOICES = [
        ('present', 'Présent'),
        ('pause', 'Pause'),
        ('meeting', 'Réunion'),
        ('absent', 'Absent'),
        ('inactive', 'Inactif'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    name = models.CharField(max_length=255, default='Unnamed')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employe')
    last_logout = models.DateTimeField(null=True, blank=True)  # Ajoute ceci

class ActivityLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=50)  # 'mouse', 'keyboard', 'status_change'
    status = models.CharField(max_length=20, choices=Employee.STATUS_CHOICES, default='present')

def user_justification_path(instance, filename):
    # Fichier enregistré dans MEDIA_ROOT/justifications/user_<id>/<filename>
    return f'justifications/user_{instance.employee.user.id}/{filename}'

class AbsenceReport(models.Model):
    STATUS_CHOICES = [
        ('absent', 'Absent'),
        ('present', 'Present'),
    ]
    
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    justified = models.BooleanField(default=False)
    justification_file = models.FileField(upload_to=user_justification_path, blank=True, null=True, 
                                         verbose_name='Justificatif (PDF)',
                                         help_text='Téléversez un fichier PDF justifiant votre absence')
    justification = models.TextField(blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Absence de {self.employee} le {self.date}"

    class Meta:
        ordering = ['-date', '-start_time']

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class Presence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Employee.STATUS_CHOICES)

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    users = models.ManyToManyField(User, related_name='notifications')

    class Meta:
        ordering = ['-created_at']


@receiver(m2m_changed, sender=User.groups.through)
def sync_role_with_group(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        if hasattr(instance, 'employee'):
            groups = instance.groups.values_list('name', flat=True)
            if 'rh' in groups:
                instance.employee.role = 'rh'
            elif 'manager' in groups:
                instance.employee.role = 'manager'
            else:
                instance.employee.role = 'employe'
            instance.employee.save()