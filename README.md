# MiniShop — Django E-commerce Project

MiniShop is a simple online shop built **only with Python + Django**:
Django Templates (HTML), CSS + Bootstrap 5, PostgreSQL, the Django ORM, and a custom dark admin panel.
It uses no Node.js, React, Vue or any other JavaScript framework. The only JavaScript is Bootstrap's own bundle (slider, tabs, dropdowns) and a few lines of plain JavaScript.

---

## 1. Folder structure

```
MiniShop/
├── manage.py                      # Django command-line tool
├── requirements.txt               # Python packages
├── minishop/                      # PROJECT settings
│   ├── settings.py                # apps, database, static/media config
│   └── urls.py                    # main URL file -> includes products/urls.py
├── products/                      # our APP (all shop logic)
│   ├── models.py                  # Category, Product, Order, OrderItem  (M)
│   ├── views.py                   # customer website views              (V)
│   ├── admin_views.py             # custom dark admin panel views        (V)
│   ├── forms.py                   # ProductForm, CategoryForm, CheckoutForm
│   ├── urls.py                    # every URL of the site
│   ├── admin.py                   # (empty - we use our own admin panel)
│   ├── context_processors.py      # cart count + categories for every page
│   ├── migrations/                # database migration files
│   └── management/commands/
│       ├── create_schema.py       # creates the PostgreSQL schema (once)
│       └── seed_data.py           # loads 38 sample products
├── templates/                                                         (T)
│   ├── _messages.html             # flash messages (used by both website and admin)
│   ├── customer/
│   │   ├── base.html              # navbar + footer (every page extends it)
│   │   ├── home.html              # hero slider, categories, featured, offer, best selling
│   │   ├── product_detail.html    # gallery, info, tabs, related products
│   │   ├── product_list.html      # all products / category / search results / wishlist
│   │   ├── categories.html, cart.html, checkout.html, order_success.html
│   │   └── _product_card.html, _stars.html, _tag.html, _features.html   # reusable pieces
│   └── admin_panel/
│       ├── base.html              # dark sidebar + top navbar
│       ├── login.html, dashboard.html, products.html, add_product.html
│       ├── categories.html, orders.html, order_detail.html, customers.html
│       └── _head.html, _product_row.html, _field.html, _search_box.html   # reusable pieces
├── static/
│   ├── css/style.css              # customer website design
│   ├── css/admin.css              # dark admin design
│   ├── img/                       # banner images
│   └── vendor/                    # Bootstrap 5 + Bootstrap Icons (offline copy)
├── media/                         # uploaded product images
└── sample_data/                   # sample products (JSON + images) for seed_data
```

---

## 2. Installation and running

You need Python 3.10 or newer.

```bash
# 1. Go into the project folder
cd MiniShop

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS

# 3. Install packages
pip install -r requirements.txt

# 4. Database: copy .env.example to .env and fill in your PostgreSQL details
copy .env.example .env           # Windows  (cp .env.example .env on Linux / macOS)
python manage.py create_schema   # only the first time
python manage.py makemigrations  # creates migration files from models.py
python manage.py migrate         # creates the tables in PostgreSQL

# 5. Admin user + sample products
python manage.py createsuperuser
python manage.py seed_data

# 6. Run the server
python manage.py runserver
```

Open these URLs in the browser:

| URL | Page |
|-----|------|
| http://127.0.0.1:8000/ | Customer website |
| http://127.0.0.1:8000/admin-panel/ | Admin panel (`/admin/` also opens it) |

A demo admin account already exists in the database: **admin / admin123**.

---

## 3. Database configuration

The connection details live in a `.env` file next to `manage.py` (it is in `.gitignore`, so the password never goes to GitHub). Copy `.env.example` to `.env` and fill it in:

```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=your-host
DB_PORT=5432
```

`minishop/settings.py` reads these values:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {'options': '-c search_path=minishop'},
    }
}
```
The `search_path=minishop` option keeps MiniShop's tables in their own PostgreSQL *schema*, which works like a folder inside the database. The database already had tables from an older project, so this keeps the two apart.

---

## 4. Features

**Customer website**
- Home page: hero slider, 8 category cards, featured products, a "40% off" offer banner, best-selling products, and a footer
- All Products page with a category filter, plus a Categories page
- Search by product name, showing "No product found" when nothing matches
- Product details: image gallery with thumbnails, category badge, rating, price and discount, specs (processor, RAM, storage, display, battery), stock status, quantity selector, Add to Cart, Wishlist, Share, the Description / Specifications / Reviews tabs, and related products
- Session cart, then checkout (cash on delivery), which creates an Order

**Admin panel (dark theme)**
- Login and logout (only staff users can enter)
- Dashboard: Total Products / Categories / Orders / Customers cards, a recent products table with Edit and Delete, and recent orders
- Products: search, category filter, Add Product, Edit, Delete
- Add/Edit Product form with image upload and live preview
- Categories: add, edit, delete, and the product count for each category
- Orders: list, filter by status, view details, update status
- Customers: people who ordered, grouped by email, with order count and total spent

---

## 5. Viva explanation

### What is MiniShop?
MiniShop is a small e-commerce web application. **Customers** can browse products, search, view details, add items to a cart, and place an order. The **admin** logs in to a dark dashboard to add, edit and delete products and categories, and to manage orders.

### Why Django?
- It is written in **Python**, which is easy to read and learn.
- It comes "batteries included": ORM, admin panel, authentication, forms, sessions, security (CSRF, SQL-injection protection, password hashing) are all built in.
- It has a clear structure (MVT), so every file has one job.
- Real companies use it (Instagram, Pinterest, Mozilla), and it works with PostgreSQL out of the box.

### Django MVT architecture
MVT = **Model – View – Template**.

```
Browser ──request──▶ urls.py ──▶ View ──▶ Model (ORM) ──▶ PostgreSQL
                                   │
                                   ▼
Browser ◀──HTML response── Template (HTML + data)
```

1. The user opens a URL, for example `/product/5/`.
2. **urls.py** finds the matching view (`product_detail`).
3. The **View** asks the **Model** for data: `Product.objects.get(pk=5)`.
4. The Model (ORM) turns that into SQL and gets the row from **PostgreSQL**.
5. The View sends the data to a **Template** (`product_detail.html`).
6. The Template fills in the HTML, and Django sends the page back to the browser.

### Role of the Model (`products/models.py`)
A model is a Python class that describes a **database table**. Each attribute is a **column**.
- `Category`: name, image
- `Product`: name, image, description, price, category (ForeignKey → Category), stock_quantity, created_date, plus optional old_price, rating, gallery images and specs
- `Order` and `OrderItem`: an order placed by a customer, and the products inside it

Models also hold small helpers, for example `discount_percent` and `stars()`.

### Role of the View (`views.py`, `admin_views.py`)
A view is a Python function that receives a **request** and returns a **response**. It contains the logic: read data with the ORM, handle forms, check permissions, and choose a template. Example:

```python
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:6]
    return render(request, 'customer/product_detail.html',
                  {'product': product, 'related_products': related_products})
```

### Role of the Template (`templates/`)
A template is an HTML file with Django Template Language tags:
- `{{ product.name }}` prints a value
- `{% for product in products %} ... {% endfor %}` is a loop
- `{% if product.in_stock %} ... {% endif %}` is a condition
- `{% extends 'customer/base.html' %}` and `{% block content %}` mean every page reuses the same navbar and footer (template inheritance)
- `{% include '_product_card.html' %}` reuses a product card everywhere
- `{% url 'product_detail' product.id %}` builds links from URL names

### URL routing
`minishop/urls.py` is the main URL file. It sends everything to `products/urls.py`:

```python
path('', include('products.urls')),
path('admin/', RedirectView.as_view(pattern_name='dashboard')),  # /admin/ opens our panel
```

`products/urls.py` connects each URL to a view:

```python
path('', views.home, name='home'),
path('product/<int:pk>/', views.product_detail, name='product_detail'),
path('search/', views.search, name='search'),
path('admin-panel/products/add/', admin_views.product_form, name='admin_product_add'),
```

`<int:pk>` captures a number from the URL and passes it to the view. The `name` lets templates build links with `{% url %}`.

### Django Admin
MiniShop has **one** admin panel: a custom dark dashboard at `/admin-panel/` (typing `/admin/` also opens it).
Django's default admin was not used, because the project asked for our own dark design. So we built the panel ourselves with views (`admin_views.py`), templates (`templates/admin_panel/`) and CSS (`admin.css`).
It uses Django's built-in **authentication system** (`django.contrib.auth`): users, password hashing, `login()`, `logout()`. Every admin view is protected with a decorator:

```python
admin_required = user_passes_test(is_admin, login_url='admin_login')

@admin_required
def dashboard(request): ...
```

A non-admin user is sent to the login page. Users are created with `python manage.py createsuperuser`. Passwords are stored hashed, never as plain text.

### PostgreSQL connection
- The Python package **psycopg** is the driver that lets Django talk to PostgreSQL.
- `settings.py` → `DATABASES` holds the engine, host, port, user, password and database name.
- `makemigrations` reads `models.py` and writes migration files (instructions like "create table products_product").
- `migrate` runs those instructions on PostgreSQL and creates the real tables.

### Django ORM
ORM = Object-Relational Mapper. We write **Python**, and Django writes the **SQL** for us.

| Django ORM | SQL |
|---|---|
| `Product.objects.all()` | `SELECT * FROM products_product` |
| `Product.objects.get(pk=5)` | `SELECT * ... WHERE id = 5` |
| `Product.objects.filter(name__icontains='laptop')` | `... WHERE name ILIKE '%laptop%'` |
| `Product.objects.filter(category=cat)` | `... WHERE category_id = 2` |
| `Product.objects.count()` | `SELECT COUNT(*) ...` |
| `Category.objects.annotate(product_count=Count('products'))` | `COUNT` + `GROUP BY` |
| `product.save()` | `INSERT` or `UPDATE` |
| `product.delete()` | `DELETE` |

Benefits: code is short and readable, it is safe from SQL injection, and it works with any database.

### CRUD operation flow (Products)
All CRUD is in `admin_views.py` and uses `ProductForm` (a **ModelForm** that builds its fields from the Product model).
Create and Update share **one view**, `product_form(request, pk=None)`, so the code is not written twice. With no `pk` the form is empty and `save()` does an INSERT. With a `pk` the form is filled with that product and `save()` does an UPDATE.

| Operation | URL | What happens |
|---|---|---|
| **Create** | `/admin-panel/products/add/` | GET shows an empty form. POST runs `ProductForm(request.POST, request.FILES)`, then `form.is_valid()`, then `form.save()` (INSERT). The image is saved in `media/products/`. |
| **Read** | `/admin-panel/products/` | `Product.objects.all()` (with optional search/filter) is shown in a table. The customer website also reads products. |
| **Update** | `/admin-panel/products/5/edit/` | `ProductForm(instance=product)` fills the form. On POST, `form.save()` runs an UPDATE. |
| **Delete** | `/admin-panel/products/5/delete/` (POST only) | A JavaScript `confirm()` asks first, then `product.delete()` runs a DELETE. |

Image upload needs three things: `ImageField` in the model, `enctype="multipart/form-data"` on the form, and `request.FILES` in the view. The **Pillow** library checks that the file really is an image. `MEDIA_ROOT` and `MEDIA_URL` in settings say where the files are stored and served.

After each action, `messages.success(...)` shows a green message, and `redirect(...)` sends the admin back to the list.

### Search implementation
1. The navbar has a form: `<form action="{% url 'search' %}" method="get"><input name="q">`.
2. Submitting it opens `/search/?q=laptop`.
3. The `search` view reads the word and filters with the ORM:

```python
def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'customer/product_list.html', {'products': products, 'query': query})
```

`icontains` means "contains, ignoring upper/lower case".

4. The template shows the product cards, or **"No product found"** when the list is empty:

```django
{% if products %} ...cards... {% else %} <h4>No product found</h4> {% endif %}
```

### Extra points you can mention
- **Cart**: stored in the **session** (`request.session['cart'] = {'5': 2}`), so no login is needed.
- **Checkout**: creates an `Order` plus its `OrderItem` rows and reduces `stock_quantity`.
- **Context processor**: `context_processors.py` puts the cart count and categories into every template automatically.
- **Security**: `{% csrf_token %}` is in every POST form, delete works only through POST, and admin pages need a staff login.
