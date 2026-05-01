# Bangazon Platform API

A full-featured e-commerce REST API for a book marketplace. Customers can browse books, manage a shopping cart, place orders, rate products, and favorite sellers. Sellers can create a store, list inventory, and track sales.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.14-a30000?style=flat)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-dependency%20manager-60A5FA?style=flat&logo=poetry&logoColor=white)

**Client Repo:** [Bangazon-client-hrmjnv](https://github.com/NSS-Day-Cohort-79/Bangazon-client-hrmjnv)

---

## Setup

### System Dependencies

**macOS**
```sh
brew install libtiff libjpeg webp little-cms2
```

**Linux**
```sh
sudo apt install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev
```

### Project Setup

1. Install [pipx](https://pipx.pypa.io/stable/installation/) then run `pipx install poetry`.
2. Clone this repository and open the directory in your terminal.
3. Run `poetry env activate` to create the virtual environment.
4. Run `poetry install` to install dependencies.
5. Run `pip install setuptools`.
6. Run `./seed_data.sh` to create the database and load starter data.
7. Open in VS Code and ensure the correct Python interpreter is selected.
8. Start the debugger (or run `python manage.py runserver`).

### Test Credentials

User accounts are in `bangazonapi/fixtures/users.json`. The password for every seed user is:

```
Admin8*
```

### Resetting the Database

Run `./seed_data.sh` at any time to drop the database and reload all fixture data from scratch.

---

## API Request Collection

1. Open [Yaak](https://yaak.app/) and click **Import → Select File**.
2. Choose `api-requests-collection.json` from the project root.
3. Click **Import** — a new workspace will be created.

To verify setup, expand the **Profile** collection, open **Login**, and send the request. You should receive:

```json
{
  "valid": true,
  "token": "9ba45f09651c5b0c404f37a2d2572c026c146690",
  "id": 5
}
```

---

## API Endpoints

All endpoints require a token in the `Authorization` header (`Token <token>`) unless noted as public.

### Authentication

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/register` | Create a new user account |
| `POST` | `/login` | Authenticate and receive a token |

### Products

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/products` | List all products. Filterable by `category`, `quantity`, `order_by`, `direction`, `number_sold`, `location`, `min_price` |
| `GET` | `/products/{id}` | Get a single product |
| `POST` | `/products` | Create a product (seller only) |
| `PUT` | `/products/{id}` | Update a product (seller only) |
| `DELETE` | `/products/{id}` | Delete a product (seller only) |
| `POST` | `/products/{id}/rate` | Submit a rating (score 0–5) and review |
| `POST` | `/products/{id}/like` | Like a product |
| `DELETE` | `/products/{id}/like` | Unlike a product |
| `POST` | `/products/{id}/recommend` | Recommend a product to another user |

### Product Categories

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/productcategories` | List all categories |
| `GET` | `/productcategories/{id}` | Get a single category |
| `POST` | `/productcategories` | Create a category |

### Stores

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/stores` | List all stores. Use `?mine` to return the authenticated user's store |
| `GET` | `/stores/{id}` | Get a single store with its products |
| `POST` | `/stores` | Create a store |
| `PUT` | `/stores/{id}` | Update a store (owner only) |
| `DELETE` | `/stores/{id}` | Delete a store (owner only) |

### Shopping Cart

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/cart` | Get the current cart (unpaid open order) |
| `POST` | `/cart` | Add a product to the cart |
| `DELETE` | `/cart/{product_id}` | Remove a product from the cart |

### Orders

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/orders` | List the authenticated user's completed orders |
| `GET` | `/orders/{id}` | Get a single order |
| `PUT` | `/orders/{id}` | Complete an order by attaching a payment type |

### Line Items

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/lineitems/{id}` | Get a single line item |
| `DELETE` | `/lineitems/{id}` | Remove a line item from the cart |

### Payment Types

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/paymenttypes` | List the authenticated user's saved payment methods |
| `GET` | `/paymenttypes/{id}` | Get a single payment method |
| `POST` | `/paymenttypes` | Add a new payment method |
| `DELETE` | `/paymenttypes/{id}` | Remove a payment method |

### Profile

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/profile` | Get the authenticated user's profile, recommendations, and liked products |
| `GET` | `/profile/cart` | Get cart contents via profile |
| `POST` | `/profile/cart` | Add a product to the cart via profile |
| `DELETE` | `/profile/cart` | Clear the entire cart |
| `GET` | `/profile/favoritesellers` | List the user's favorited sellers |

### Users & Customers

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/users` | List all users |
| `GET` | `/users/{id}` | Get a single user |
| `PUT` | `/customers/{id}` | Update a customer profile (own profile only) |

### Reports

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/reports/orders` | HTML report of all completed orders with totals |
| `GET` | `/reports/expensiveproducts` | HTML report of products priced $1,000 or more |
| `GET` | `/reports/inexpensiveproducts` | HTML report of products priced under $1,000 |

---

## Contributors

- [Cory Drumright](https://github.com/cmdrumright)
- Ashley Bell
- Dakota Seagraves
- Jack Gardner
- [Steve Brownlee](https://github.com/stevebrownlee)
