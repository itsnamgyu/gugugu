from django.db import models, transaction
from django.utils.translation import ugettext as _
from django.core.validators import validate_slug
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone


class Comment(models.Model):
    date = models.DateTimeField(_('Date'), auto_now_add=True, editable=False)
    nickname = models.TextField(_('Nickname'))
    content = models.TextField(_('Content'))
    likes = models.IntegerField(_('Likes'), default=0)


class Room(models.Model):
    date_created = models.DateTimeField(_('Date Created'), default=timezone.now, editable=False)
    date_polled = models.DateTimeField(_('Date Last Polled'), default=timezone.now)
    date_updated = models.DateTimeField(_('Date Updated'), default=timezone.now)
    date_deactivated = models.DateTimeField(_('Date Deactivated'), default=None, null=True, blank=True)
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=255, validators=[validate_slug])
    deactivate_delta_sec = models.IntegerField(default=12*3600)

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
            self.active = False
            self.date_deactivated = timezone.now()
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
    session_key = models.CharField(_('Session Key'), max_length=255)
    name = models.CharField(max_length=32, null=True, blank=False, validators=[UnicodeUsernameValidator])
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)

    def retrieve_new_messages(self, n=300):
        # TODO: need to limit the number of chats... (but how?)
        with transaction.atomic():
            start = Member.objects.select_for_update().get(pk=self.pk).date_updated
            end = timezone.now()
            Member.objects.filter(pk=self.pk).update(date_updated=end)
        messages = list(self.room.message_set.all().filter(
            date_sent__gt=start, date_sent__lt=end).reverse())

        return messages

    def retrieve_all_messages(self, n=300):
        # TODO: need to limit the number of chats... (but how?)
        self.date_updated = timezone.now()
        self.save()
        messages = list(self.room.message_set.all().filter(
            date_sent__gt=self.date_joined, date_sent__lt=self.date_updated).reverse()[:300])
        return messages

    class Meta:
        unique_together = ('room', 'name')

    def __str__(self):
        return self.name


class Message(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_sent = models.DateTimeField(_('Date Sent'), auto_now_add=True, editable=False)
    text = models.TextField()

    def __str__(self):
        return 'Message from {} in {} on {}'.format(self.member.name, self.room.name, self.date_sent.strftime('%x %X'))
