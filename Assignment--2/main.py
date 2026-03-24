#-------Day-1------
# from fastapi import FastAPI
# app=FastAPI()
# @app.get("/")
# def home():
#     return {"message":"Welcome to our app"}

#--------Day-2--------
from fastapi import FastAPI,Query,Response,status
from pydantic import BaseModel, Field
app=FastAPI()
def find_product(product_id:int):
    for p in products:
        if p['id']==product_id:
            return p
    return None
def calculate_total(product:dict,quantity:int):
    return product['price']*quantity
def filter_products_logic(category=None,min_price=None,max_price=None,in_stock=None):
    result=products
    if category is not None:
        result=[p for p in result if p['category']==category]
    if min_price is not None:
        result=[p for p in result if p['price']==min_price]
    if max_price is not None:
        result=[p for p in result if p['price']==max_price]
    if in_stock is not None:
        result=[p for p in result if p['in_stock']==in_stock]
    return result
class OrderRequest(BaseModel):
    customer_name:str=Field(...,min_length=2,max_length=100)
    product_id:int=Field(...,gt=0)
    quantity:int=Field(...,gt=0,le=100)
    delivery_address:str=Field(...,min_length=10)
from typing import Optional

class CustomerFeedback(BaseModel):
    customer_name:str=Field(...,min_length=2)
    product_id:int=Field(...,gt=0)
    rating:int=Field(...,gt=0,le=5)
    comment:Optional[str]=Field(None,max_length=300)
feedback=[]
@app.post("/feedback")
def submit_feedback(data:CustomerFeedback):
    feedback.append(data.dict())
    return{
        "message":"Feedback submitted successfully",
        "feedback":data.dict(),
        "total_feedback":len(feedback),
    }
from typing import List
class OrderItem(BaseModel):
    product_id:int=Field(...,gt=0)
    quantity:int=Field(...,gt=0,le=50)
class BulkOrder(BaseModel):
    company_name:str=Field(...,min_length=2)
    contact_email:str=Field(min_length=5)
    items:list[OrderItem]=Field(...,min_items=1)
@app.post("/orders/bulk")
def check_order(order:BulkOrder):
    confirmed,failed,grandtotal=[],[],0
    for item in order.items:
        product=next((p for p in products if p['id']==item.product_id),None)
        if not product:
            failed.append({"product_id":item.product_id,"reason":"Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id":item.product_id,"reason":f"{product['name']}is out of stock"})
        else:
            subtotal=product["price"]*item.quantity
            grandtotal+=subtotal
            confirmed.append({"product":product["name"],"qty":item.quantity,"subtotal":subtotal})
    return{"company":order.company_name, "confirmed": confirmed,
            "failed": failed, "grand_total": grandtotal}
@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if     p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["Category"] for p in products))
    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }
products=[
    {'id':1, 'name':'Wireless Mouse', 'price':499, 'Category':'Electronics', 'in_stock':True},
    {'id':2, 'name':'Notebook', 'price':99, 'Category':'Stationary', 'in_stock':True},
    {'id':3, 'name':'USB Hub', 'price':799, 'Category':'Electronics', 'in_stock':False},
    {'id':4, 'name':'Pen Set', 'price':49, 'Category':'Stationary', 'in_stock':True},
    # {'id':5, 'name':'Laptop Stand', 'price':500, 'Category':'Stationary', 'in_stock':True},
    # {'id':6, 'name':'Mechanical Keyboard', 'price':399, 'Category':'Electronics', 'in_stock':False},
    # {'id':7, 'name':'Webcamp', 'price':999, 'Category':'Electronics', 'in_stock':True}
]
orders=[]
order_counter=1
@app.get('/')
def home():
    return {'message':'Welcome to our E-commerce API'}
@app.get('/products')
def get_all_products():
    return {'products':products,'total':len(products)}
@app.get('/products/filter')
def filter_products(
    category:str=Query(None,description='Electronics' or 'Stationary'),
    max_price:int=Query(None,description='Maximum Price'),
    in_stack:bool=Query(None,description='True in stack only'),
    min_price:int=Query(None,description='Minimum Price')
):
    result=products
    if category:
        result=[p for p in result if p['category']==category]
    if max_price:
        result=[p for p in result if p['price']<=max_price]
    if in_stack is not None:
        result=[p for p in result if p['in_stack']==in_stack]
    if min_price:
        result=[p for p in result if p['price']>=min_price]
    return {'filtered_products':result,'count':len(result)}
@app.get('/products/category/{category_name}')
def get_by_category(category_name:str):
    result=[p for p in products if p["Category"]==category_name]
    if not result:
        return {'Error: No products found in this category'}
    return {'category':{category_name},'products':result,'total':len(result)}
# @app.get('/products/in_stock/')
# def get_by_stock():
#     result=[p for p in products if p["in_stock"]==True]
#     return {'in_stock_products':result,'count':len(result)}
@app.get("/products/instock") 
def get_instock(): 
    available = [p for p in products if p["in_stock"]] 
    return {"in_stock_products": available, "count": len(available)}
@app.get('/store/summary')
def store_summary():
    in_stock_count=len([p for p in products if p['in_stock']])
    out_of_stock=len(products)-in_stock_count
    categories=list(set([p['Category']for p in products]))
    return {"store_name":"My E-commerce store","total_products":len(products),
            "in_stock":in_stock_count,"out_of_stock":out_of_stock,"categories":categories
            }
@app.get('/products/search/{product_name}')
def get_items(product_name:str):
    result=[p for p in products if product_name.lower() in p['name'].lower()]
    if not result:
        return{"message":"No products matched your search"}
    return {"product name":product_name,"matched_product":result,"total count of matches":len(result)}
@app.get('/products/deals')
def get_cheap_premium_product():
    lowest_price=min(products,key=lambda p: p['price'])
    highest_price=max(products,key=lambda p: p['price'])
    return {"best deal":lowest_price,"premium_pick":highest_price}
@app.get('/products/audit')
def product_id():
    stock_count_list=[p for p in products if p['in_stock']]
    out_stock_list=[p for p in products if not p['in_stock']]
    stock_value=sum(p['price']*10 for p in stock_count_list)
    priciest=max(products,key=lambda p:p['price'])
    return {'total_products':len(products),'in_stock_count':len(stock_count_list),'out_of_stock_count':(p['name'] for p in products),'total_stock_value':stock_value,'most_expensive':{'name':priciest['name'],'price':priciest['price']},}
@app.put('/products/discount') 
def bulk_discount( 
    category: str = Query(..., description='Category to discount'), discount_percent: int = Query(..., ge=1, le=99, description='% off'), 
    ): 
    updated = [] 
    for p in products: 
        if p['Category'] == category: p['price'] = int(p['price'] * (1 - discount_percent / 100)) 
        updated.append(p) 
    if not updated: 
        return {'message': f'No products found in category: {category}'} 
    return { 'message': f'{discount_percent}% discount applied to {category}', 'updated_count': len(updated), 'updated_products': updated, }

@app.get('/products/{product_id}')
def get_product(product_id:int):
    for product in products:
        if product['id']==product_id:
            return {'product':product}
    return {'error':'Product not found'}
@app.post('/orders')
def place_order(order_data:OrderRequest):
    global order_counter
    product=next((p for p in products if p['id']==order_data.product_id),None)
    if product is None:
        return{'error':'Product not found'}
    if not product['in_stock']:
        return{'error':f"{product['name']} is out of stock"}
    total_price=product['price']*order_data.quantity
    order={'order_id':order_counter,'customer_name':order_data.customer_name,'product':product['name'],'quantity':order_data.quantity,'delivery_address':order_data.delivery_address,'total_price':total_price,'status':'pending'}
    orders.append(order)
    order_counter+=1
    return{'message':'Order placed successfully','order':order}

@app.get("/orders/{order_id}")
def get_order(order_id:int):
    for order in orders:
        if order['order_id']==order_id:
            return {"Order":order}
    return{"error":"Order not found"}
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id:int):
    for order in orders:
        if order['order_id']==order_id:
            return{"message":"Order Confirmed","order":order}
    return{"error":"Order not found"}
@app.get('/orders')
def get_all_orders():
    return{'orders':orders,'total_orders':len(orders)}
@app.get('/products/{product_id}/price')
def get_proName_price(product_id:int):
    for product in products:
        if product['id']==product_id:
            return{'Procudt':product['name'],'Price':product['price']}
    return{'error':'Product not found'}
# ■■ Day 3 ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
@app.get('/products/compare')
def compare_products(
    product_id_1: int = Query(...),
    product_id_2: int = Query(...),
):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1:
        return {'error': f'Product {product_id_1} not found'}
    if not p2:
        return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {
'product_1': p1,
'product_2': p2,
'better_value': cheaper['name'],
'price_diff': abs(p1['price'] - p2['price']),
}
# ■■ Day 4 — CRUD (variable routes come AFTER fixed routes) ■■■■■
class NewProduct(BaseModel):
    name:str=Field(...,min_length=2,max_length=100)
    price:int=Field(...,gt=0)
    category:str=Field(...,min_length=2)
    in_stock:bool=True
@app.post('/products')
def add_product(new_product: NewProduct, response: Response):
    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}
    next_id = max(p['id'] for p in products) + 1
    product = {
    'id': next_id,
    'name': new_product.name,
    'price': new_product.price,
    'category': new_product.category,
    'in_stock': new_product.in_stock,
}
    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}
@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    response: Response,
    in_stock: bool = Query(None,description='Update stock status'),
    price: int = Query(None,description='Update price'),
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    if in_stock is not None:
        product['in_stock'] = in_stock
    if price is not None:
        product['price'] = price
    return {'message': 'Product updated', 'product': product}
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}

@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        return {'error': 'Product not found'}
        return {'product': product}

