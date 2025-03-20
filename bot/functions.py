from db.model import User, Product, Order

async def save_user(**kwargs):
    check=await User.get(User.user_id,kwargs.get('user_id'))
    if not check:
        await User.create(**kwargs)

async def get_products(category_id:str):
    s=''.join([i for i in category_id if i.isdigit()])
    products=await Product.gets(Product.category_id,int(s),Product.name)
    return products

async def get_orders(product_name:str):
    price = await Product.gets(Product.name, product_name,Product.price)
    image=await Product.gets(Product.name,product_name,Product.image)
    count=await Product.gets(Product.name,product_name,Product.count)
    id_=await Product.gets(Product.name,product_name,Product.id)
    price_format = f"{price[0]}"
    count_format=f'{count[0]}'
    id_format=f'{id_[0]}'
    return price_format,count_format,''.join(image),id_format

async def orders_save(**kwargs):
    await Order.create(**kwargs)

async def get_order(user_id):
    product_name=await Order.gets(Order.user_id,user_id,Order.product_name)
    product_count=await Order.gets(Order.user_id,user_id,Order.product_count)
    product_price=await Order.gets(Order.user_id,user_id,Order.product_price)
    return product_name,product_price,product_count

async def search_products(product_id:int):
    price = await Product.gets(Product.id, product_id,Product.price)
    image=await Product.gets(Product.id,product_id,Product.image)
    count=await Product.gets(Product.id,product_id,Product.count)
    name=await Product.gets(Product.id,product_id,Product.name)
    price_format = f"{price[0]}"
    count_format=f'{count[0]}'
    name_format=f'{name[0]}'
    return name_format, price_format,count_format,''.join(image)


