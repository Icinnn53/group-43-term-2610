from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from owner.models import Stall


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


# ================= ADD PRODUCT (STAY IN STALL CONTEXT) =================
def product_create(request):
    stalls = Stall.objects.all()

    # 🔥 auto-select stall from URL (?stall=1)
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

        Product.objects.create(
            stall=stall,
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            description=request.POST.get('description') or ""
        )

        # 🔥 IMPORTANT: go back to same stall page (not global list)
        return redirect('product_by_stall', stall_id=stall.id)

    return render(request, 'products/product_create.html', {
        'stalls': stalls,
        'preselected_stall_id': preselected_stall_id
    })


# ================= EDIT PRODUCT =================
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    stalls = Stall.objects.all()

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description') or ""
        product.stall_id = request.POST.get('stall')

        product.save()

        # 🔥 FIX: go back to stall view, not product detail
        return redirect('product_by_stall', stall_id=product.stall.id)

    return render(request, 'products/edit_product.html', {
        'product': product,
        'stalls': stalls
    })


# ================= DELETE PRODUCT =================
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    stall_id = product.stall.id

    if request.method == "POST":
        product.delete()
        # 🔥 FIX: return to stall product page
        return redirect('product_by_stall', stall_id=stall_id)

    return redirect('product_by_stall', stall_id=stall_id)