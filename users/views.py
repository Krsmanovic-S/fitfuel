from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm, LoginForm, UserEditForm
from food.models import Order, MenuItemPortion


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST, request=request)
        if register_form.is_valid():
            new_user = register_form.save(commit=False)
            new_user.set_password(register_form.cleaned_data['password'])            
            new_user.save()
            
            login(request, new_user)
            return redirect('index')
    register_form = RegisterForm()
    return render(request, 'users/register.html', {'register_form': register_form})


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST, request=request)
        if login_form.is_valid():
            data = login_form.cleaned_data
            user = authenticate(request=request, username=data['email'], password=data['password'])
            
            if user:
                login(request, user)
                return redirect('index')

    login_form = LoginForm()
    return render(request, 'users/login.html', {'login_form': login_form})


def logout_view(request):
    logout(request)
    return render(request, 'food/index.html')
    

@login_required
@csrf_exempt
def profile(request):
    if request.method == 'POST':
        user_edit_form = UserEditForm(request.POST, instance=request.user)
        if user_edit_form.is_valid():
            user_edit_form.save()
            return redirect('profile')
    else:
        # Initialize the form with the current users data for pre-population
        user_edit_form = UserEditForm(instance=request.user)

    past_orders = Order.objects.filter(customer_email=request.user.email)
        
    all_macros = {
        'carbs': 0,
        'protein': 0,
        'fats': 0
    }
    for order in past_orders:
        individual_macros = order.get_order_macros()

        all_macros['carbs'] += individual_macros['carbs']
        all_macros['protein'] += individual_macros['protein']
        all_macros['fats'] += individual_macros['fats']
        
    return render(request, 'users/profile.html', {
        'user_edit_form': user_edit_form,
        'past_orders': past_orders,
        'all_macros': all_macros
    })
    
    
def order_view(request, id):
    order = Order.objects.get(id=id)

    context_items = []
    for item in order.order_items:
        portion = MenuItemPortion.objects.get(id=item['portion_id'])
        
        context_items.append({
            'menu_item_name': item['item_name'],
            'portion_name': item['portion_name'],
            'quantity': item['quantity'],
            'price_per_item': portion.get_final_price() * item['quantity'],
            'image_url': portion.menu_item.image_url,
        })
        
    return render(request, 'users/order_view.html', {'order': order, 'context_items': context_items})
        
    