# # Messaging framework for toasts
# from django.contrib import messages
# from django.shortcuts import HttpResponse, redirect, render
# from django.urls import reverse

# # Show which item was added to bag from the model
# from products.models import Product


# # Create your views here.
# def view_bag(request):
#     """A view that renders the bag contents age."""
#     return render(request, "bag/bag.html")


# def add_to_bag(request, item_id):
#     """This view takes in the `item_id` of the item that the customer
#     wishes to add to their bag, as well as the quantities therof.
#     """

#     # Get product for use in toast
#     product = Product.objects.get(pk=item_id)

#     # Get `quantity` input from the form and cast as int
#     quantity = int(request.POST.get("quantity"))
#     # Get `redirect_url` hidden input from the form
#     redirect_url = request.POST.get("redirect_url")
#     # Size to the `bag` session
#     size = None
#     if "product_size" in request.POST:
#         size = request.POST["product_size"]
#     # Check for a `bag` var in the session, else init as empty dict
#     bag = request.session.get("bag", {})

#     # Handling of items with a size
#     if size:
#         # If the item is already in the bag
#         if item_id in list(bag.keys()):
#             # If the item and id are already present
#             if size in bag[item_id]["items_by_size"].keys():
#                 messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')

#                 # Increment the quantity
#                 bag[item_id]["items_by_size"][size] += quantity
#             else:
#                 # Set quantity if not present
#                 bag[item_id]["items_by_size"][size] = quantity

#         else:
#             # If the item is not already in the bag
#             # Accounts for same item id with different sizes
#             bag[item_id] = {"items_by_size": {size: quantity}}

#     # If item does not have size, run original logic
#     else:
#         # Increment or create the `item_id` key in the `bag` dict
#         if item_id in list(bag.keys()):
#             bag[item_id] += quantity
#         else:
#             bag[item_id] = quantity

#         # Add success message to the request object (TOAST)
#         messages.success(request, f"Added {product.name} to your bag")

#     # Put the `bag` var into the session
#     request.session["bag"] = bag
#     print(request.session["bag"])

#     return redirect(redirect_url)


# def adjust_bag(request, item_id):
#     """This view handles the updating of product quantities."""

#     quantity = int(request.POST.get("quantity"))
#     size = None
#     if "product_size" in request.POST:
#         size = request.POST["product_size"]
#     bag = request.session.get("bag", {})

#     if size:
#         if quantity > 0:
#             bag[item_id]["items_by_size"][size] = quantity

#             # If items by size dict is empty
#             if not bag[item_id]["items_by_size"]:
#                 # Remove empty dict
#                 bag.pop(item_id)
#         else:
#             del bag[item_id]["items_by_size"][size]

#     else:
#         if quantity > 0:
#             bag[item_id] = quantity
#         else:
#             bag.pop[item_id]

#     request.session["bag"] = bag
#     print(request.session["bag"])

#     return redirect(reverse("view_bag"))


# def remove_from_bag(request, item_id):
#     """This view handles the removal of products from the bag entirely."""

#     try:
#         size = None
#         if "product_size" in request.POST:
#             size = request.POST["product_size"]
#         bag = request.session.get("bag", {})

#         if size:
#             del bag[item_id]["items_by_size"][size]

#             # If items by size dict is empty
#             if not bag[item_id]["items_by_size"]:
#                 # Remove empty dict
#                 bag.pop(item_id)

#         else:
#             bag.pop(item_id)

#         request.session["bag"] = bag
#         print(request.session["bag"])

#         # View is posted to a JS function so return OK response
#         return HttpResponse(status=200)

#     except Exception as e:
#         return HttpResponse(status=500)

from django.shortcuts import (
    render,
    redirect,
    reverse,
    HttpResponse,
    get_object_or_404,
)
from django.contrib import messages

from products.models import Product

# Create your views here.


def view_bag(request):
    """A view that renders the bag contents page"""

    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """Add a quantity of the specified product to the shopping bag"""

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get("quantity"))
    redirect_url = request.POST.get("redirect_url")
    size = None
    if "product_size" in request.POST:
        size = request.POST["product_size"]
    bag = request.session.get("bag", {})

    if size:
        if item_id in list(bag.keys()):
            if size in bag[item_id]["items_by_size"].keys():
                bag[item_id]["items_by_size"][size] += quantity
                messages.success(
                    request,
                    f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}',
                )
            else:
                bag[item_id]["items_by_size"][size] = quantity
                messages.success(
                    request,
                    f"Added size {size.upper()} {product.name} to your bag",
                )
        else:
            bag[item_id] = {"items_by_size": {size: quantity}}
            messages.success(
                request,
                f"Added size {size.upper()} {product.name} to your bag",
            )
    else:
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            messages.success(
                request, f"Updated {product.name} quantity to {bag[item_id]}"
            )
        else:
            bag[item_id] = quantity
            messages.success(request, f"Added {product.name} to your bag")

    request.session["bag"] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get("quantity"))
    size = None
    if "product_size" in request.POST:
        size = request.POST["product_size"]
    bag = request.session.get("bag", {})

    if size:
        if quantity > 0:
            bag[item_id]["items_by_size"][size] = quantity
            messages.success(
                request,
                f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}',
            )
        else:
            del bag[item_id]["items_by_size"][size]
            if not bag[item_id]["items_by_size"]:
                bag.pop(item_id)
            messages.success(
                request,
                f"Removed size {size.upper()} {product.name} from your bag",
            )
    else:
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(
                request, f"Updated {product.name} quantity to {bag[item_id]}"
            )
        else:
            bag.pop(item_id)
            messages.success(request, f"Removed {product.name} from your bag")

    request.session["bag"] = bag
    return redirect(reverse("view_bag"))


def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""

    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if "product_size" in request.POST:
            size = request.POST["product_size"]
        bag = request.session.get("bag", {})

        if size:
            del bag[item_id]["items_by_size"][size]
            if not bag[item_id]["items_by_size"]:
                bag.pop(item_id)
            messages.success(
                request,
                f"Removed size {size.upper()} {product.name} from your bag",
            )
        else:
            bag.pop(item_id)
            messages.success(request, f"Removed {product.name} from your bag")

        request.session["bag"] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f"Error removing item: {e}")
        return HttpResponse(status=500)
