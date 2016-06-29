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
import random
import unidecode


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


def gen_random_nickname():
    import random
    parts = {}
    path = os.path.dirname(os.path.dirname(__file__)) + '/app/names'
    with open(path, 'r') as f:
        lis = []
        for line in f.readlines():
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                lis = []
                parts[line[1:-1]] = lis
            else:
                lis.append(line.strip())

    nick = random.choice(parts['part1']) + " " + random.choice(parts['part2'])
    for user in Profile.objects.all():
        if user.nickname == nick:
            nick = gen_random_nickname()
            return nick
    return nick


def vote_user_create(ra, name, course, password, vote, reason, prevalues, request):
    course, first_name = normalize_data(course, name)
    try:
        #   Check if user exists
        a = User.objects.get(username=ra)
        prevalues['cap_error'] = 'Faça o login para alterar seu voto'
        return prevalues

    except User.DoesNotExist:
        try:
            f = Profile.objects.get(name=name)
            prevalues['cap_error'] = "Usuário já cadastrado com outro RA."
            return prevalues
        except:
            pass
        b = User(username=ra)
        b.set_password(password)
        b.save()
        nick = gen_random_nickname()
        c = Profile(user=b, ra=ra, name=name, course=course, first_name=first_name, nickname=nick)
        c.save()
        d = Vote(profile=c, vote=vote, reason=reason)
        d.save()
        prevalues['cap_error'] = "Usuário e voto adicionados com sucesso"
        user = authenticate(username=ra, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
        return prevalues


def normalize_data(course, name):
    course = re.sub('Curso: ', '', course)
    name = name.split()[0]
    return course, name
