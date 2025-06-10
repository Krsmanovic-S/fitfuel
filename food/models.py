from django.db import models


# Represents a category for menu items (Main Course, Drinks etc...)
class MenuItemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='Category of a specific Menu Item')

    class Meta:
        verbose_name = 'Menu Item Category'
        verbose_name_plural = 'Menu Item Categories'
        ordering = ['name']

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
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, help_text="The menu item this portion belongs to")
    name = models.CharField(max_length=100, help_text="Name of the portion ('Small', 'Regular', etc...)")
    amount_in_grams_ml = models.IntegerField(default=100, help_text="Amount for this portion in grams or milliliters")
    price = models.FloatField()
    is_liquid = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Menu Item Portion"
        verbose_name_plural = "Menu Item Portions"
        # A menu item cannot have two portions with the same name
        unique_together = ('menu_item', 'name') 

    def __str__(self):
        return f"{self.menu_item.name} - {self.name} ({self.amount_in_grams_ml}g/ml) - ${self.price}"