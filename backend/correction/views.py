from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import date

from .models import (
    CorrectionObject, FamilyRelation, VisitPlan, VisitRecord,
    LocationRecord, RiskLevelChange, FamilyFeedback, Notification
)
from .serializers import (
    CorrectionObjectSerializer, CorrectionObjectListSerializer,
    FamilyRelationSerializer, VisitPlanSerializer, VisitRecordSerializer,
    LocationRecordSerializer, RiskLevelChangeSerializer,
    FamilyFeedbackSerializer, NotificationSerializer
)
from .utils import validate_location, handle_risk_level_change, regenerate_monthly_plans, check_missed_visits


class IsJudicialWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'judicial'


class IsSocialWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'social_worker'


class IsFamily(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'family'


class CorrectionObjectViewSet(viewsets.ModelViewSet):
    queryset = CorrectionObject.objects.all()
    serializer_class = CorrectionObjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'id_card', 'phone']
    ordering_fields = ['created_at', 'risk_level']

    def get_serializer_class(self):
        if self.action == 'list':
            return CorrectionObjectListSerializer
        return CorrectionObjectSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsJudicialWorker()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'social_worker':
            queryset = queryset.filter(assigned_worker=user)
        elif user.role == 'family':
            queryset = queryset.filter(family_members__family_user=user)

        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)

        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.distinct()

    @action(detail=True, methods=['post'])
    def change_risk_level(self, request, pk=None):
        correction_obj = self.get_object()
        from_level = correction_obj.risk_level
        to_level = request.data.get('to_level')
        reason = request.data.get('reason', '')

        if not to_level:
            return Response({'error': '请指定目标风险等级'}, status=status.HTTP_400_BAD_REQUEST)

        if from_level == to_level:
            return Response({'error': '风险等级未变化'}, status=status.HTTP_400_BAD_REQUEST)

        correction_obj.risk_level = to_level
        correction_obj.save()

        risk_change = handle_risk_level_change(
            correction_obj, from_level, to_level, reason, request.user
        )

        return Response({
            'message': '风险等级调整成功',
            'risk_change': RiskLevelChangeSerializer(risk_change).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def generate_monthly_plans(self, request, pk=None):
        correction_obj = self.get_object()
        count = regenerate_monthly_plans(correction_obj, request.user)
        return Response({'message': f'成功生成{count}条走访计划', 'count': count})


class VisitPlanViewSet(viewsets.ModelViewSet):
    queryset = VisitPlan.objects.all()
    serializer_class = VisitPlanSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['plan_date', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsJudicialWorker()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'social_worker':
            queryset = queryset.filter(assigned_worker=user)
        elif user.role == 'family':
            queryset = queryset.filter(correction_object__family_members__family_user=user)

        correction_object_id = self.request.query_params.get('correction_object_id')
        if correction_object_id:
            queryset = queryset.filter(correction_object_id=correction_object_id)

        plan_date = self.request.query_params.get('plan_date')
        if plan_date:
            queryset = queryset.filter(plan_date=plan_date)

        plan_month = self.request.query_params.get('plan_month')
        if plan_month:
            year, month = plan_month.split('-')
            queryset = queryset.filter(plan_date__year=year, plan_date__month=month)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset.distinct().order_by('plan_date')

    @action(detail=False, methods=['post'])
    def batch_generate(self, request):
        risk_level = request.data.get('risk_level')
        count = 0

        if risk_level:
            objects = CorrectionObject.objects.filter(risk_level=risk_level, status='active')
        else:
            objects = CorrectionObject.objects.filter(status='active')

        for obj in objects:
            count += regenerate_monthly_plans(obj, request.user)

        return Response({'message': f'成功为{objects.count()}名对象生成{count}条走访计划', 'object_count': objects.count(), 'plan_count': count})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        plan = self.get_object()
        if plan.status != 'pending':
            return Response({'error': '只能取消待执行的计划'}, status=status.HTTP_400_BAD_REQUEST)
        plan.status = 'cancelled'
        plan.save()
        return Response({'message': '计划已取消'})


class VisitRecordViewSet(viewsets.ModelViewSet):
    queryset = VisitRecord.objects.all()
    serializer_class = VisitRecordSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['visit_date', 'created_at']

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsSocialWorker()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'social_worker':
            queryset = queryset.filter(visitor=user)
        elif user.role == 'family':
            queryset = queryset.filter(correction_object__family_members__family_user=user)

        correction_object_id = self.request.query_params.get('correction_object_id')
        if correction_object_id:
            queryset = queryset.filter(correction_object_id=correction_object_id)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(visit_date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(visit_date__lte=end_date)

        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['visitor'] = request.user.id

        longitude = data.get('longitude')
        latitude = data.get('latitude')
        correction_object_id = data.get('correction_object')

        if longitude and latitude and correction_object_id:
            try:
                correction_obj = CorrectionObject.objects.get(id=correction_object_id)
                is_valid, distance = validate_location(correction_obj, longitude, latitude)
                data['location_valid'] = is_valid
                data['location_deviation'] = distance

                if not is_valid:
                    return Response({
                        'error': '定位偏离允许范围，无法提交走访记录',
                        'deviation': distance,
                        'allowed': correction_obj.allowed_deviation,
                        'location_valid': False
                    }, status=status.HTTP_400_BAD_REQUEST)

                location_record = LocationRecord.objects.create(
                    correction_object=correction_obj,
                    longitude=longitude,
                    latitude=latitude,
                    recorded_by=request.user,
                    is_deviated=not is_valid,
                    deviation_distance=distance
                )
            except CorrectionObject.DoesNotExist:
                pass

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        visit_record = serializer.instance
        if visit_record.visit_plan:
            visit_record.visit_plan.status = 'completed'
            visit_record.visit_plan.save()

        if visit_record.risk_change and visit_record.risk_change != visit_record.correction_object.risk_level:
            from_level = visit_record.correction_object.risk_level
            to_level = visit_record.risk_change
            visit_record.correction_object.risk_level = to_level
            visit_record.correction_object.save()
            handle_risk_level_change(
                visit_record.correction_object, from_level, to_level,
                f"走访后风险调整：{visit_record.talk_summary[:100]}", request.user
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LocationRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocationRecord.objects.all()
    serializer_class = LocationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'social_worker':
            queryset = queryset.filter(correction_object__assigned_worker=user)
        elif user.role == 'family':
            queryset = queryset.filter(correction_object__family_members__family_user=user)

        correction_object_id = self.request.query_params.get('correction_object_id')
        if correction_object_id:
            queryset = queryset.filter(correction_object_id=correction_object_id)

        return queryset

    @action(detail=False, methods=['post'])
    def validate(self, request):
        correction_object_id = request.data.get('correction_object_id')
        longitude = request.data.get('longitude')
        latitude = request.data.get('latitude')

        if not all([correction_object_id, longitude, latitude]):
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            correction_obj = CorrectionObject.objects.get(id=correction_object_id)
        except CorrectionObject.DoesNotExist:
            return Response({'error': '矫正对象不存在'}, status=status.HTTP_404_NOT_FOUND)

        is_valid, distance = validate_location(correction_obj, longitude, latitude)

        return Response({
            'valid': is_valid,
            'deviation': distance,
            'allowed': correction_obj.allowed_deviation,
            'home_longitude': str(correction_obj.home_longitude),
            'home_latitude': str(correction_obj.home_latitude)
        })


class RiskLevelChangeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskLevelChange.objects.all()
    serializer_class = RiskLevelChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'social_worker':
            queryset = queryset.filter(correction_object__assigned_worker=user)
        elif user.role == 'family':
            queryset = queryset.filter(correction_object__family_members__family_user=user)

        correction_object_id = self.request.query_params.get('correction_object_id')
        if correction_object_id:
            queryset = queryset.filter(correction_object_id=correction_object_id)

        return queryset


class FamilyFeedbackViewSet(viewsets.ModelViewSet):
    queryset = FamilyFeedback.objects.all()
    serializer_class = FamilyFeedbackSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['feedback_date', 'created_at']

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsFamily()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsJudicialWorker()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'family':
            queryset = queryset.filter(family_user=user)
        elif user.role == 'social_worker':
            queryset = queryset.filter(correction_object__assigned_worker=user)

        correction_object_id = self.request.query_params.get('correction_object_id')
        if correction_object_id:
            queryset = queryset.filter(correction_object_id=correction_object_id)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['family_user'] = request.user.id
        data['status'] = 'submitted'

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        feedback = self.get_object()
        if feedback.status != 'submitted':
            return Response({'error': '只能审核待审核的反馈'}, status=status.HTTP_400_BAD_REQUEST)

        feedback.status = 'reviewed'
        feedback.review_remark = request.data.get('review_remark', '')
        feedback.reviewed_by = request.user
        feedback.reviewed_at = timezone.now()
        feedback.save()

        return Response({'message': '审核成功'})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(receiver=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': '已标记为已读'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'message': '全部标记为已读'})

    @action(detail=True, methods=['post'])
    def mark_handled(self, request, pk=None):
        notification = self.get_object()
        notification.is_handled = True
        notification.save()
        return Response({'message': '已标记为已处理'})


class FamilyRelationViewSet(viewsets.ModelViewSet):
    queryset = FamilyRelation.objects.all()
    serializer_class = FamilyRelationSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsJudicialWorker()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'family':
            queryset = queryset.filter(family_user=user)

        correction_object_id = self.request.query_params.get('correction_object_id')
        if correction_object_id:
            queryset = queryset.filter(correction_object_id=correction_object_id)

        return queryset


class SystemViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def check_missed_visits(self, request):
        count = check_missed_visits()
        return Response({'message': f'检查完成，生成{count}条通知', 'count': count})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        stats = {}

        if user.role == 'judicial':
            objects = CorrectionObject.objects.filter(status='active')
            stats['total_objects'] = objects.count()
            stats['high_risk'] = objects.filter(risk_level='high').count()
            stats['medium_risk'] = objects.filter(risk_level='medium').count()
            stats['low_risk'] = objects.filter(risk_level='low').count()

            today = date.today()
            stats['today_plans'] = VisitPlan.objects.filter(plan_date=today).count()
            stats['pending_plans'] = VisitPlan.objects.filter(status='pending', plan_date__lt=today).count()
            stats['monthly_visits'] = VisitRecord.objects.filter(
                visit_date__year=today.year, visit_date__month=today.month
            ).count()

            stats['unread_notifications'] = Notification.objects.filter(
                receiver=user, is_read=False
            ).count()

        elif user.role == 'social_worker':
            objects = CorrectionObject.objects.filter(assigned_worker=user, status='active')
            stats['total_objects'] = objects.count()
            stats['high_risk'] = objects.filter(risk_level='high').count()

            today = date.today()
            stats['today_plans'] = VisitPlan.objects.filter(
                assigned_worker=user, plan_date=today
            ).count()
            stats['pending_plans'] = VisitPlan.objects.filter(
                assigned_worker=user, status='pending', plan_date__lt=today
            ).count()
            stats['monthly_visits'] = VisitRecord.objects.filter(
                visitor=user, visit_date__year=today.year, visit_date__month=today.month
            ).count()

            stats['unread_notifications'] = Notification.objects.filter(
                receiver=user, is_read=False
            ).count()

        elif user.role == 'family':
            relations = FamilyRelation.objects.filter(family_user=user)
            object_ids = relations.values_list('correction_object_id', flat=True)
            stats['related_objects'] = len(object_ids)

            today = date.today()
            stats['monthly_visits'] = VisitRecord.objects.filter(
                correction_object_id__in=object_ids,
                visit_date__year=today.year,
                visit_date__month=today.month
            ).count()

            stats['my_feedbacks'] = FamilyFeedback.objects.filter(
                family_user=user
            ).count()

            stats['unread_notifications'] = Notification.objects.filter(
                receiver=user, is_read=False
            ).count()

        return Response(stats)
