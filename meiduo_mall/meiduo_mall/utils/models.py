# _*_ coding:utf-8 _*_
from django.db import models

class BaseModel(models.Model):
    '''为模型类补充字段'''
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')

    class Meta:
        # 说明是一个抽象的模型类,数据库在迁移时,不会创建BaseModel表
        abstract = True
