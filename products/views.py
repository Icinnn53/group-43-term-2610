from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from owner.models import Stall, Owner


# ================= PRODUCT LIST =================
def product_list(request):
    owner = Owner.objects.filter(user=request.user).first()

    if owner:
        products = Product.objects.select_related('stall').filter(stall__owner=owner)
    else:
        products = Product.objects.none()

    return render(request, 'products/product_list.html', {
        'products': products
    })


# ================= PRODUCT DETAIL =================
def product_detail(request, id):
    owner = Owner.objects.filter(user=request.user).first()

    product = get_object_or_404(
        Product,
        id=id,
        stall__owner=owner
    )

    return render(request, 'products/product_detail.html', {
        'product': product
    })


# ================= PRODUCTS BY STALL =================
def product_by_stall(request, stall_id):
    owner = Owner.objects.filter(user=request.user).first()

    stall = get_object_or_404(
        Stall,
        id=stall_id,
        owner=owner
    )

    products = Product.objects.filter(stall=stall)

    return render(request, 'products/product_by_stall.html', {
        'stall': stall,
        'products': products
    })


# ================= ADD PRODUCT =================
def product_create(request):
    owner = Owner.objects.filter(user=request.user).first()
    stalls = Stall.objects.filter(owner=owner)

    preselected_stall_id = request.GET.get('stall')

    if request.method == "POST":
        stall_id = request.POST.get('stall')

        if not stall_id:
            return render(request, 'products/product_create.html', {
                'stalls': stalls,
                'error': 'Please select a stall.',
                'preselected_stall_id': preselected_stall_id
            })

        stall = get_object_or_404(
            Stall,
            id=stall_id,
            owner=owner
        )

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
def edit_product(request, id):
    owner = Owner.objects.filter(user=request.user).first()

    product = get_object_or_404(
        Product,
        id=id,
        stall__owner=owner
    )

    stalls = Stall.objects.filter(owner=owner)

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description') or ""
        product.stall_id = request.POST.get('stall')
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
def delete_product(request, id):
    owner = Owner.objects.filter(user=request.user).first()

    product = get_object_or_404(
        Product,
        id=id,
        stall__owner=owner
    )

    stall_id = product.stall.id

    if request.method == "POST":
        product.delete()
        return redirect('product_by_stall', stall_id=stall_id)

    return redirect('product_by_stall', stall_id=stall_id)