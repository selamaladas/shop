import random
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from shop.models import Product, Category, Cart, CartItem, Client, Order, OrderItem
from django.contrib.auth.hashers import make_password


def index(request):
    add_to_cart(request)
    return render(request, 'shop/index.html', {
        'products': Product.objects.all()[:10]
    })


def users(request):
    return render(request, 'shop/users/users.html', {
        'users': Client.objects.all()
    })


def user(request, user_id):
    return render(request, 'shop/users/profil.html', {
        'user': Client.objects.get(pk=user_id)
    })


def store_user(request):
    if request.method == 'POST' and request.POST['action'] == 'edit_user':
        client = Client.objects.get(pk=request.POST['user_id'])
        client.first_name = request.POST['first_name']
        client.last_name = request.POST['last_name']
        client.username = request.POST['username']
        client.email = request.POST['email']
        if request.POST['password'] != '':
            client.password = make_password(request.POST['password'])
        client.address = request.POST['address']
        client.phone = request.POST['phone']

        client.save()

        return redirect('user', user_id=request.POST['user_id'])


def edit_user(request, user_id):
    return render(request, 'shop/users/editprofile.html', {
        'user': Client.objects.get(pk=user_id)
    })


def products(request):
    add_to_cart(request)
    return render(request, 'shop/products/products.html', {
        'products': Product.objects.all()
    })


def product(request, product_id=0):
    add_to_cart(request)
    if product_id == 0:
        return request.POST['product_id'];

    picked_product = Product.objects.get(pk=product_id)
    return render(request, 'shop/products/single_product.html', {
        'product': picked_product,
    })


def categories(request):
    return render(request, 'shop/categories/categories.html')


def category(request, category_id):
    add_to_cart(request)
    return render(request, 'shop/categories/single_category.html', {
        'category': Category.objects.get(pk=category_id),
        'products': Product.objects.filter(PRDCategory=category_id)
    })


def user_login(request):
    if request.client.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        return authenticate_user(request, username=username, password=password)
    elif request.method == 'GET':
        return render(request, 'shop/auth/login.html')


def authenticate_user(request, username, password):
    client = authenticate(username=username, password=password)
    if client is not None:
        login(request, client)
        return redirect('index')
    else:
        return render(request, 'shop/auth/login.html', {
            'error': 'Invalid credentials'
        })


def user_logout(request):
    logout(request)
    return redirect('index')


def user_register(request):
    if request.method == 'POST':
        # if user is already authenticated, redirect to index
        if request.client.is_authenticated:
            return redirect('index')

        # if user is not authenticated, register the user
        client = Client.objects.create_user(
            username=request.POST['username'],
            password=make_password(request.POST['password']),
            email=request.POST['email'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name']
        )
        client.save()
        return render(request, 'shop/auth/login.html')
    elif request.method == 'GET':
        return render(request, 'shop/auth/signup.html')


def reset_password(request):
    if request.method == 'POST':
        if 'reset_token' in request.POST and 'password' in request.POST:
            if request.POST['password'] != request.POST['password_confirm']:
                return render(request, 'shop/auth/set_new_password.html', {
                    'error': 'Passwords do not match',
                    'reset_token': request.POST['reset_token']
                })
            client = get_client_by_token(request.POST['reset_token'])
            if client is not None:
                set_new_password(client, request.POST['password'])
                return render(request, 'shop/auth/set_new_password.html', {
                    'success': 'Your password has been reset successfully',
                    'done': True
                })
        return render(request, 'shop/auth/reset_password.html', {
            'success': 'A link has been sent to your email',
            'reset_token': get_reset_token(request)
        })
    elif request.method == 'GET':
        if 'reset_token' in request.GET:
            client = get_client_by_token(request.GET['reset_token'])
            if client is not None:
                return render(request, 'shop/auth/set_new_password.html', {
                    'reset_token': request.GET['reset_token']
                })
            return render(request, 'shop/auth/reset_password.html', {
                'error': 'Invalid reset token'
            })
        return render(request, 'shop/auth/reset_password.html')


def get_reset_token(request):
    # check if the user exists
    try:
        client = Client.objects.get(email=request.POST['email'])
    except Client.DoesNotExist:
        return render(request, 'shop/auth/reset_password.html', {
            'error': 'The email you entered does not exist'
        })
    # save the reset token
    client.reset_token = str(make_password(str(random.randint(100000, 999999))))
    client.save()
    return client.reset_token


def get_client_by_token(reset_token):
    try:
        client = Client.objects.get(reset_token=reset_token)
    except Client.DoesNotExist:
        return None
    return client


def set_new_password(client, password):
    client.password = make_password(password)
    client.reset_token = None
    client.save()


@login_required
def cart(request):
    cart_items = get_cart_items(request)
    return render(request, 'shop/cart/cart.html', {
        'cart_items': cart_items['items'],
        'total': cart_items['total']
    })


def get_cart_items(request):
    cart_items = CartItem.objects.filter(cart__client=request.client)
    total_price = 0
    # get related products
    for item in cart_items:
        item.product = Product.objects.get(pk=item.product.id)
        item.price = item.product.PRDPrice * item.quantity
        total_price += item.price
    return {
        'items': cart_items,
        'total': total_price
    }


@login_required
def add_to_cart(request):
    if request.method == 'POST' and request.POST['action'] == 'add_to_cart':
        product_id = request.POST['product_id']
        quantity = int(request.POST['quantity'])
        selected_product = Product.objects.get(pk=product_id)

        # check if the client has a cart
        try:
            client_cart = Cart.objects.get(client=request.client)
        except Cart.DoesNotExist:
            client_cart = Cart.objects.create(client=request.client)
            client_cart.save()

        # check if the product is already in the cart
        try:
            cart_item = CartItem.objects.get(product=selected_product)
        except CartItem.DoesNotExist:
            cart_item = None

        # if the product is already in the cart, increase the quantity
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # if the product is not in the cart, add it
            cart_item = CartItem.objects.create(
                product=selected_product,
                quantity=quantity,
                cart=client_cart
            )
            cart_item.save()
        return True


@login_required
def checkout(request):
    cart_items = get_cart_items(request)
    return render(request, 'shop/cart/checkout.html', {
        'cart_items': cart_items['items'],
        'total': cart_items['total']
    })


@login_required
def make_order(request):
    if request.method == 'POST':
        # get the cart items
        cart_items = get_cart_items(request)
        if cart_items is None:
            return render(request, 'shop/cart/checkout.html', {
                'error': 'Your cart is empty'
            })
        client = Client.objects.get(pk=request.client.id)
        if client is not None:
            client.address = request.POST['address']
            client.phone = request.POST['phone']
            client.save()
        # create the order
        order = Order.objects.create(
            client=request.client,
            tracking_number=random.randint(1000000000, 9999999999),
            status='pending',
            payment_method='Credit Card',
            status_description='Your order is pending',
            total=cart_items['total'],
            created_at=datetime.now()
        )
        order.save()
        # create the order items
        for item in cart_items['items']:
            order_item = OrderItem.objects.create(
                product=item.product,
                quantity=item.quantity,
                price=item.price * item.quantity,
                order=order
            )
            order_item.save()

        # clear the cart
        Cart.objects.get(client=request.client).delete()
        return render(request, 'shop/order/order_success.html', {
            'order': order
        })
    elif request.method == 'GET':
        return redirect('index')


def track_order(request):
    if request.method == 'POST' or (request.method == 'GET' and 'tracking_number' in request.GET):

        if 'tracking_number' in request.GET:
            tracking_number = request.GET['tracking_number']
        else:
            tracking_number = request.POST['tracking_number']

        try:
            order = Order.objects.get(tracking_number=tracking_number)
        except Order.DoesNotExist:
            return render(request, 'shop/order/track_order.html', {
                'error': 'Invalid tracking number'
            })
        return render(request, 'shop/order/track_order.html', {
            'order': order
        })
    elif request.method == 'GET':
        return render(request, 'shop/order/track_order.html')


@login_required
def client_orders(request):
    orders = Order.objects.filter(client=request.client)
    return render(request, 'shop/order/orders.html', {
        'orders': orders
    })


def search(request, q=None):
    if 'q' in request.GET:
        query = request.GET['q']
    else:
        query = q
    if query is None:
        return redirect('index')
    if request.method == 'POST':
        add_to_cart(request)
        return redirect('search', q=query)
    if request.method == 'GET':
        return render(request, 'shop/products/search_list.html', {
            'products': Product.objects.filter(PRDName__icontains=query)
        })
