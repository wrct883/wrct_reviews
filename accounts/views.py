from django.shortcuts import get_object_or_404, render
from .models import User

# this is the account profile page
def detail(request, pk):
    obj = get_object_or_404(User, pk=pk) if pk else request.user
    context = {
        'table': 'user',
        'object': obj,
        'fields': ('djname', 'phone', 'email', 'auth_level'),
    }
    return render(request, 'library/detail.html', context)
