from django.contrib import admin
from .models import (
    CorrectionObject, FamilyRelation, VisitPlan, VisitRecord,
    LocationRecord, RiskLevelChange, FamilyFeedback, Notification
)

admin.site.register(CorrectionObject)
admin.site.register(FamilyRelation)
admin.site.register(VisitPlan)
admin.site.register(VisitRecord)
admin.site.register(LocationRecord)
admin.site.register(RiskLevelChange)
admin.site.register(FamilyFeedback)
admin.site.register(Notification)
