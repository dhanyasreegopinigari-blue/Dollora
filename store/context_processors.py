from .models import Cart, CartItem, Category


def categories(request):
    return {'categories': Category.objects.all()}


def sidebar_menu(request):
    def first_category(name):
        return Category.objects.filter(name__iexact=name).first()

    return {
        'sidebar_menu': [
            {
                'title': 'Browse All',
                'links': [
                    {'label': 'All Products', 'category': None},
                ],
            },
            {
                'title': 'Electronics',
                'links': [
                    {'label': 'Electronics', 'category': first_category('Electronics')},
                    {'label': 'Mobiles', 'category': first_category('Mobiles')},
                    {'label': 'Laptops', 'category': first_category('Laptops')},
                    {'label': 'Headphones', 'category': first_category('Headphones')},
                ],
            },
            {
                'title': 'Fashion',
                'links': [
                    {'label': 'Fashion', 'category': first_category('Fashion')},
                    {'label': 'Men Wear', 'category': first_category('Men Wear')},
                    {'label': 'Women Wear', 'category': first_category('Women Wear')},
                    {'label': 'Kids & Toys', 'category': first_category('Kids and toys')},
                ],
            },
            {
                'title': 'Home & Kitchen',
                'links': [
                    {'label': 'Home & Kitchen', 'category': first_category('Home & Kitchen')},
                    {'label': 'Kitchen Appliances', 'category': first_category('Kitchen Appliances')},
                    {'label': 'Home Decor', 'category': first_category('Home Decor')},
                ],
            },
            {
                'title': 'Books & Lifestyle',
                'links': [
                    {'label': 'Books', 'category': first_category('Books')},
                    {'label': 'Beauty', 'category': first_category('Beauty')},
                    {'label': 'Sports', 'category': first_category('Sports')},
                ],
            },
        ]
    }


def cart_count(request):
    count = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = CartItem.objects.filter(cart=cart).count()

    return {'cart_count': count}
