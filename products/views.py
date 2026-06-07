from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from owner.models import Stall


def is_organizer(user):
    return getattr(user, "role", None) == "organizer"


def is_stall_owner(user, stall):
    return stall.owner and stall.owner.user == user


# ================= PRODUCT LIST =================
def product_list(request):
    products = Product.objects.select_related('stall').all()

    return render(request, 'products/product_list.html', {
        'products': products
    })


# ================= PRODUCT DETAIL =================
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    return render(request, 'products/product_detail.html', {
        'product': product
    })


# ================= PRODUCTS BY STALL =================
def product_by_stall(request, stall_id):
    stall = get_object_or_404(Stall, id=stall_id)
    products = Product.objects.filter(stall=stall)

    return render(request, 'products/product_by_stall.html', {
        'stall': stall,
        'products': products
    })


# ================= ADD PRODUCT =================
@login_required
def product_create(request):
    if is_organizer(request.user):
        stalls = Stall.objects.all()
    else:
        stalls = Stall.objects.filter(owner__user=request.user)

    preselected_stall_id = request.GET.get('stall')

    if request.method == "POST":
        stall_id = request.POST.get('stall')

        if not stall_id:
            return render(request, 'products/product_create.html', {
                'stalls': stalls,
                'error': 'Please select a stall.',
                'preselected_stall_id': preselected_stall_id
            })

        stall = get_object_or_404(Stall, id=stall_id)

        if not is_organizer(request.user) and not is_stall_owner(request.user, stall):
            return redirect('product_list')

        Product.objects.create(
            stall=stall,
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            description=request.POST.get('description') or "",
            product_image=request.FILES.get('product_image'),
            stock_quantity=int(request.POST.get('stock_quantity') or 0)
        )

        return redirect('product_by_stall', stall_id=stall.id)

    return render(request, 'products/product_create.html', {
        'stalls': stalls,
        'preselected_stall_id': preselected_stall_id
    })


# ================= EDIT PRODUCT =================
@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if not is_organizer(request.user) and not is_stall_owner(request.user, product.stall):
        return redirect('product_by_stall', stall_id=product.stall.id)

    if is_organizer(request.user):
        stalls = Stall.objects.all()
    else:
        stalls = Stall.objects.filter(owner__user=request.user)

    if request.method == "POST":
        stall_id = request.POST.get('stall')
        new_stall = get_object_or_404(Stall, id=stall_id)

        if not is_organizer(request.user) and not is_stall_owner(request.user, new_stall):
            return redirect('product_by_stall', stall_id=product.stall.id)

        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description') or ""
        product.stall = new_stall
        product.stock_quantity = int(request.POST.get('stock_quantity') or 0)

        if request.FILES.get('product_image'):
            product.product_image = request.FILES.get('product_image')

        product.save()

        return redirect('product_by_stall', stall_id=product.stall.id)

    return render(request, 'products/edit_product.html', {
        'product': product,
        'stalls': stalls
    })


# ================= DELETE PRODUCT =================
@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    stall_id = product.stall.id

    if not is_organizer(request.user) and not is_stall_owner(request.user, product.stall):
        return redirect('product_by_stall', stall_id=stall_id)

    if request.method == "POST":
        product.delete()
        return redirect('product_by_stall', stall_id=stall_id)

    return redirect('product_by_stall', stall_id=stall_id)