from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CorrectionObjectViewSet, VisitPlanViewSet, VisitRecordViewSet,
    LocationRecordViewSet, RiskLevelChangeViewSet, FamilyFeedbackViewSet,
    NotificationViewSet, FamilyRelationViewSet, SystemViewSet
)

router = DefaultRouter()
router.register(r'correction-objects', CorrectionObjectViewSet, basename='correction_object')
router.register(r'visit-plans', VisitPlanViewSet, basename='visit_plan')
router.register(r'visit-records', VisitRecordViewSet, basename='visit_record')
router.register(r'location-records', LocationRecordViewSet, basename='location_record')
router.register(r'risk-changes', RiskLevelChangeViewSet, basename='risk_change')
router.register(r'family-feedbacks', FamilyFeedbackViewSet, basename='family_feedback')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'family-relations', FamilyRelationViewSet, basename='family_relation')
router.register(r'system', SystemViewSet, basename='system')

urlpatterns = [
    path('', include(router.urls)),
]
