from django.shortcuts import render

# Create your views here.


def indexCalc1(request):
    return render(request, '_AppCalc1/index.html')
