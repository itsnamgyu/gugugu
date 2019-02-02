from django.db import models
from django.utils.translation import ugettext as _


class Comment(models.Model):
    date = models.DateTimeField(_('Date'), auto_now_add=True, editable=False)
    nickname = models.TextField(_('Nickname'))
    content = models.TextField(_('Content'))
    likes = models.IntegerField(_('Likes'), default=0)
