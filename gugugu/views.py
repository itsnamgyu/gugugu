from django.shortcuts import render, redirect
from .forms import CommentForm
from .models import Comment
from django.urls import reverse


def index(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))

    form = None
    comments = Comment.objects.all()
    return render(request, 'gugugu/index.html', {
        'comments': comments,
        'form': form,
    })
