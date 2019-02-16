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
    print(claps_updated_messages)

    data = {
        'messages': [],
        'claps': [],
    }

    for message in messages:
        data['messages'].append({
            'sender': message.member.name,
            'text': message.text,
            'claps': message.claps,
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

    if request.method == 'POST':
        if Clap.objects.filter(message=message, member=member).count() < 50:
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
    if form.is_valid():
        name = form.cleaned_data['name']
        room = Room.objects.filter(name=name, active=True)
        valid = True
        taken = room.exists() and not room.get().deactivate()
    else:
        valid = False
        taken = False

    error_msg = ''
    if not valid:
        error_msg = form.errors['name'][0]

    else:
        if not taken:
            error_msg = _('A room with that name has been recently used.')

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
