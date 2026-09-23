import pytest

from products.models import Product

PRODUCTS_URL = '/api/v1/products/'


def product_payload(**overrides):
    payload = {
        'name': 'Test Product',
        'description': 'A test product',
        'price': '9.99',
        'stock_quantity': 10,
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_create_product_requires_auth(api_client):
    resp = api_client.post(PRODUCTS_URL, product_payload())
    assert resp.status_code == 401


@pytest.mark.django_db
def test_create_product(auth_client):
    resp = auth_client.post(PRODUCTS_URL, product_payload())
    assert resp.status_code == 201
    assert resp.data['status'] == 'ACTIVE'
    assert resp.data['stock_quantity'] == 10


@pytest.mark.django_db
def test_create_product_invalid_price(auth_client):
    resp = auth_client.post(PRODUCTS_URL, product_payload(price='0'))
    assert resp.status_code == 400


@pytest.mark.django_db
def test_list_active_products_only(auth_client, user):
    active = Product.objects.create(name='Active One', price='5.00', stock_quantity=1, status=Product.Status.ACTIVE, owner=user)
    Product.objects.create(name='Inactive One', price='5.00', stock_quantity=1, status=Product.Status.INACTIVE, owner=user)
    resp = auth_client.get(PRODUCTS_URL)
    assert resp.status_code == 200
    names = [p['name'] for p in resp.data['results']]
    assert 'Active One' in names
    assert 'Inactive One' not in names


@pytest.mark.django_db
def test_retrieve_product(auth_client, user):
    p = Product.objects.create(name='Retrieve Me', price='5.00', stock_quantity=1, owner=user)
    resp = auth_client.get(f'{PRODUCTS_URL}{p.id}/')
    assert resp.status_code == 200
    assert resp.data['name'] == 'Retrieve Me'


@pytest.mark.django_db
def test_update_product(auth_client, user):
    p = Product.objects.create(name='Old Name', price='5.00', stock_quantity=1, owner=user)
    resp = auth_client.put(f'{PRODUCTS_URL}{p.id}/', {
        'name': 'New Name',
        'description': 'Updated desc',
        'price': '12.50',
    })
    assert resp.status_code == 200
    assert resp.data['name'] == 'New Name'
    assert resp.data['price'] == '12.50'


@pytest.mark.django_db
def test_stock_increase(auth_client, user):
    p = Product.objects.create(name='Stock Item', price='5.00', stock_quantity=5, owner=user)
    resp = auth_client.patch(f'{PRODUCTS_URL}{p.id}/stock/', {'delta': 5}, format='json')
    assert resp.status_code == 200
    assert resp.data['stock_quantity'] == 10


@pytest.mark.django_db
def test_stock_decrease_rejects_negative(auth_client, user):
    p = Product.objects.create(name='Stock Item 2', price='5.00', stock_quantity=3, owner=user)
    resp = auth_client.patch(f'{PRODUCTS_URL}{p.id}/stock/', {'delta': -10}, format='json')
    assert resp.status_code == 400
    p.refresh_from_db()
    assert p.stock_quantity == 3


@pytest.mark.django_db
def test_deactivate_and_activate_product(auth_client, user):
    p = Product.objects.create(name='Toggle Item', price='5.00', stock_quantity=3, owner=user)
    resp = auth_client.patch(f'{PRODUCTS_URL}{p.id}/deactivate/')
    assert resp.status_code == 200
    assert resp.data['status'] == 'INACTIVE'

    resp2 = auth_client.patch(f'{PRODUCTS_URL}{p.id}/activate/')
    assert resp2.status_code == 200
    assert resp2.data['status'] == 'ACTIVE'


@pytest.mark.django_db
def test_delete_product(auth_client, user):
    p = Product.objects.create(name='Delete Item', price='5.00', stock_quantity=3, owner=user)
    resp = auth_client.delete(f'{PRODUCTS_URL}{p.id}/')
    assert resp.status_code == 204
    assert not Product.objects.filter(id=p.id).exists()
