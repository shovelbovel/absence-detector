from django import forms
from django.contrib.auth import get_user_model
from .models import Message, AbsenceReport

User = get_user_model()

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'recipient-select'
            }),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Exclure l'utilisateur actuel et obtenir les employés actifs
            self.fields['recipient'].queryset = User.objects.filter(
                is_active=True,
                employee__isnull=False
            ).exclude(id=user.id).order_by('first_name', 'last_name')
            
            # Améliorer l'affichage des noms dans la liste déroulante
            self.fields['recipient'].label_from_instance = lambda obj: (
                f"{obj.get_full_name()} - {obj.employee.get_role_display()}"
                if obj.get_full_name()
                else f"{obj.username} - {obj.employee.get_role_display()}"
            )
    
    def clean_recipient(self):
        recipient = self.cleaned_data.get('recipient')
        if recipient == self.user:
            raise forms.ValidationError("Vous ne pouvez pas vous envoyer un message à vous-même.")
        return recipient

class AbsenceReportForm(forms.ModelForm):
    class Meta:
        model = AbsenceReport
        fields = ['date', 'start_time', 'end_time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }