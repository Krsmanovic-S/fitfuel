from django.shortcuts import render
from .models import MenuItem, MenuItemCategory


def index(request):
    return render(request, 'food/index.html')


def menu(request):
    menu_items = MenuItem.objects.all()
    menu_categories = MenuItemCategory.objects.all()
    return render(request, 'food/menu.html', {'menu_items': menu_items, 'menu_categories': menu_categories})