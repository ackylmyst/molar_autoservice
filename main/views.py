from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import User, Client, Car, Order


def orders_page(request):
    if request.method == "POST":
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        car_brand = request.POST.get('car_brand')
        car_model = request.POST.get('car_model')
        car_plate = request.POST.get('car_plate')
        vin = request.POST.get('vin', '')
        car_year = request.POST.get('car_year', None)
        car_color = request.POST.get('car_color', '')
        problem_desc = request.POST.get('problem_desc', '')
        
        if not all([name, surname, email, phone, car_brand, car_model, car_plate]):
            messages.error(request, 'Пожалуйста, заполните все поля')
            return redirect('/')
        
        try:
            with transaction.atomic():
                user = User.objects.filter(email=email).first()
                
                if not user:
                    user = User(
                        name=name,
                        surname=surname,
                        email=email
                    )
                    temp_password = f"auto_{email.split('@')[0]}_{phone[-4:]}"
                    user.set_password(temp_password)
                    user.save()
                    messages.success(request, f'Новый пользователь {surname} {name} создан!')
                else:
                    messages.info(request, f'Добро пожаловать, {user.surname} {user.name}!')
                
                client = Client.objects.filter(user_id=user).first()
                
                if not client:
                    client = Client(
                        user_id=user,
                        phone=phone
                    )
                    client.save()
                    messages.info(request, 'Профиль клиента создан!')
                else:
                    if client.phone != phone:
                        client.phone = phone
                        client.save()
                
                existing_car = Car.objects.filter(plate_number=car_plate.upper()).first()
                
                if existing_car:
                    if existing_car.client_id == user.id:
                        car = existing_car
                        messages.info(request, f'Машина {car_plate} уже есть в системе')
                    else:
                        owner = User.objects.filter(id=existing_car.client_id).first()
                        messages.error(request, f'Машина с госномером {car_plate} закреплена за {owner.surname} {owner.name}')
                        return redirect('/')
                else:
                    car = Car.objects.create(
                        client_id=user.id,
                        brand=car_brand,
                        model=car_model,
                        vin=vin if vin else '',
                        plate_number=car_plate.upper(),
                        year_produced=car_year if car_year else None,
                        color=car_color if car_color else None
                    )
                    messages.success(request, 'Новая машина добавлена!')
                
                order = Order.objects.create(
                    client_id=client,
                    car_id=car.id,
                    problem_desc=problem_desc,
                    status_id=1
                )
                
                messages.success(request, f'Заявка #{order.id} успешно создана!')
                return redirect('/')
                
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return redirect('/')
    
    orders = Order.objects.select_related('client_id__user_id').all().order_by('-created_at')
    
    for order in orders:
        if order.car_id:
            try:
                order.car = Car.objects.get(id=order.car_id)
            except Car.DoesNotExist:
                order.car = None
        else:
            order.car = None
    
    return render(request, 'orders.html', {'orders': orders})


def get_client_by_phone(request):
    phone = request.GET.get('phone', '')
    
    if phone:
        client = Client.objects.filter(phone=phone).select_related('user_id').first()
        if client:
            return JsonResponse({
                'found': True,
                'name': client.user_id.name,
                'surname': client.user_id.surname,
                'email': client.user_id.email,
                'phone': client.phone,
                'client_id': client.user_id.id
            })
    return JsonResponse({'found': False})


def get_car_by_plate(request):
    plate = request.GET.get('plate', '').upper()
    
    if plate:
        car = Car.objects.filter(plate_number=plate).first()
        if car:
            owner = User.objects.filter(id=car.client_id).first()
            return JsonResponse({
                'found': True,
                'brand': car.brand,
                'model': car.model,
                'vin': car.vin or '',
                'year': car.year_produced,
                'color': car.color or '',
                'owner_client_id': car.client_id,
                'owner_name': f"{owner.surname} {owner.name}" if owner else 'неизвестен'
            })
    return JsonResponse({'found': False})


def check_plate_owner(request):
    plate = request.GET.get('plate', '').upper()
    current_client_id = request.GET.get('client_id', None)
    
    if plate:
        car = Car.objects.filter(plate_number=plate).first()
        if car:
            if current_client_id and str(car.client_id) == current_client_id:
                return JsonResponse({
                    'is_owner': True,
                    'message': 'Это ваша машина',
                })
            else:
                owner = User.objects.filter(id=car.client_id).first()
                return JsonResponse({
                    'is_owner': False,
                    'owner_name': f"{owner.surname} {owner.name}" if owner else 'другим клиентом',
                    'message': f'Машина закреплена за {owner.surname} {owner.name}'
                })
    return JsonResponse({'is_owner': True, 'message': ''})
