from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.core.validators import validate_slug
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import User
from django.utils import timezone


class Comment(models.Model):
    date = models.DateTimeField(_('Date'), auto_now_add=True, editable=False)
    nickname = models.TextField(_('Nickname'))
    content = models.TextField(_('Content'))
    likes = models.IntegerField(_('Likes'), default=0)


class Room(models.Model):
    DEFAULT_DEACTIVATE_DELTA = 12 * 3600

    date_created = models.DateTimeField(_('Date Created'), default=timezone.now, editable=False)
    date_polled = models.DateTimeField(_('Date Last Polled'), default=timezone.now)
    date_updated = models.DateTimeField(_('Date Updated'), default=timezone.now)
    date_deactivated = models.DateTimeField(_('Date Deactivated'), default=None, null=True, blank=True)
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=255, validators=[validate_slug])
    deactivate_delta_sec = models.IntegerField(default=DEFAULT_DEACTIVATE_DELTA)

    owner = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True)

    @property
    def registered(self):
        return self.owner is not None

    def deactivate_and_return_none(self):
        self._deactivate()
        return None

    def _deactivate(self):
        """
        Actually deactivates the chat room
        :return:
        """
        self.active = False
        self.date_deactivated = timezone.now()

    def deactivate(self):
        """
        Deactivate chat room if criteria is met (not polled for a long time)

        :return:
        Success
        """
        if not self.active:
            return False
        delta = timezone.now() - self.date_polled
        delta_sec = delta.days * 43200 + delta.seconds
        if delta_sec > self.deactivate_delta_sec:
            self._deactivate()
            return True

    @transaction.atomic
    def activate(self):
        """
        Activate chat room if there is no active chat room with
        the same name

        :return:
        Success
        """
        if Room.objects.all().filter(name=self.name, active=True).exists():
            return False
        else:
            self.active = True
            return True

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    Each "user" is assigned one Member for each chatroom.

    When an anonymous user (who are identified by their session keys) enters a Room,
    a Member object associated with that Room is initialized with their session key.
    The User object is ignored.

    When a registered user enters a Room, a Member associated with that Room is initialized
    with their User object. The session key of the currently logged in User is also saved.
    If the same User enters the Room using a different session key (from a different device),
    then the previous session is invalidated and the Member's session_key field is updated
    with the new session key. *Hence, there can't be more than one Member associated with
    the same room and user at the same time.
    """
    session_key = models.CharField(_('Session Key'), max_length=255, null=True)
    name = models.CharField(max_length=32, null=True, blank=False, validators=[UnicodeUsernameValidator])
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def retrieve_new_messages(self, n=300):
        # TODO: need to limit the number of chats... (but how?)
        with transaction.atomic():
            start = Member.objects.select_for_update().get(pk=self.pk).date_updated
            end = timezone.now()
            Member.objects.filter(pk=self.pk).update(date_updated=end)
        messages = list(self.room.message_set.all().filter(
            date_sent__gt=start, date_sent__lt=end).reverse())

        claps_updated_messages = list(self.room.message_set.all().filter(
            date_claps_updated__gt=start, date_claps_updated__lt=end).reverse())

        updated_data = {"messages": messages, "claps_updated_messages": claps_updated_messages}

        return updated_data

    def retrieve_all_messages(self, n=300):
        # TODO: need to limit the number of chats... (but how?)
        self.date_updated = timezone.now()
        self.save()
        messages = list(self.room.message_set.all().filter(
        #   date_sent__gt=self.date_joined, date_sent__lt=self.date_updated).reverse()[:300])
            date_sent__lt=self.date_updated).reverse()[:300])  # temp
        return messages

    class Meta:
        unique_together = (('room', 'name'), ('room', 'user'))

    @property
    def registered(self):
        return self.user is not None

    def __str__(self):
        return self.name


class Message(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_sent = models.DateTimeField(_('Date Sent'), auto_now_add=True, editable=False)
    text = models.TextField(max_length=1024)

    date_claps_updated = models.DateTimeField(_('Date Claps Updated'), default=timezone.now)

    def get_my_claps_count(self, member_id):
        member_message_claps = self.claps.filter(member_id=member_id)
        return member_message_claps.count()

    def __str__(self):
        return 'Message from {} in {} on {}'.format(self.member.name, self.room.name, self.date_sent.strftime('%x %X'))


class Clap(models.Model):
    message = models.ForeignKey(Message, related_name='claps', on_delete=models.CASCADE)
    member = models.ForeignKey(Member, related_name='claps', on_delete=models.CASCADE)
    date_created = models.DateTimeField(_('Date Created'), default=timezone.now, editable=False)

    def __str__(self):
        return '{} claped {} message'.format(self.member.name, self.message.text)


class TalkRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    department = models.CharField(max_length=25)
    student_id = models.IntegerField()
    year = models.IntegerField()
    interest = models.CharField(max_length=100)
    career_path = models.CharField(max_length=100)
    inquiry = models.TextField()
