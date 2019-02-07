from django import forms
from . import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['nickname', 'content']


class RoomForm(forms.ModelForm):
    class Meta:
        model = models.Room
        fields = ['name']


class MemberForm(forms.ModelForm):
    class Meta:
        model = models.Member
        fields = ['name']


class MessageForm(forms.ModelForm):
    class Meta:
        model = models.Message
        fields = ['text']
