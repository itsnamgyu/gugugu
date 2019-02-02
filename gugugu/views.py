from django.shortcuts import render
from .forms import CommentForm
from .models import Comment


def index(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            form = None
    else:
        form = None
    comments = Comment.objects.all()
    return render(request, 'gugugu/index.html', {
        'comments': comments,
        'form': form,
    })
