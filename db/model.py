
from sqlalchemy import Text, String, BIGINT, DECIMAL, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base, db
from db.utils import CreatedModel



class User(CreatedModel):
    user_id:Mapped[int]=mapped_column(BIGINT,unique=True)
    username:Mapped[str]=mapped_column(String,nullable=True)
    order=relationship('Order',back_populates='user')

class Category(CreatedModel):
    __tablename__ = 'categories'

    name:Mapped[str]=mapped_column(String)
    product = relationship('Product', back_populates='category')

    def __repr__(self):
        return f"{self.name}"


class Product(CreatedModel):
    name:Mapped[str]=mapped_column(String)
    price:Mapped[float]=mapped_column(Float)
    image:Mapped[str]=mapped_column(Text)
    count:Mapped[int]=mapped_column(Integer,default=1,nullable=False)
    category_id:Mapped[int]=mapped_column(ForeignKey('categories.id',ondelete='CASCADE'))
    category=relationship('Category',back_populates='product')
    order=relationship('Order',back_populates='product')

    def __repr__(self):
        return f"{self.name},{self.price},{self.image},{self.category_id},{self.count}"


class Order(CreatedModel):
    product_name:Mapped[str]=mapped_column(String)
    product_price:Mapped[float]=mapped_column(Float)
    product_count:Mapped[int]=mapped_column(Integer)
    product_id:Mapped[int]=mapped_column(ForeignKey('products.id',ondelete='CASCADE'))
    user_id:Mapped[int]=mapped_column(ForeignKey('users.user_id',ondelete='CASCADE'))
    product=relationship('Product',back_populates='order')
    user=relationship('User',back_populates='order')
    def __repr__(self):
        return f"{self.product_name},{self.product_id},{self.product_id}"

class Channel(CreatedModel):
    link:Mapped[str]=mapped_column(String)
    channel_id:Mapped[int]=mapped_column(BIGINT)



metadata = Base.metadata
