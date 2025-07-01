from django.contrib import admin
from .models import Employee, AbsenceReport

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'department', 'role', 'status')
    search_fields = ('user__username', 'name', 'department', 'role')
    readonly_fields = ('status',)  # Ajoutez ceci pour rendre le champ status non modifiable

admin.site.register(Employee, EmployeeAdmin)

# Ajout du module AbsenceReport dans l'admin
@admin.register(AbsenceReport)
class AbsenceReportAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'start_time', 'end_time', 'justified')
    list_filter = ('justified', 'date', 'employee__department')
    search_fields = ('employee__name', 'employee__department', 'reason')

