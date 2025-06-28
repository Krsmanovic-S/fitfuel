from django.db import models
from django.core.validators import MinValueValidator
from users.models import CustomUser
import math 


# Represents a category for menu items (Main Course, Drinks etc...)
class MenuItemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='Category of a specific Menu Item')
    index = models.IntegerField(default=0, help_text='Which category shows up first')
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL of the image for this category")
    
    class Meta:
        verbose_name = 'Menu Item Category'
        verbose_name_plural = 'Menu Item Categories'
        ordering = ['index']

    def __str__(self):
        return self.name


# Represents a singular instance of a menu item
class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text='A brief description of the menu item')
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL of the image for this menu item")
    calories = models.IntegerField(default=0, help_text='Calories per 100g')
    carbs = models.IntegerField(default=0, help_text='Carbohydrates per 100g')
    protein = models.IntegerField(default=0, help_text='Protein per 100g')
    fats = models.IntegerField(default=0, help_text='Fats per 100g')
    category = models.ForeignKey(
        MenuItemCategory, on_delete=models.SET_NULL, null=True, 
        blank=True, help_text='The category this menu item belongs to'
    )
    
    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
    
    def __str__(self):
        return f"{self.name} ({self.category.name if self.category else 'Uncategorized'})"


# Represents a specific portion size for a MenuItem, with its own price and amount.
class MenuItemPortion(models.Model):
    menu_item = models.ForeignKey(MenuItem, related_name='portions', on_delete=models.CASCADE, help_text="The menu item this portion belongs to")
    name = models.CharField(max_length=100, help_text="Name of the portion ('Small', 'Regular', etc...)")
    amount_in_grams_ml = models.IntegerField(default=100, help_text="Amount for this portion in grams or milliliters")
    price = models.FloatField(default=10, validators=[MinValueValidator(0.0, message='Price cannot be negative.')])
    discount_percent = models.FloatField(default=0, validators=[MinValueValidator(0.0, message='Discount cannot be negative.')])

    class Meta:
        verbose_name = "Menu Item Portion"
        verbose_name_plural = "Menu Item Portions"
        # A menu item cannot have two portions with the same name
        unique_together = ('menu_item', 'name') 

    def __str__(self):
        return f"{self.menu_item.name} - {self.name} ({self.amount_in_grams_ml}g/ml) - ${self.price}"
    
    def calculate_macros_for_portion(self):
        scale_factor = self.amount_in_grams_ml / 100

        portion_calories = math.ceil(self.menu_item.calories * scale_factor)
        portion_protein = math.ceil(self.menu_item.protein * scale_factor)
        portion_carbs = math.ceil(self.menu_item.carbs * scale_factor)
        portion_fats = math.ceil(self.menu_item.fats * scale_factor)

        return {
            'calories': portion_calories,
            'protein': portion_protein,
            'carbs': portion_carbs,
            'fats': portion_fats
        }
        
    def get_final_price(self):
        if self.discount_percent and self.discount_percent > 0:
            discount_amount = self.price * (self.discount_percent / 100)
            return round(self.price - discount_amount, 2)
        return round(self.price, 2)
        
        
class Order(models.Model):
    stripe_checkout_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=200, blank=True)
    customer_address = models.CharField(max_length=200, blank=True)
    customer_zipcode = models.CharField(max_length=200, blank=True)
    
    total_price = models.FloatField(default=0.0)

    order_date = models.DateTimeField(auto_now_add=True)    
    has_paid = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    
    order_items = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer_email}"
    
    def get_order_macros(self):
        macros = {
            'carbs': 0,
            'protein': 0,
            'fats': 0
        }
        
        for item in self.order_items:
            portion = MenuItemPortion.objects.get(id=item['portion_id'])
            portion_macros = portion.calculate_macros_for_portion()
            
            macros['carbs'] += portion_macros['carbs']
            macros['protein'] += portion_macros['protein']
            macros['fats'] += portion_macros['fats']
            
        return macros
            
            
            
