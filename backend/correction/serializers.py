from rest_framework import serializers
from .models import (
    CorrectionObject, FamilyRelation, VisitPlan, VisitRecord,
    LocationRecord, RiskLevelChange, FamilyFeedback, Notification
)
from users.serializers import UserSerializer


class CorrectionObjectSerializer(serializers.ModelSerializer):
    assigned_judicial_name = serializers.CharField(source='assigned_judicial.real_name', read_only=True)
    assigned_worker_name = serializers.CharField(source='assigned_worker.real_name', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CorrectionObject
        fields = '__all__'


class CorrectionObjectListSerializer(serializers.ModelSerializer):
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CorrectionObject
        fields = ['id', 'name', 'id_card', 'risk_level', 'risk_level_display', 'status', 'status_display',
                  'correction_type', 'correction_start', 'correction_end', 'phone']


class FamilyRelationSerializer(serializers.ModelSerializer):
    family_user_info = UserSerializer(source='family_user', read_only=True)
    relation_display = serializers.CharField(source='get_relation_display', read_only=True)

    class Meta:
        model = FamilyRelation
        fields = '__all__'


class VisitPlanSerializer(serializers.ModelSerializer):
    correction_object_name = serializers.CharField(source='correction_object.name', read_only=True)
    assigned_worker_name = serializers.CharField(source='assigned_worker.real_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = VisitPlan
        fields = '__all__'


class VisitRecordSerializer(serializers.ModelSerializer):
    correction_object_name = serializers.CharField(source='correction_object.name', read_only=True)
    visitor_name = serializers.CharField(source='visitor.real_name', read_only=True)
    visit_way_display = serializers.CharField(source='get_visit_way_display', read_only=True)
    risk_change_display = serializers.CharField(source='get_risk_change_display', read_only=True)

    class Meta:
        model = VisitRecord
        fields = '__all__'


class LocationRecordSerializer(serializers.ModelSerializer):
    correction_object_name = serializers.CharField(source='correction_object.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.real_name', read_only=True)

    class Meta:
        model = LocationRecord
        fields = '__all__'


class RiskLevelChangeSerializer(serializers.ModelSerializer):
    correction_object_name = serializers.CharField(source='correction_object.name', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)
    from_level_display = serializers.CharField(source='get_from_level_display', read_only=True)
    to_level_display = serializers.CharField(source='get_to_level_display', read_only=True)

    class Meta:
        model = RiskLevelChange
        fields = '__all__'


class FamilyFeedbackSerializer(serializers.ModelSerializer):
    correction_object_name = serializers.CharField(source='correction_object.name', read_only=True)
    family_user_name = serializers.CharField(source='family_user.real_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FamilyFeedback
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    receiver_name = serializers.CharField(source='receiver.real_name', read_only=True)
    correction_object_name = serializers.CharField(source='correction_object.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
