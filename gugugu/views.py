from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.urls import reverse
from django.utils.translation import gettext as _
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

    comments = Comment.objects.all()
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

    if member.exists():
        chats = member.retrieve_subsequent_chats()
    else:
        return render(request, 'gugugu/room-enter.html', dict(room=room))

    return render(request, 'gugugu/room.html', dict(room=room))


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
