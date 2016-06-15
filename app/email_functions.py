#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
from .models import Profile, Vote
from .DACInfo import core
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import re
import bleach
from django.utils.html import escape


def captcha(grs):
    try:
        url = "https://www.google.com/recaptcha/api/siteverify"
        values = {
            'secret': str(os.environ.get('CAP_SECRET')),
            'response': grs,
        }
        verify_rs = requests.get(url, params=values, verify=True)
        verify_rs = verify_rs.json()
        response = verify_rs.get("success", False)
        if not response:
            return 0, "Captcha incorreto"
    except:
        return 0, "Captcha incorreto"
    return 1, "Captcha correto"


def dac_check(key_code):
    c, v = core.check_code(key_code)
    if c is 0:
        return 0, v
    else:
        vars = core.check_fields(v)
        for key, value in vars.iteritems():
            if value is 0:
                return 0, "[404] Fale com o administrador."
    return 1, vars


def proc_request(request):
    auth_code = request.POST['auth_code']
    auth_code = re.sub(r'\s+', '', auth_code)
    password = request.POST['password']
    passwordconf = request.POST['passwordconf']
    reason = request.POST['reason']
    reason = escape(bleach.clean(reason, strip=True))
    try:
        vote = request.POST['vote']
    except:
        return 0, auth_code, 'Abstenção', password, passwordconf, reason
    return 1, auth_code, vote, password, passwordconf, reason


def set_prevalues(vote, reason, auth_code):
    v = vote
    if v == 'Sim':
        vote_prev = 'vote_0'
    elif v == u'Não':
        vote_prev = 'vote_2'
    else:
        vote_prev = 'vote_1'
    prevalues = {
        'auth_prev': auth_code,
        vote_prev: 'checked="Checked"',
        'reason_prev': reason
    }
    return prevalues


def vote_user_create(ra, name, rg, course, password, vote, reason, prevalues, request):
    course, rg, ram, first_name = normalize_data(course, rg, ra, name)
    try:
        #   Check if user exists
        a = User.objects.get(username=ra)
        if a.profile.active is True:
            prevalues['cap_error'] = 'Faça o login para alterar seu voto'
            return prevalues
        if password:
            a.profile.active = True
            a.set_password(password)
            prevalues['cap_error'] = "Usuário e voto adicionado com sucesso"
        else:
            prevalues['cap_error'] = "Voto atualizado com sucesso"
        a.profile.vote.vote, a.profile.vote.reason = vote, reason
        a.profile.vote.save()
        a.profile.save()
        a.save()
        user = authenticate(username=ra, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
        return prevalues
    except User.DoesNotExist:

        #   TEST CODE
        #   Check if user already exists with another RA, by checking BOTH rg and name. (false-positives are priority)
        try:
            f = Profile.objects.get(name=name)
            f = Profile.objects.get(rg=rg)
            prevalues['cap_error'] = "Usuário já cadastrado com outro RA."
            return prevalues
        except:
            pass
        #   /TEST CODE
        if password:
            b = User(username=ra)
            b.set_password(password)
            b.save()
            c = Profile(user=b, ra=ra, name=name, rg=rg, course=course, active=True, first_name=first_name, ram=ram)
            c.save()
            d = Vote(profile=c, vote=vote, reason=reason)
            d.save()
            prevalues['cap_error'] = "Usuário e voto adicionados com sucesso"
            user = authenticate(username=ra, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
            return prevalues
        b = User(username=ra)
        b.save()
        c = Profile(user=b, ra=ra, name=name, rg=rg, course=course, active=False, first_name=first_name, ram=ram)
        c.save()
        d = Vote(profile=c, vote=vote, reason=reason)
        d.save()
        prevalues['cap_error'] = "Voto adicionado com sucesso"
        return prevalues


def normalize_data(course, rg, ra, name):
    course = re.sub('Curso: ', '', course)
    rg = re.sub('[a-zA-Z]| ', '', rg)
    if len(re.findall('-', rg)) > 1:
        rg = rg[:-1]
    rg = rg[:3] + re.sub(r'\d', '*', rg[3:-1]) + rg[-1]
    n = re.compile(r'\d')
    #   c = re.compile(r'[a-zA-Z]+ ')
    #   name = c.findall(name)[0]
    name = re.findall(r'(\w+)', name, re.UNICODE)[0]
    ra = ra[:3] + n.sub('*', ra[3:])
    return course, rg, ra, name
