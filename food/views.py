from django.shortcuts import render
from .models import MenuItem, MenuItemCategory, MenuItemPortion, Order
from django.views.decorators.csrf import csrf_exempt
import json, stripe
from django.http import JsonResponse, HttpResponse  
from django.conf import settings
from django.urls import reverse
from .forms import CheckoutForm
from django.db import transaction


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
    # This will be used in the checkout.html for display purposes
    cart_context = []
    total_cart_price = 0

    if 'cart' in request.session:
        cart = request.session['cart']
        
        # Get all items from the Javascript cart and use it for our context 
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
    
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    checkout_form = CheckoutForm()
    
    return render(request, 'food/checkout.html', {
        'cart_items': cart_context, 
        'total_cart_price': total_cart_price,
        'stripe_publishable_key': stripe_publishable_key,
        'checkout_form': checkout_form
    })


@csrf_exempt
def create_checkout_session(request):
    request_data = json.loads(request.body)
    
    # Make sure the user information from the form is correct before proceeding
    form = CheckoutForm(request_data)
    if not form.is_valid():
        return JsonResponse({'error': form.errors.as_json()}, status=400)
    
    user_email = form.cleaned_data['email']
    user_phone = form.cleaned_data['phone']
    user_address = form.cleaned_data['address']
    user_zipcode = form.cleaned_data['zipcode']

    current_cart = request.session.get('cart', {})
    line_items = []
    
    # Loop through the Javascript cart to generate information needed for Stripe
    for portion_id, quantity in current_cart.items():
        portion = MenuItemPortion.objects.get(id=int(portion_id))
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': f"{portion.menu_item.name} ({portion.name})",
                    'images': [portion.menu_item.image_url] if portion.menu_item.image_url else [],
                    # This metadata will be used for creating orders later
                    'metadata': {
                        'menu_item_name': portion.menu_item.name,
                        'portion_name': portion.name,
                    }
                },
                'unit_amount': int(portion.get_final_price() * 100),
            },
            'quantity': quantity,
        }) 

    # Create the Stripe session for payment
    stripe.api_key = settings.STRIPE_SECRET_KEY  
    checkout_session = stripe.checkout.Session.create(
        customer_email= user_email,
        payment_method_types= ['card'],
        line_items= line_items,
        mode= 'payment',
        metadata={
            'customer_email': user_email,
            'customer_phone': user_phone,
            'customer_address': user_address,
            'customer_zipcode': user_zipcode,
        },
        success_url= request.build_absolute_uri(reverse('success')) +
        "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url= request.build_absolute_uri(reverse('failed')),
    )
    
    return JsonResponse({'sessionId': checkout_session.id})
    
    
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None
    
    # Verify that the request came for Stripe - security purpose
    try:
        event = stripe.Webhook.construct_event(
            payload, 
            request.META.get('HTTP_STRIPE_SIGNATURE'), 
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError as e:
        print(f'Request did not come from Stripe, or API_SECRET is wrong')
        return HttpResponse(status=400)
    except Exception as e:
        print(f'Exception caught when trying to verify Stripe request, error: {e}')
        return HttpResponse(status=500)

    if event['type'] == 'checkout.session.completed':
        # Checkout session object
        session = event['data']['object']

        # Prevention of duplicate orders in case of multiple webhooks at the same time
        try:
            with transaction.atomic():
                if Order.objects.filter(stripe_checkout_session_id=session.id).exists():
                    return HttpResponse(status=200)

                full_session = stripe.checkout.Session.retrieve(
                    session.id,
                    expand=['line_items']
                )
                
                # Retrieve the metadata that was passed during session creation
                customer_email = full_session.metadata.get('customer_email', '') 
                customer_phone = full_session.metadata.get('customer_phone', '')
                customer_address = full_session.metadata.get('customer_address', '')
                customer_zipcode = full_session.metadata.get('customer_zipcode', '')

                # Stripe has amount total in cents so we need to recalculate it here
                order_total = session.amount_total / 100 

                # This is to gain access to the product metadata
                full_session_items = stripe.checkout.Session.list_line_items(
                    session['id'], expand=['data.price.product']
                )

                # Get all line items from the checkout session and format them for the order
                processed_order_items = []
                for item in full_session_items:
                    product = item['price']['product']
                    
                    menu_item_name = product['metadata'].get('menu_item_name', '')
                    portion_name = product['metadata'].get('portion_name', '')
                    
                    # JSON Format for the Order
                    processed_order_items.append({
                        'item_name': menu_item_name,
                        'portion_name': portion_name,
                        'quantity': item.quantity,
                        'total_price': item.amount_total / 100,
                    })
                
                # Creating and saving the order
                order = Order.objects.create(
                    stripe_checkout_session_id=session.id,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    customer_address=customer_address,
                    customer_zipcode=customer_zipcode,
                    total_price=order_total,
                    order_items=processed_order_items,
                    has_paid=True,
                )
                order.save()
                # TODO: Could add a confimation email here later
        except stripe.error.StripeError as e:
            print(f'Stripe API call error: {e}')
            return HttpResponse(status=400)
        except Exception as e:
            print(f'Exception error in stripe_webhook method: {e}')
            return HttpResponse(status=500)

    return HttpResponse(status=200)


def payment_success_view(request):
    # Clearing the cart after a successfull payment
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
    
    return render(request, 'food/payment/payment_success.html')


def payment_failed_view(request):
    return render(request, 'food/payment/payment_failed.html')