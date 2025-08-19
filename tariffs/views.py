from django.shortcuts import render
from .models import Region, Tariff

def index(request):
    regions = Region.objects.all()
    tariffs = Tariff.objects.all()
    return render(request, "index.html", {"regions": regions, "tariffs": tariffs})
