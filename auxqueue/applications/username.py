from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import CustomUser
import json

@csrf_exempt
def usernameValidator(request):
    username = request.GET.get('username', '')
    try:
        user = CustomUser.objects.get(user_name=username)
        return HttpResponse(json.dumps({'valid': False}))
    except CustomUser.DoesNotExist:
        return HttpResponse(json.dumps({'valid': True}))
