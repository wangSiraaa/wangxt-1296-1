from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('judicial', '司法所'),
        ('social_worker', '社工'),
        ('family', '家属'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='角色')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    real_name = models.CharField(max_length=50, blank=True, verbose_name='真实姓名')
    department = models.CharField(max_length=100, blank=True, verbose_name='所属部门')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.real_name or self.username
