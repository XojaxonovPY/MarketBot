from sqlalchemy import Text, String, BIGINT, DECIMAL, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base, db
from db.utils import CreatedModel


class User(CreatedModel):
    user_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=True)

    orders = relationship('Order', back_populates='user', lazy='selectin')


class Category(CreatedModel):
    __tablename__ = 'categories'
    name: Mapped[str] = mapped_column(String)

    products = relationship('Product', back_populates='category', lazy='selectin')

    def __repr__(self):
        return f"{self.name}"


class Product(CreatedModel):
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    image_url: Mapped[str] = mapped_column(Text,nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(Text,nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))

    category = relationship('Category', back_populates='products', lazy='selectin')
    orders = relationship('Order', back_populates='product', lazy='selectin')

    def __repr__(self):
        return f"{self.name},{self.price},{self.image_url},{self.category_id},{self.count}"


class Order(CreatedModel):
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_price: Mapped[float] = mapped_column(Float)
    product = relationship('Product', back_populates='orders', lazy='selectin')
    user = relationship('User', back_populates='orders', lazy='selectin')


class Channel(CreatedModel):
    link: Mapped[str] = mapped_column(String)
    channel_id: Mapped[int] = mapped_column(BIGINT)


metadata = Base.metadata
