#!/usr/bin/env python
# coding: utf-8
from django.shortcuts import render, redirect
import re
from .models import Args, Profile, Comment, Vote
from . import email_functions
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout
import bleach
from django.utils.html import escape
from operator import itemgetter
from django.http import HttpResponse
from django.core.mail import send_mail
from django.shortcuts import render_to_response
from django.template import RequestContext
# Create your views here.


def index(request):

    return render(request, 'index.html')


def results(request):
    total = yes = no = abs = 0
    for profs in Profile.objects.all():
        try:
            u = profs.vote.vote
            total += 1
            if profs.vote.vote == u'Sim':
                yes += 1
            elif profs.vote.vote == u'Não':
                no += 1
            else:
                abs += 1
        except:
            pass
    try:
        yes = str(yes) + " (" + str(round((float(yes)/total)*100, 2)) + "%)"
        no = str(no) + " (" + str(round((float(no)/total)*100, 2)) + "%)"
        abs = str(abs) + " (" + str(round((float(abs)/total)*100, 2)) + "%)"
    except ZeroDivisionError:
        total = yes = no = abs = 0

    inst = []
    uinst = []
    for profs in Profile.objects.all():
        try:
            if profs.vote:
                uinst.append(profs.course)
        except:
            pass
    uinst = set(uinst)
    for institution in uinst:
            list = Profile.objects.filter(course=institution)
            totali = 0
            yesi = noi = absi = 0
            for student in list:
                try:
                    if student.vote.vote == u'Sim':
                        yesi += 1
                    elif student.vote.vote == u'Não':
                        noi += 1
                    else:
                        absi += 1
                    totali += 1
                except:
                    pass

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
        'infos': Vote.objects.all(),
        'insts': sorted(inst, key=itemgetter(0))
    }
    return render(request, 'results.html', values)


def prev_results(request):
    return render(request, 'previous_results.html')


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
        try:
            request.user.vote.vote
        except:
            d = Vote(profile=request.user.profile, vote=vote, reason=reason)
            d.save()
            prevalues['cap_error'] = 'Voto enviado com sucesso'
            return render(request, 'index.html', prevalues)
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
    ra, name, course = codet['ra'], codet['nome'], codet['curso']

    if not (password or passwordconf):
        prevalues['pass_error'] = 'Senha necessária'
        return render(request, 'index.html', prevalues)

    if password != passwordconf:
        prevalues['pass_error'] = 'Senhas diferentes'
        return render(request, 'index.html', prevalues)

    prevalues = email_functions.vote_user_create(ra, name, course, password, vote, reason, prevalues, request)
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
    return render(request, 'userinfo.html',{'args': Args.objects.filter(profile=request.user.profile), 'comments': Comment.objects.filter(author=request.user.profile)})


def submit_arg(request):
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


def like_arg(request):
    if not request.user.is_authenticated():
        return redirect('arguments')
    button = request.POST['press']
    a = Args.objects.get(id=button)
    if not check_like_dislike_arg(request):
        return redirect('/arguments/#' + str(a.id))
    a.likes += 1
    a.hits.add(request.user.profile)
    a.save()
    return redirect('/arguments/#' + str(a.id))


def dislike_arg(request):
    if not request.user.is_authenticated():
        return redirect('arguments')
    button = request.POST['press']
    a = Args.objects.get(id=button)
    if not check_like_dislike_arg(request):
        return redirect('/arguments/#' + str(a.id))
    a.dislikes += 1
    a.hits.add(request.user.profile)
    a.save()
    return redirect('/arguments/#' + str(a.id))


def delete_arg(request):
    if not request.user.is_authenticated():
        return redirect('index')
    button = request.POST['press']
    a = Args.objects.get(id=button)
    if not a.profile == request.user.profile:
        return redirect('index')
    a.delete()
    return redirect('/user_info/')


def check_like_dislike_arg(request):
    button = request.POST['press']
    a = Args.objects.get(id=button)
    user = request.user.profile
    for hit in a.hits.all():
        if hit.ra == user.ra:
            return 0
    return 1


def help_page(request):
    return render(request, 'help.html')


def down_stats(request):
    total = yes = no = abs = 0
    for profs in Profile.objects.all():
        try:
            u = profs.vote.vote
            total += 1
            if profs.vote.vote == u'Sim':
                yes += 1
            elif profs.vote.vote == u'Não':
                no += 1
            else:
                abs += 1
        except:
            pass
    open('stats.txt', 'w+')
    with open("stats.txt", "a") as stats:
        stats.write(str(yes) + ", " + str(no) + ", " + str(abs) + "\n")
        uinst = []
        for profs in Profile.objects.all():
            try:
                if profs.vote:
                    uinst.append(profs.course)
            except:
                pass
        uinst = set(uinst)
        for institution in uinst:
            list = Profile.objects.filter(course=institution)
            totali = 0
            yesi = noi = absi = 0
            for student in list:
                try:
                    if student.vote.vote == u'Sim':
                        yesi += 1
                    elif student.vote.vote == u'Não':
                        noi += 1
                    else:
                        absi += 1
                    totali += 1
                except:
                    pass
            stats.write(institution.encode('utf-8'))
            stats.write(", " + str(yesi) + ", " + str(noi) + ", " + str(absi) + "\n")
    stats.close()
    stats = open('stats.txt', 'r')
    stats.flush()
    stats.seek(0)  # move the pointer to the beginning of the buffer
    response = HttpResponse(stats, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=stats.txt'
    stats.close()
    return response


def comments(request, arg_id):
    arg_id = int(arg_id)
    arg = Args.objects.get(id=arg_id)
    comment = Comment.objects.filter(argument=arg)
    return render(request, 'comments.html', {'comments': comment, 'arg': arg})


def submit_comment(request):
    author = request.user.profile
    text = request.POST['text']
    arg = request.POST['arg']
    arg = Args.objects.get(id=arg)
    a = Comment(argument=arg, text=text, dislikes=0, likes=0, author=author)
    a.save()
    if not request.user.profile == arg.profile:
        recipient_list = []
        message = u"Olá, %s.\nSeu argumento '%s' acaba de receber um novo comentário de %s\nO comentário pode ser encontrado em www.votaunicamp.herokuapp.com/arguments/%s#%s\n\nAtenciosamente,\nBot de emails" % (arg.profile.first_name, arg.title, request.user.profile.nickname, arg.id, a.id)
        subject = u"Novo comentário em um de seus argumentos"
        from_email = "votaunicamp@gmail.com"
        recipient_list.append(arg.profile.name[0].lower() + arg.profile.ra + '@dac.unicamp.br')
        fail_silently = True
        send_mail(subject, message, from_email, recipient_list, fail_silently)

    check_list = []
    for comment in Comment.objects.filter(argument=arg):
        if not request.user.profile.ra == comment.author.ra and not comment.author.ra == arg.profile.ra:
            check_list.append(comment.author.name[0].lower() + comment.author.ra + '@dac.unicamp.br')
    check_list = set(check_list)
    for item in check_list:
        recipient_list = []
        recipient_list.append(item)
        message = u"Olá!\nA discussão do argumento '%s' que você faz parte acaba de receber um novo comentário de %s\nO comentário pode ser encontrado em www.votaunicamp.herokuapp.com/arguments/%s#%s\n\nAtenciosamente,\nBot de emails" % (arg.title, request.user.profile.nickname, arg.id, a.id)
        subject = u"Novo comentário em um argumento que você segue"
        from_email = "votaunicamp@gmail.com"
        fail_silently = True
        send_mail(subject, message, from_email, recipient_list, fail_silently)
    return redirect('/arguments/' + str(arg.id) + "#" + str(a.id))


def like_comment(request):
    button = request.POST['press']
    a = Comment.objects.get(id=button)
    arg = a.argument
    if not request.user.is_authenticated():
        return redirect('/arguments/' + str(arg.id) + "#" + str(a.id))
    if not check_like_dislike_comment(request):
        return redirect('/arguments/' + str(arg.id) + "#" + str(a.id))
    a.likes += 1
    a.hits.add(request.user.profile)
    a.save()
    return redirect('/arguments/' + str(arg.id) + "#" + str(a.id))


def dislike_comment(request):
    button = request.POST['press']
    a = Comment.objects.get(id=button)
    arg = a.argument
    if not request.user.is_authenticated():
        return redirect('/arguments/' + str(arg.id) + "#" + str(a.id))
    if not check_like_dislike_comment(request):
        return redirect('/arguments/' + str(arg.id) + "#" + str(a.id))
    a.dislikes += 1
    a.hits.add(request.user.profile)
    a.save()

    return redirect('/arguments/' + str(arg.id) + "#" + str(a.id))


def delete_comment(request):
    if not request.user.is_authenticated():
        return redirect('index')
    button = request.POST['press']
    a = Comment.objects.get(id=button)
    if not a.author == request.user.profile:
        return redirect('index')
    a.delete()
    return redirect('/user_info/')


def check_like_dislike_comment(request):
    button = request.POST['press']
    a = Comment.objects.get(id=button)
    user = request.user.profile
    for hit in a.hits.all():
        if hit.ra == user.ra:
            return 0
    return 1


def send_email_all():
    for user in Profile.objects.all():
        recipient_list = []
        message = u"Olá, %s.\n Sou o bot de emails do VotaUnicamp e quero agradecer por você ter feito parte de nossa última votação.\n Primeiramente, gostaria de anunciar que o site sofreu algumas mudanças interessantes em seu formato e apresentação. Dentre elas:\n - RG não será mais necessário em novas contas e foi apagado do banco de dados das contas antigas\n - Não mais é possível ver o nome, RA ou RG do aluno nos resultados ou na discussão.\n - No lugar dessas informações será mostrado um nome fictício gerado automaticamente e único para cada usuário.\n - Na questão usuários, agora é obrigatória a criação de uma conta com senha no site.\n - É possível agora apagar sua conta por completo\n - A cada novo comentário em um argumento, todos os usuários envolvidos serão notificados via email da DAC\n Para mais informações, consulte https://github.com/Maronato/votaunicamp/blob/master/README.md\n\n Depois de cerca de duas semanas com as votações para Greve dos Estudantes abertas, conseguimos 473 votos, sendo 141 a favor, 17 abstenções e 315 contra a pauta.\n Você pode consultar os resultados da última pauta em https://votaunicamp.herokuapp.com/prev_results/\n\n Com o fim dessa votação, iniciaremos outra com a pauta Piquetes e ocupações.\n Recebemos essa sugestão inúmeras vezes e concordamos que piquetes são polêmicos e merecem ser debatidos.\n Se tiver interesse, as votações estão disponíveis em https://votaunicamp.herokuapp.com. Contamos com você nos resultados!\n\nAtenciosamente,\nBot de emails" % (user.first_name)
        subject = u"VotaUnicamp: Atualização, resultados e novas votações"
        from_email = "votaunicamp@gmail.com"
        recipient_list.append(user.name[0].lower() + user.ra + '@dac.unicamp.br')
        fail_silently = True
        send_mail(subject, message, from_email, recipient_list, fail_silently)


def change_name(request):
    user = request.user
    if user.is_authenticated:
        nick = email_functions.gen_random_nickname()
        user.profile.nickname = nick
        user.profile.save()
        return redirect('/user_info/')
    return redirect('index')


def delete_account(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        user.delete()
    return redirect('index')


def test(request):
    recipient_list = []
    message = u"Olá,.\n Sou o bot de emails do VotaUnicamp e quero agradecer por você ter feito parte de nossa última votação.\n Primeiramente, gostaria de anunciar que o site sofreu algumas mudanças interessantes em seu formato e apresentação. Dentre elas:\n - RG não será mais necessário em novas contas e foi apagado do banco de dados das contas antigas\n - Não mais é possível ver o nome, RA ou RG do aluno nos resultados ou na discussão.\n - No lugar dessas informações será mostrado um nome fictício gerado automaticamente e único para cada usuário.\n - Na questão usuários, agora é obrigatória a criação de uma conta com senha no site.\n - É possível agora apagar sua conta por completo\n - A cada novo comentário em um argumento, todos os usuários envolvidos serão notificados via email da DAC\n Para mais informações, consulte https://github.com/Maronato/votaunicamp/blob/master/README.md\n\n Depois de cerca de duas semanas com as votações para Greve dos Estudantes abertas, conseguimos 473 votos, sendo 141 a favor, 17 abstenções e 315 contra a pauta.\n Você pode consultar os resultados da última pauta em https://votaunicamp.herokuapp.com/prev_results/\n\n Com o fim dessa votação, iniciaremos outra com a pauta Piquetes e ocupações.\n Recebemos essa sugestão inúmeras vezes e concordamos que piquetes são polêmicos e merecem ser debatidos.\n Se tiver interesse, as votações estão disponíveis em https://votaunicamp.herokuapp.com. Contamos com você nos resultados!\n\nAtenciosamente,\nBot de emails"
    subject = u"VotaUnicamp: Atualização, resultados e novas votações"
    from_email = "votaunicamp@gmail.com"
    recipient_list.append('g169323@dac.unicamp.br')
    fail_silently = True
    send_mail(subject, message, from_email, recipient_list, fail_silently)
    return redirect('index')


def update(request):
    for profile in Profile.objects.all():
        nick = email_functions.gen_random_nickname()
        profile.nickname = nick
        profile.save()
    return redirect('index')


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response
