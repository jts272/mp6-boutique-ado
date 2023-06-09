from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Product, Category


# Create your views here.
def all_products(request):
    """A view to show all products, including sorting and search queries."""

    products = Product.objects.all()
    # Give no search term value to context by default (i.e. empty search)
    query = None
    # Give `None` value to category for context dict if not used
    categories = None

    # Access URL parameters from form get
    if request.GET:
        print(request.GET)
        # Reference `name` of text input `q`
        if "q" in request.GET:
            # Create var for search query
            query = request.GET["q"]
            # Handle empty queries
            if not query:
                # Invoke Django messages system
                messages.error(request, "You didn't enter any search criteria")
                return redirect(reverse("products"))

            # Use Q object for complex lookup
            # https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects

            # Get `Products` item whose query matches name or description
            # Use OR statement and specify case insensitivity
            queries = Q(name__icontains=query) | Q(
                description__icontains=query
            )
            # Perform the actual filtering with the Q objects
            products = products.filter(queries)

        # If `category` is in the URL from the GET request from nav links
        if "category" in request.GET:
            """`category` has been created as key for the QueryDict
            object when `?category=<categories>` was given as the href
            in `main_nav.html`.

            https://developer.mozilla.org/en-US/docs/Web/API/URL/search
            """
            # Get the csv list of categories from the href and split commas
            # dict lookup with square brackets, not a method call
            categories = request.GET["category"].split(",")
            # Use these categories to filter the products for the context
            # https://docs.djangoproject.com/en/3.2/topics/db/queries/#lookups-that-span-relationships
            # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#in
            products = products.filter(category__name__in=categories)
            # Also get the selected categories to show in the template
            categories = Category.objects.filter(name__in=categories)

    # The `query` must be provided to the context
    context = {
        "products": products,
        "search_term": query,
        "current_categories": categories,
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """A view to show individual product details."""

    product = get_object_or_404(Product, pk=product_id)

    context = {"product": product}

    return render(request, "products/product_detail.html", context)
