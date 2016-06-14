#!/usr/bin/env python
# coding: utf-8
from django.shortcuts import render, redirect
import re
from .models import Args, Profile, Vote
from . import email_functions
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
import bleach
from django.utils.html import escape
# Create your views here.


def index(request):

    return render(request, 'index.html')


def results(request):
    total = yes = no = abs = 0
    for profs in Profile.objects.all():
        total += 1
        if profs.vote.vote == u'Sim':
            yes += 1
        elif profs.vote.vote == u'Não':
            no += 1
        else:
            abs += 1
    try:
        yes = str(yes) + " (" + str(round((float(yes)/total)*100, 2)) + "%)"
        no = str(no) + " (" + str(round((float(no)/total)*100, 2)) + "%)"
        abs = str(abs) + " (" + str(round((float(abs)/total)*100, 2)) + "%)"
    except ZeroDivisionError:
        total = yes = no = abs = 0

    inst = []
    for institution in Profile.objects.values_list('course', flat=True).distinct():
            list = Profile.objects.filter(course=institution)
            totali = len(list)
            yesi = noi = absi = 0
            for student in list:
                if student.vote.vote == u'Sim':
                    yesi += 1
                elif student.vote.vote == u'Não':
                    noi += 1
                else:
                    absi += 1

            try:
                yesi = str(yesi) + " (" + str(round((float(yesi) / totali) * 100, 1)) + "%)"
                noi = str(noi) + " (" + str(round((float(noi) / totali) * 100, 1)) + "%)"
                absi = str(absi) + " (" + str(round((float(absi) / totali) * 100, 1)) + "%)"
            except ZeroDivisionError:
                totali = yesi = noi = absi = 0

            inst.append([institution, totali, yesi, absi, noi])

    values = {
        'total': total,
        'yes': yes,
        'no': no,
        'abs': abs,
        'infos': Profile.objects.all(),
        'insts': inst
    }
    return render(request, 'results.html', values)


def arguments(request):
    args = Args.objects.all()
    return render(request, 'arguments.html', {'args': args})


def process_vote(request):
    if hasattr(request.user, 'password'):
        reason = request.POST['reason']
        try:
            vote = request.POST['vote']

        except:
            prevalues = email_functions.set_prevalues('vote_1', reason, 0)
            prevalues['cap_error'] = 'Escolha um voto'
            return render(request, 'index.html', prevalues)
        prevalues = email_functions.set_prevalues(vote, reason, 0)

        recapv, recapt = email_functions.captcha(request.POST['g-recaptcha-response'])
        if not recapv:
            prevalues['cap_error'] = 'Captcha incorreto'
            return render(request, 'index.html', prevalues)
        reason = escape(bleach.clean(reason, strip=True))
        request.user.profile.vote.vote, request.user.profile.vote.reason = vote, reason
        request.user.profile.vote.save()
        prevalues['cap_error'] = 'Voto atualizado com sucesso'
        return render(request, 'index.html', prevalues)
    vnf, auth_code, vote, password, passwordconf, reason = email_functions.proc_request(request)
    prevalues = email_functions.set_prevalues(vote, reason, auth_code)
    recapv, recapt = email_functions.captcha(request.POST['g-recaptcha-response'])
    if not recapv:
        prevalues['cap_error'] = recapt
        return render(request, 'index.html', prevalues)
    if not vnf:
        prevalues['cap_error'] = 'Escolha um voto'
        return render(request, 'index.html', prevalues)

    codev, codet = email_functions.dac_check(auth_code)
    if not codev:
        prevalues['auth_error'] = codet
        return render(request, 'index.html', prevalues)
    ra, name, rg, course = codet['ra'], codet['nome'], codet['rg'], codet['curso']

    if password:
        if password != passwordconf:
            prevalues['pass_error'] = 'Senhas diferentes'
            return render(request, 'index.html', prevalues)

    prevalues = email_functions.vote_user_create(ra, name, rg, course, password, vote, reason, prevalues, request)
    return render(request, 'index.html', prevalues)


def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect('index')
        return render(request, 'index.html', {'login_error': 'Sua conta está desativada'})
    return render(request, 'index.html', {'login_error': 'Usuário ou senha incorretos'})


def logout_user(request):
    logout(request)
    return redirect('index')


def user_info(request):
    return render(request, 'userinfo.html',{'args': Args.objects.filter(profile=request.user.profile)})


def submit_comment(request):
    author = request.user
    text = request.POST['text']
    if request.POST['vote'] == 'Sim':
        side = False
    else:
        side = True
    title = request.POST['title']
    a = Args(profile=author.profile, text=text, side=side, dislikes=0, likes=0, title=title)
    a.save()
    return redirect('arguments')


def like_comment(request):
    if not request.user.is_authenticated():
        return redirect('arguments')
    button = request.POST['press']
    a = Args.objects.get(id=button)
    if not check_like_dislike(request):
        return redirect('/arguments/#' + str(a.id))
    a.likes += 1
    a.hits.add(request.user.profile)
    a.save()
    return redirect('/arguments/#' + str(a.id))


def dislike_comment(request):
    if not request.user.is_authenticated():
        return redirect('arguments')
    button = request.POST['press']
    a = Args.objects.get(id=button)
    if not check_like_dislike(request):
        return redirect('/arguments/#' + str(a.id))
    a.dislikes += 1
    a.hits.add(request.user.profile)
    a.save()
    return redirect('/arguments/#' + str(a.id))


def delete_comment(request):
    if not request.user.is_authenticated():
        return redirect('index')
    button = request.POST['press']
    a = Args.objects.get(id=button)
    if not a.profile == request.user.profile:
        return redirect('index')
    a.delete()
    return redirect('/user_info/')


def check_like_dislike(request):
    button = request.POST['press']
    a = Args.objects.get(id=button)
    user = request.user.profile
    for hit in a.hits.all():
        if hit.ra == user.ra:
            return 0
    return 1


def help_page(request):
    return render(request, 'help.html')
