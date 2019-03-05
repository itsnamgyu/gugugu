from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.utils import IntegrityError


def index(request):
    form = None
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))

    room_form = RoomForm(request.POST)

    if request.POST.get('name', '') == '':
        valid = None
    else:
        valid = False

    if room_form.is_valid():
        name = room_form.cleaned_data['name']
        room = Room.objects.filter(name=name, active=True)
        if room.exists() and not room.get().deactivate():
            pass
        elif name in ['sg-talk', 'gu']:
            pass
        else:
            new = room_form.save()
            if new.activate():
                new.save()
                return redirect(reverse('room', kwargs=dict(name=name)))
            else:
                new.delete()

    comments = Comment.objects.all()[::-1]
    return render(request, 'gugugu/index.html', {
        'comments': comments,
        'form': form,
        'room_form': room_form,
        'valid': valid,
        'validate_room_name_url': reverse('validate_room_name'),
    })


def talk(request):
    """
    Custom view for sg seminar event!
    :param request:
    :return:
    """
    registered = False
    user = None
    if request.user.is_authenticated:
        user = request.user
        if TalkRegistration.objects.filter(user=request.user).exists():
            registered = True

    return render(request, 'gugugu/talk-index.html', {
        'registered': registered,
        'user': user
    })


def talk_room(request):
    registered = False
    user: User = None
    if request.user.is_authenticated:
        user = request.user
        registered = TalkRegistration.objects.filter(user=request.user).exists()
    if not registered:
        return redirect(reverse('talk'))

    name = 'sg-talk'
    registration = user.registration

    room_query = Room.objects.filter(name=name)
    if not room_query.exists():
        with transaction.atomic():
            if not room_query.exists():
                Room(name=name, active=True).save()
    room = room_query.get()

    message_form = MessageForm(prefix='message')
    member = Member.objects.all().filter(room=room, session_key=request.session.session_key)
    if member.exists():
        member = member.get()
    else:
        member = Member(room=room, session_key=request.session.session_key, name=registration.name)
        member.user = user
        member.save()
        
    messages = member.retrieve_all_messages()[::-1] # TODO: for some reason?
    # TODO: is there any better logic?
    for message in messages:
        message.my_claps = message.get_my_claps_count(member.id)
    return render(request, 'gugugu/room.html', {
        'room': room,
        'messages': messages,
        'member': member,
        'message_form': message_form,
    })


def talk_register(request):
    if request.user.is_authenticated:
        if TalkRegistration.objects.filter(user=request.user).exists():
            return redirect(reverse('talk'))
    else:
        return redirect(reverse('talk'))

    form = None
    if request.method == 'POST':
        form = TalkRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.save()
            return redirect(reverse('talk'))

    if form is None:
        form = TalkRegistrationForm()

    return render(request, 'gugugu/talk-register.html', {
        'form': form
    })


def admin(request):
    return redirect(reverse('admin_stats'))


def admin_stats(request):
    regs = list(TalkRegistration.objects.all())

    reg_dicts = list()
    for reg in regs:
        reg_dicts.append(dict(
            registration=reg,
            claps_received=reg.claps_received(),
            claps_sent=reg.claps_sent(),
            messages_sent=reg.messages_sent(),
            characters_sent=reg.characters_sent(),
        ))

    # sorted TalkRegistration dicts
    claps_received = sorted(reg_dicts, key=lambda d: d['claps_received'], reverse=True)[:5]
    claps_sent = sorted(reg_dicts, key=lambda d: d['claps_sent'], reverse=True)[:5]
    characters_sent = sorted(reg_dicts, key=lambda d: d['characters_sent'], reverse=True)[:5]

    total_claps = 0
    total_messages = 0
    for d in reg_dicts:
        total_claps += d['claps_received']
        total_messages += d['messages_sent']
    total_registrations = TalkRegistration.objects.all().count()

    stats = dict(
        total_claps=total_claps,
        total_messages=total_messages,
        total_registrations=total_registrations,
    )

    departments = [
        '컴퓨터공학과',
        '경영학과',
        '아트앤테크놀로지',
        '전자공학',
        '기타',
    ]
    registrations_by_department = dict()
    for department in departments:
        registrations_by_department[department] = TalkRegistration.objects.filter(department=department).count()

    return render(request, 'gugugu/admin-stats.html', {
        'stats': stats,
        'registrations_by_department': registrations_by_department,
        'd_by_claps_received': claps_received,
        'd_by_claps_sent': claps_sent,
        'd_by_characters_sent': characters_sent,
    })


def admin_questions_claps(request):
    sg_room = Room.objects.all().get(name='sg-talk')
    messages = Message.objects.all().filter(room=sg_room).annotate(clap_count=Count('claps')).order_by('-clap_count')

    return render(request, 'gugugu/admin-questions-claps.html', {
        'messages': messages,
    })


def admin_questions_time(request):
    sg_room = Room.objects.all().get(name='sg-talk')
    messages = Message.objects.all().filter(room=sg_room).order_by('-date_sent')

    return render(request, 'gugugu/admin-questions-time.html', {
        'messages': messages,
    })


def room(request, name):
    room = get_object_or_404(Room, name=name, active=True)
    member = Member.objects.all().filter(room=room, session_key=request.session.session_key)
    message_form = MessageForm(prefix='message')
    form = MemberForm(prefix='member')

    if member.exists():
        member = member.get()
        if request.method == 'POST':
            # TODO: this should be AJAX
            message_form = MessageForm(request.POST, prefix='message')
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.member = member
                message.room = room
                message.save()
                return redirect(reverse('room', kwargs={
                    'name': name,
                }))
    else:
        member = None
        if request.method == 'POST':
            form = MemberForm(request.POST, prefix='member')
            if form.is_valid():
                member = form.save(commit=False)
                if not request.session.session_key:
                    request.session.create()
                # TODO: better way to process this in the Model layer?
                member.session_key = request.session.session_key
                member.room = room
                member.save()
                return redirect(reverse('room', kwargs={
                    'name': name,
                }))

    if member:
        messages = member.retrieve_all_messages()[::-1]  # TODO: for some reason?
        # TODO: is there any better logic?
        for message in messages:
            message.my_claps = message.get_my_claps_count(member.id)
        return render(request, 'gugugu/room.html', {
            'room': room,
            'messages': messages,
            'member': member,
            'message_form': message_form,
        })
    else:
        return render(request, 'gugugu/room-enter.html', {
            'room': room,
            'member_form': form,
        })


def room_ajax(request, pk):
    room = get_object_or_404(Room, pk=pk)
    member = get_object_or_404(Member, room=room, session_key=request.session.session_key)
    room.date_polled = timezone.now()

    if request.method == 'POST':
        form = MessageForm(request.POST, prefix='message')
        if form.is_valid():
            message = form.save(commit=False)
            message.member = member
            message.room = room
            message.save()
            room.date_updated = timezone.now()

    room.save()
    updated_data = member.retrieve_new_messages()
    messages = updated_data["messages"]
    claps_updated_messages = updated_data["claps_updated_messages"]

    data = {
        'messages': [],
        'claps': [],
    }

    for message in messages:
        data['messages'].append({
            'sender': message.member.name,
            'text': message.text,
            'claps': message.claps.count(),
            'pk': message.pk,
        })

    for message in claps_updated_messages:
        data['claps'].append({
            'message_pk': message.pk,
            'claps': message.claps.count(),
        })

    return JsonResponse(data)


def clap_ajax(request, room_id, message_id):
    room = get_object_or_404(Room, pk=room_id)
    message = get_object_or_404(Message, pk=message_id)
    member = get_object_or_404(Member, room=room, session_key=request.session.session_key)
    clap_count = request.POST.get('claps')

    if request.method == 'POST':
        if Clap.objects.filter(message=message, member=member).count() < 50:
            with transaction.atomic():
                for i in range(0, int(clap_count)):
                    clap = Clap(message=message, member=member)
                    clap.save()
            message.date_claps_updated = timezone.now()
            message.save()
            room.date_updated = timezone.now()

    room.save()
    data = {
        'memberId': member.id,
        'messageId': message.id,
    }
    return JsonResponse(data)


def validate_room_name(request):
    form = RoomForm(request.GET)
    error_msg = ''

    reserved = False
    taken = False
    if form.is_valid():
        name = form.cleaned_data['name']
        room = Room.objects.filter(name=name, active=True)
        if name in ['sg-talk', 'gu']:
            valid = False
            reserved = True
        else:
            valid = True
            taken = room.exists() and not room.get().deactivate()
    else:
        valid = False
        taken = True

    if not valid:
        if taken:
            error_msg = _('A room with that name has been recently used.')
        elif reserved:
            error_msg = _('That name is reserved')
        else:
            error_msg = form.errors['name'][0]

    data = {
        'usable': valid and not taken,
        'error_msg': error_msg
    }

    return JsonResponse(data)


def validate_member_name(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    form = MemberForm(request.GET)

    usable = False
    if form.is_valid():
        if room.member_set.all().filter(name=form.cleaned_data['name']).exists():
            usable = True

    data = dict(
        usable=usable,
    )

    return JsonResponse(data)
