from django.shortcuts import render, redirect


# Create your views here.
def view_bag(request):
    """A view that renders the bag contents age."""
    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """This view takes in the `item_id` of the item that the customer
    wishes to add to their bag, as well as the quantities therof.
    """

    # Get `quantity` input from the form and cast as int
    quantity = int(request.POST.get("quantity"))
    # Get `redirect_url` hidden input from the form
    redirect_url = request.POST.get("redirect_url")
    # Size to the `bag` session
    size = None
    if "product_size" in request.POST:
        size = request.POST["product_size"]
    # Check for a `bag` var in the session, else init as empty dict
    bag = request.session.get("bag", {})

    # Handling of items with a size
    if size:
        # If the item is already in the bag
        if item_id in list(bag.keys()):
            # If the item and id are already present
            if size in bag[item_id]["items_by_size"].keys():
                # Increment the quantity
                bag[item_id]["items_by_size"][size] += quantity
            else:
                # Set quantity if not present
                bag[item_id]["items_by_size"][size] = quantity

        else:
            # If the item is not already in the bag
            # Accounts for same item id with different sizes
            bag[item_id] = {"items_by_size": {size: quantity}}

    # If item does not have size, run original logic
    else:
        # Increment or create the `item_id` key in the `bag` dict
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    # Put the `bag` var into the session
    request.session["bag"] = bag
    print(request.session["bag"])

    return redirect(redirect_url)
