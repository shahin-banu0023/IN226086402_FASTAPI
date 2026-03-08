#-------Day-1------
# from fastapi import FastAPI
# app=FastAPI()
# @app.get("/")
# def home():
#     return {"message":"Welcome to our app"}

#--------Day-2--------
from fastapi import FastAPI,Query
app=FastAPI()
products=[
    {'id':1, 'name':'Wireless Mouse', 'price':499, 'Category':'Electronics', 'in_stock':True},
    {'id':2, 'name':'Notebook', 'price':99, 'Category':'Stationary', 'in_stock':True},
    {'id':3, 'name':'USB Hub', 'price':799, 'Category':'Electronics', 'in_stock':False},
    {'id':4, 'name':'Pen Set', 'price':49, 'Category':'Stationary', 'in_stock':True},
    {'id':5, 'name':'Laptop Stand', 'price':500, 'Category':'Stationary', 'in_stock':True},
    {'id':6, 'name':'Mechanical Keyboard', 'price':399, 'Category':'Electronics', 'in_stock':False},
    {'id':7, 'name':'Webcamp', 'price':999, 'Category':'Electronics', 'in_stock':True}
]
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
    in_stack:bool=Query(None,description='True in stack only')
):
    result=products
    if category:
        result=[p for p in result if p['category']==category]
    if max_price:
        result=[p for p in result if p['price']<=max_price]
    if in_stack is not None:
        result=[p for p in result if p['in_stack']==in_stack]
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