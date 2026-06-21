import math
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from .models import (
    CorrectionObject, VisitPlan, LocationRecord, Notification,
    RiskLevelChange, User
)


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def validate_location(correction_object, longitude, latitude):
    if not correction_object.home_longitude or not correction_object.home_latitude:
        return True, 0.0

    distance = calculate_distance(
        correction_object.home_latitude,
        correction_object.home_longitude,
        latitude,
        longitude
    )

    is_valid = distance <= correction_object.allowed_deviation
    return is_valid, distance


def check_missed_visits():
    today = date.today()
    yesterday = today - timedelta(days=1)

    missed_plans = VisitPlan.objects.filter(
        plan_date__lte=yesterday,
        status='pending',
        correction_object__status='active'
    ).select_related('correction_object', 'assigned_worker')

    notifications = []
    for plan in missed_plans:
        correction_obj = plan.correction_object
        is_high_risk = correction_obj.risk_level == 'high'

        title = f"漏访提醒：{correction_obj.name}"
        content = f"计划于{plan.plan_date}对{correction_obj.name}的走访未完成，请尽快安排走访。"
        level = 'urgent' if is_high_risk else 'warning'

        if correction_obj.assigned_judicial:
            notifications.append(Notification(
                type='missed_visit',
                level=level,
                title=title,
                content=content,
                receiver=correction_obj.assigned_judicial,
                correction_object=correction_obj,
                related_id=plan.id
            ))

        if plan.assigned_worker:
            notifications.append(Notification(
                type='missed_visit',
                level=level,
                title=title,
                content=content,
                receiver=plan.assigned_worker,
                correction_object=correction_obj,
                related_id=plan.id
            ))

        if is_high_risk:
            judicial_workers = User.objects.filter(role='judicial')
            for worker in judicial_workers:
                if worker != correction_obj.assigned_judicial:
                    notifications.append(Notification(
                        type='missed_visit',
                        level='urgent',
                        title=f"高风险漏访升级提醒：{correction_obj.name}",
                        content=f"高风险对象{correction_obj.name}于{plan.plan_date}的走访已逾期，已自动升级提醒，请紧急处理。",
                        receiver=worker,
                        correction_object=correction_obj,
                        related_id=plan.id
                    ))

    if notifications:
        Notification.objects.bulk_create(notifications)

    return len(notifications)


def regenerate_monthly_plans(correction_object, operator=None):
    today = date.today()
    next_month = today.replace(day=28) + timedelta(days=4)
    first_day = next_month.replace(day=1)
    if first_day.month == 12:
        last_day = first_day.replace(day=31)
    else:
        last_day = first_day.replace(month=first_day.month + 1, day=1) - timedelta(days=1)

    VisitPlan.objects.filter(
        correction_object=correction_object,
        plan_date__range=[first_day, last_day],
        status='pending',
        is_auto_generated=True
    ).delete()

    risk_level = correction_object.risk_level
    if risk_level == 'high':
        visit_interval = 7
    elif risk_level == 'medium':
        visit_interval = 15
    else:
        visit_interval = 30

    plans = []
    current_date = first_day
    while current_date <= last_day:
        plans.append(VisitPlan(
            correction_object=correction_object,
            plan_date=current_date,
            plan_type=f"{risk_level}风险定期走访",
            assigned_worker=correction_object.assigned_worker,
            created_by=operator,
            status='pending',
            is_auto_generated=True,
            remark=f"根据{risk_level}风险等级自动生成"
        ))
        current_date += timedelta(days=visit_interval)

    if plans:
        VisitPlan.objects.bulk_create(plans)

    return len(plans)


def handle_risk_level_change(correction_object, from_level, to_level, reason, operator):
    risk_change = RiskLevelChange.objects.create(
        correction_object=correction_object,
        from_level=from_level,
        to_level=to_level,
        reason=reason,
        operator=operator
    )

    notification_users = User.objects.filter(role='judicial')
    notifications = []
    for user in notification_users:
        notifications.append(Notification(
            type='risk_change',
            level='warning',
            title=f"风险等级变更：{correction_object.name}",
            content=f"{correction_object.name}的风险等级由{from_level}调整为{to_level}，原因：{reason}",
            receiver=user,
            correction_object=correction_object,
            related_id=risk_change.id
        ))

    if correction_object.assigned_worker:
        notifications.append(Notification(
            type='risk_change',
            level='warning',
            title=f"风险等级变更：{correction_object.name}",
            content=f"{correction_object.name}的风险等级由{from_level}调整为{to_level}，原因：{reason}",
            receiver=correction_object.assigned_worker,
            correction_object=correction_object,
            related_id=risk_change.id
        ))

    if notifications:
        Notification.objects.bulk_create(notifications)

    regenerate_monthly_plans(correction_object, operator)
    risk_change.regenerated_plan = True
    risk_change.save()

    return risk_change
