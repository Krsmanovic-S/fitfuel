from django.contrib import admin
from .models import MenuItemCategory, MenuItem, MenuItemPortion


@admin.register(MenuItemCategory)
class MenuItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class MenuItemPortionInline(admin.TabularInline):
    model = MenuItemPortion
    extra = 1
    fields = ('name', 'amount_in_grams_ml', 'price', 'is_liquid')
    
    
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'calories',)
    list_filter = ('category',)
    search_fields = ('name', 'description', 'category__name')
    inlines = [MenuItemPortionInline]
    