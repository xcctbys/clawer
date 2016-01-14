#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


class TimeStampedModel(models.Model):
    """
    abstract base class, 提供创建时间和修改时间两个通用的field
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
