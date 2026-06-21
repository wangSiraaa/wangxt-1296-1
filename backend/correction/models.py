from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class CorrectionObject(models.Model):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )

    RISK_LEVEL_CHOICES = (
        ('low', '低风险'),
        ('medium', '中风险'),
        ('high', '高风险'),
    )

    STATUS_CHOICES = (
        ('active', '在矫中'),
        ('completed', '已解矫'),
        ('suspended', '暂停'),
    )

    name = models.CharField(max_length=50, verbose_name='姓名')
    id_card = models.CharField(max_length=18, unique=True, verbose_name='身份证号')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='性别')
    age = models.IntegerField(verbose_name='年龄')
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    address = models.CharField(max_length=200, verbose_name='居住地址')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='medium', verbose_name='风险等级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    correction_type = models.CharField(max_length=50, verbose_name='矫正类型')
    correction_start = models.DateField(verbose_name='矫正开始日期')
    correction_end = models.DateField(verbose_name='矫正结束日期')
    assigned_judicial = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='correction_judicial', verbose_name='负责司法所')
    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='correction_worker', verbose_name='负责社工')
    home_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name='家经度')
    home_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, verbose_name='家纬度')
    allowed_deviation = models.FloatField(default=500.0, verbose_name='允许偏离距离(米)')
    avatar = models.ImageField(upload_to='correction_objects/', null=True, blank=True, verbose_name='照片')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '矫正对象'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FamilyRelation(models.Model):
    RELATION_CHOICES = (
        ('spouse', '配偶'),
        ('parent', '父母'),
        ('child', '子女'),
        ('sibling', '兄弟姐妹'),
        ('other', '其他'),
    )

    correction_object = models.ForeignKey(CorrectionObject, on_delete=models.CASCADE, related_name='family_members', verbose_name='矫正对象')
    family_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='correction_relations', verbose_name='家属用户')
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, verbose_name='与矫正对象关系')
    is_primary = models.BooleanField(default=False, verbose_name='主要联系人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '家属关系'
        verbose_name_plural = verbose_name
        unique_together = ['correction_object', 'family_user']


class VisitPlan(models.Model):
    STATUS_CHOICES = (
        ('pending', '待执行'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    correction_object = models.ForeignKey(CorrectionObject, on_delete=models.CASCADE, related_name='visit_plans', verbose_name='矫正对象')
    plan_date = models.DateField(verbose_name='计划走访日期')
    plan_type = models.CharField(max_length=50, verbose_name='走访类型')
    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_visit_plans', verbose_name='负责社工')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_visit_plans', verbose_name='创建人')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    is_auto_generated = models.BooleanField(default=False, verbose_name='是否自动生成')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '走访计划'
        verbose_name_plural = verbose_name
        ordering = ['-plan_date']

    def __str__(self):
        return f"{self.correction_object.name} - {self.plan_date}"


class VisitRecord(models.Model):
    VISIT_WAY_CHOICES = (
        ('home', '入户走访'),
        ('telephone', '电话走访'),
        ('video', '视频走访'),
        ('office', '司法所报到'),
        ('other', '其他'),
    )

    visit_plan = models.OneToOneField(VisitPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='visit_record', verbose_name='关联走访计划')
    correction_object = models.ForeignKey(CorrectionObject, on_delete=models.CASCADE, related_name='visit_records', verbose_name='矫正对象')
    visit_date = models.DateTimeField(verbose_name='走访时间')
    visit_way = models.CharField(max_length=20, choices=VISIT_WAY_CHOICES, verbose_name='走访方式')
    visitor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='visit_records', verbose_name='走访人')
    talk_summary = models.TextField(verbose_name='谈话摘要')
    risk_change = models.CharField(max_length=20, choices=CorrectionObject.RISK_LEVEL_CHOICES, null=True, blank=True, verbose_name='风险变化')
    location_valid = models.BooleanField(default=True, verbose_name='定位是否有效')
    location_deviation = models.FloatField(null=True, blank=True, verbose_name='定位偏离距离(米)')
    photos = models.JSONField(default=list, verbose_name='走访照片')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '走访记录'
        verbose_name_plural = verbose_name
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.correction_object.name} - {self.visit_date}"


class LocationRecord(models.Model):
    correction_object = models.ForeignKey(CorrectionObject, on_delete=models.CASCADE, related_name='location_records', verbose_name='矫正对象')
    longitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='经度')
    latitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='纬度')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='location_records', verbose_name='记录人')
    is_deviated = models.BooleanField(default=False, verbose_name='是否偏离')
    deviation_distance = models.FloatField(null=True, blank=True, verbose_name='偏离距离(米)')
    address = models.CharField(max_length=200, blank=True, verbose_name='地址描述')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')

    class Meta:
        verbose_name = '定位记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class RiskLevelChange(models.Model):
    correction_object = models.ForeignKey(CorrectionObject, on_delete=models.CASCADE, related_name='risk_changes', verbose_name='矫正对象')
    from_level = models.CharField(max_length=20, choices=CorrectionObject.RISK_LEVEL_CHOICES, verbose_name='原风险等级')
    to_level = models.CharField(max_length=20, choices=CorrectionObject.RISK_LEVEL_CHOICES, verbose_name='新风险等级')
    reason = models.TextField(verbose_name='调整原因')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='risk_changes', verbose_name='操作人')
    regenerated_plan = models.BooleanField(default=False, verbose_name='是否已重生成计划')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='调整时间')

    class Meta:
        verbose_name = '风险等级变更'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class FamilyFeedback(models.Model):
    STATUS_CHOICES = (
        ('submitted', '已提交'),
        ('reviewed', '已审核'),
    )

    correction_object = models.ForeignKey(CorrectionObject, on_delete=models.CASCADE, related_name='family_feedbacks', verbose_name='矫正对象')
    family_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', verbose_name='家属')
    feedback_date = models.DateField(verbose_name='反馈日期')
    behavior_situation = models.TextField(verbose_name='帮教情况')
    mental_state = models.TextField(blank=True, verbose_name='思想动态')
    life_condition = models.TextField(blank=True, verbose_name='生活状况')
    work_study = models.TextField(blank=True, verbose_name='工作学习情况')
    problems = models.TextField(blank=True, verbose_name='存在问题')
    suggestions = models.TextField(blank=True, verbose_name='意见建议')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted', verbose_name='状态')
    review_remark = models.TextField(blank=True, verbose_name='审核意见')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviewed_feedbacks', verbose_name='审核人')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '家属帮教反馈'
        verbose_name_plural = verbose_name
        ordering = ['-feedback_date']


class Notification(models.Model):
    TYPE_CHOICES = (
        ('missed_visit', '漏访提醒'),
        ('location_deviation', '定位偏离'),
        ('risk_change', '风险变更'),
        ('system', '系统通知'),
    )

    LEVEL_CHOICES = (
        ('normal', '普通'),
        ('warning', '警告'),
        ('urgent', '紧急'),
    )

    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='通知类型')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='normal', verbose_name='通知级别')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收人')
    correction_object = models.ForeignKey(CorrectionObject, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications', verbose_name='关联矫正对象')
    related_id = models.IntegerField(null=True, blank=True, verbose_name='关联记录ID')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_handled = models.BooleanField(default=False, verbose_name='是否已处理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title
