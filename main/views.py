from django.shortcuts import render,redirect
from .models import Request

#def requests_page(request):
    #return render(request, 'requests.html')
def requests_page(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        car_model = request.POST.get('car_model')
        license_plate = request.POST.get('license_plate')

        Request.objects.create(
            phone=phone,
            car_model=car_model,
            license_plate=license_plate
        )
        return redirect('/requests/')

    requests = Request.objects.all()
    return render(request, 'requests.html', {'requests': requests})
def home(request):
    return render(request, 'base.html')  # или отдельный home.html