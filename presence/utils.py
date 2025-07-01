from django.db.models import Count, Sum, Case, When, functions
from django.db.models.functions import ExtractHour
from datetime import timedelta
from .models import AbsenceReport, ActivityLog, User  # Import relatif

def calculate_monthly_stats():
    from django.utils import timezone
    from_date = timezone.now() - timedelta(days=30)
    return {
        'total_absences': AbsenceReport.objects.filter(date__gte=from_date).count(),
        'unjustified_absences': AbsenceReport.objects.filter(date__gte=from_date, justified=False).count(),
        'by_department': AbsenceReport.objects.filter(date__gte=from_date)
                             .values('employee__department')
                             .annotate(total=Count('id'), unjustified=Sum(Case(When(justified=False, then=1), default=0))),
        'activity_levels': ActivityLog.objects.filter(timestamp__gte=from_date)
                             .extra({'hour': "HOUR(timestamp)"})
                             .values('hour')
                             .annotate(count=Count('id'))
                             .order_by('hour')
    }

def generate_analytics(start_date, end_date):
    return {
        'activity_heatmap': ActivityLog.objects.filter(
            timestamp__range=(start_date, end_date))
            .annotate(hour=ExtractHour('timestamp'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour'),
        'top_inactive_users': User.objects.annotate(
            inactive_count=Count('employee__absencereport'))
            .order_by('-inactive_count')[:5]
    }