from django.shortcuts import render
from .models import MenuItem, MenuItemCategory, MenuItemPortion
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse


def index(request):
    return render(request, 'food/index.html')


def menu(request):
    menu_items = MenuItem.objects.all()
    menu_categories = MenuItemCategory.objects.all()
    return render(request, 'food/menu.html', {'menu_items': menu_items, 'menu_categories': menu_categories})


@csrf_exempt 
def update_session_cart(request):
    try:
        raw_body = request.body.decode('utf-8')
        data = json.loads(raw_body)
        cart_from_js = data.get('cart', {})

        valid_cart = {}
        
        if cart_from_js:
            for portion_id, data_list in cart_from_js.items():
                try:
                    valid_cart[portion_id] = int(data_list[1])

                except (ValueError, TypeError, IndexError) as e:
                    print(f"Invalid item conversion from JS, Portion ID String:'{portion_id}', Data:'{data_list}'. Error: {e}")
                    continue

        request.session['cart'] = valid_cart
        request.session.modified = True

        return JsonResponse({'status': 'success', 'message': 'Cart session updated.'})
    except Exception as e:
        print(f"Error occurred in update_session_cart(): {e}")
        
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)


def checkout_page(request):
    cart_context = []
    total_cart_price = 0

    if 'cart' in request.session:
        cart = request.session['cart']
        
        for portion_id, quantity in cart.items():

            try:
                portion = MenuItemPortion.objects.get(id=portion_id)
                final_price = portion.get_final_price()
                item_total = final_price * quantity
                image_url = portion.menu_item.image_url

                cart_context.append({
                    'menu_item_name': portion.menu_item.name,
                    'portion_name': portion.name,
                    'quantity': quantity,
                    'price_per_item': final_price,
                    'item_total': item_total,
                    'image_url': image_url,
                })
                total_cart_price += item_total

            except MenuItemPortion.DoesNotExist:
                print(f"Portion with ID {portion_id} not found in checkout_page().")
                continue
    
    return render(request, 'food/checkout.html', {
        'cart_items': cart_context, 'total_cart_price': total_cart_price})

