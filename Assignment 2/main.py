#-------Day-1------
# from fastapi import FastAPI
# app=FastAPI()
# @app.get("/")
# def home():
#     return {"message":"Welcome to our app"}

#--------Day-2--------
from fastapi import FastAPI,Query
from pydantic import BaseModel, Field
app=FastAPI()
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
