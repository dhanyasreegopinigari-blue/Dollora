from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Sum, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Cart,
    CartItem,
    Category,
    Coupon,
    Order,
    OrderItem,
    Product,
    ProductImage,
    Review,
    Wishlist,
)


def _safe_int_list(values):
    cleaned = []
    for value in values or []:
        try:
            cleaned.append(int(value))
        except (TypeError, ValueError):
            continue
    return cleaned


def _paginate(queryset, request, per_page=6, on_each_side=2, on_ends=1):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(
        page_obj.number,
        on_each_side=on_each_side,
        on_ends=on_ends,
    )
    return page_obj, page_range


def home(request):
    query = request.GET.get('q', '').strip()
    price = request.GET.get('price', '')
    stock = request.GET.get('stock', '')
    sort = request.GET.get('sort', '')

    products_list = Product.objects.all().select_related('category')

    if query:
        search_q = Q()
        for term in query.split():
            search_q |= (
                Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(category__name__icontains=term)
            )
        products_list = products_list.filter(search_q).distinct()

    if price == '1':
        products_list = products_list.filter(price__lte=500)
    elif price == '2':
        products_list = products_list.filter(price__gt=500, price__lte=1000)
    elif price == '3':
        products_list = products_list.filter(price__gt=1000)

    if stock == '1':
        products_list = products_list.filter(stock__gt=0)

    if sort == 'low':
        products_list = products_list.order_by('price')
    elif sort == 'high':
        products_list = products_list.order_by('-price')
    elif sort == 'new':
        products_list = products_list.order_by('-created_at')
    else:
        products_list = products_list.order_by('-created_at')

    products, page_range = _paginate(products_list, request, per_page=6)

    recent_ids = _safe_int_list(request.session.get('recently_viewed', []))
    recent_products = (
        Product.objects.filter(id__in=recent_ids).select_related('category')
        if recent_ids and not query
        else Product.objects.none()
    )

    return render(request, 'home.html', {
        'products': products,
        'page_range': page_range,
        'categories': Category.objects.all(),
        'query': query,
        'price': price,
        'stock': stock,
        'sort': sort,
        'recent_products': recent_products,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    recent = _safe_int_list(request.session.get('recently_viewed', []))
    if product.id in recent:
        recent.remove(product.id)
    recent.insert(0, product.id)
    request.session['recently_viewed'] = recent[:5]

    reviews = Review.objects.filter(product=product).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    images = ProductImage.objects.filter(product=product)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')

        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if rating and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=comment
            )

        return redirect(f'/product/{product.id}/')

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'images': images,
        'related_products': related_products,
    })


def category_products(request, id):
    category = get_object_or_404(Category, id=id)
    products_list = Product.objects.filter(category=category).order_by('-created_at')

    products, page_range = _paginate(products_list, request, per_page=6)

    return render(request, 'category.html', {
        'category': category,
        'products': products,
        'page_range': page_range,
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
    messages.success(request, "Product added to cart successfully!")
    return redirect('/cart/')


@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum((item.total_price for item in items), start=0)

    return render(request, 'cart.html', {
        'items': items,
        'total': total,
    })


@login_required
def increase_quantity(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()
    return redirect('/cart/')


@login_required
def decrease_quantity(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('/cart/')


@login_required
def remove_item(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    item.delete()
    return redirect('/cart/')


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum((item.total_price for item in items), start=0)

    coupon_code = request.POST.get('coupon', '').strip() if request.method == "POST" else ''
    discount = 0

    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
        if coupon:
            discount = (total * coupon.discount_percent) / 100

    final_total = total - discount

    if request.method == "POST":
        for item in items:
            if item.product.stock < item.quantity:
                return render(request, 'checkout.html', {
                    'items': items,
                    'total': total,
                    'discount': discount,
                    'final_total': final_total,
                    'error': f"Not enough stock for {item.product.name}",
                })

        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name', '').strip(),
            email=request.POST.get('email', '').strip(),
            address=request.POST.get('address', '').strip(),
            city=request.POST.get('city', '').strip(),
            state=request.POST.get('state', '').strip(),
            zip_code=request.POST.get('zip_code', '').strip(),
            total_amount=final_total,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        items.delete()
        return redirect('/order-success/')

    return render(request, 'checkout.html', {
        'items': items,
        'total': total,
        'discount': discount,
        'final_total': final_total,
    })


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': user_orders})


def order_success(request):
    return render(request, 'order_success.html')


@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('/wishlist/')


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'items': items})


@login_required
def remove_from_wishlist(request, id):
    item = get_object_or_404(Wishlist, id=id, user=request.user)
    item.delete()
    return redirect('/wishlist/')


@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'order_detail.html', {
        'order': order,
        'items': items,
    })


@login_required
def profile(request):
    order_count = Order.objects.filter(user=request.user).count()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    cart_count = CartItem.objects.filter(cart__user=request.user).count()

    return render(request, 'profile.html', {
        'order_count': order_count,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    })


@login_required
def dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    recent_orders = Order.objects.order_by('-created_at')[:5]
    top_products = (
        OrderItem.objects.values('product__name')
        .annotate(sold=Sum('quantity'))
        .order_by('-sold')[:5]
    )

    monthly_sales = (
        Order.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    low_stock_products = Product.objects.filter(stock__lte=5).order_by('stock', 'name')

    return render(request, 'dashboard.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'revenue': revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'monthly_sales': monthly_sales,
        'low_stock_products': low_stock_products,
    })


def compare_products(request):
    product1_id = request.GET.get('p1')
    product2_id = request.GET.get('p2')

    product1 = get_object_or_404(Product, id=product1_id) if product1_id else None
    product2 = get_object_or_404(Product, id=product2_id) if product2_id else None
    products = Product.objects.all().order_by('name')

    return render(request, 'compare.html', {
        'products': products,
        'product1': product1,
        'product2': product2,
    })




from django.http import HttpResponse
from pathlib import Path
from django.conf import settings

def media_test(request):
    p = Path(settings.MEDIA_ROOT) / "products"
    if p.exists():
        return HttpResponse("<br>".join([f.name for f in p.iterdir()][:20]))
    return HttpResponse("MEDIA FOLDER NOT FOUND")


from django.http import HttpResponse
from django.conf import settings
import os

def media_check(request):
    media_path = settings.MEDIA_ROOT

    if not os.path.exists(media_path):
        return HttpResponse(f"MEDIA_ROOT does not exist: {media_path}")

    files = []

    for root, dirs, filenames in os.walk(media_path):
        for f in filenames[:50]:
            files.append(os.path.join(root, f))

    return HttpResponse("<br>".join(files))