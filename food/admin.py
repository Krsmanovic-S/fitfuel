from django.contrib import admin
from .models import MenuItemCategory, MenuItem, MenuItemPortion, Order


@admin.register(MenuItemCategory)
class MenuItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class MenuItemPortionInline(admin.TabularInline):
    model = MenuItemPortion
    extra = 1
    fields = ('name', 'amount_in_grams_ml', 'price', 'discount_percent')
    
    
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'calories',)
    list_filter = ('category',)
    search_fields = ('name', 'description', 'category__name')
    inlines = [MenuItemPortionInline]
    
    
admin.site.register(Order)

admin.site.site_header = "Fit-Fuel Administration"
admin.site.site_title = "Fit-Fuel Admin"
    