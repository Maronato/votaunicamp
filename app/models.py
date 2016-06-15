#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=20)
    ra = models.CharField(max_length=7)
    ram = models.CharField(max_length=7)
    name = models.CharField(max_length=70)
    rg = models.CharField(max_length=25)
    course = models.CharField(max_length=70)
    active = models.BooleanField(default=False)

    def __str__(self):
        return "Profile: " + str(self.ra)


class Vote(models.Model):
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
    )
    vote = models.CharField(max_length=9)
    reason = models.TextField()

    def __str__(self):
        return "Vote from: " + str(self.profile)


class Args(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
    )
    side = models.BooleanField(default=False)
    text = models.CharField(max_length=5000)
    dislikes = models.DecimalField(max_digits=5, decimal_places=0)
    likes = models.DecimalField(max_digits=5, decimal_places=0)
    title = models.CharField(max_length=60)
    hits = models.ManyToManyField(Profile, related_name='click')

    def __str__(self):
        return "Arg: " + str(self.title)
