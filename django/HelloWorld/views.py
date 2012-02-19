from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from models.hello import Hello

def index(request):
    return HttpResponse("Hello World!")

def dtl_hello(request):
    return render_to_response('hellos.html')

def dtl_sql(request):
    data = Hello.objects.all()
    return render_to_response('hellodb.html', {'data': data})
