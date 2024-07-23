from shop.models import Cart, Category


def get_user_cart_count(request):
    try:
        client_cart = Cart.objects.get(client=request.client)
    except:
        return 0
    return client_cart.items.all().count()


def global_variables(request):
    return {
        'categories': Category.objects.all(),
        'cart_count': get_user_cart_count(request)
    }
