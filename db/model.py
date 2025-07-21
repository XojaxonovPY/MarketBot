from enum import Enum

from sqlalchemy import Text, String, BIGINT, ForeignKey, Integer, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from db.utils import CreatedModel


class StatusType(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    DELIVERED = 'delivered'
    RETURNED = 'returned'


class User(CreatedModel):
    user_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=True)

    orders = relationship('Order', back_populates='user', lazy='selectin')

    async def save_user(**kwargs):
        check = await User.get(User.user_id, kwargs.get('user_id'))
        if not check:
            await User.create(**kwargs)


class Category(CreatedModel):
    __tablename__ = 'categories'
    name: Mapped[str] = mapped_column(String)

    products = relationship('Product', back_populates='category', lazy='selectin')

    def __repr__(self):
        return f"{self.name}"


class Product(CreatedModel):
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(Text, nullable=True)
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
    status: Mapped[str] = mapped_column(SQLEnum(StatusType, name='status_type', create_constraint=True),
                                        default=StatusType.PENDING, nullable=True)
    total_price: Mapped[float] = mapped_column(Float)
    product = relationship('Product', back_populates='orders', lazy='selectin')
    user = relationship('User', back_populates='orders', lazy='selectin')


class Channel(CreatedModel):
    link: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=True)
    channel_id: Mapped[int] = mapped_column(BIGINT, nullable=True)


metadata = Base.metadata
