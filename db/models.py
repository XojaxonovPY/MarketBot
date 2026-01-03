from enum import Enum

from sqlalchemy import Text, String, BIGINT, ForeignKey, Integer, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.utils import Model, Base


class StatusType(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    DELIVERED = 'delivered'
    RETURNED = 'returned'


class User(Model):
    id = None
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(length=50), nullable=True)

    orders = relationship('Order', back_populates='user', lazy='selectin')

    @staticmethod
    async def save_user(data: dict):
        check = await User.get(user_id=data.get('user_id'))
        if not check:
            await User.create(**data)


class Category(Model):
    __tablename__ = 'categories'
    name: Mapped[str] = mapped_column(String(length=100))

    products = relationship('Product', back_populates='category', lazy='selectin')

    def __repr__(self):
        return f"{self.name}"


class Product(Model):
    name: Mapped[str] = mapped_column(String(length=100))
    price: Mapped[float] = mapped_column(Float)
    image_url: Mapped[str] = mapped_column(Text)
    thumbnail_url: Mapped[str] = mapped_column(Text)
    count: Mapped[int] = mapped_column(Integer, default=1)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))

    category = relationship('Category', back_populates='products', lazy='joined')
    orders = relationship('Order', back_populates='product', lazy='selectin')

    def __repr__(self):
        return f"{self.name},{self.price},{self.image_url},{self.category_id},{self.count}"

    @staticmethod
    async def sub_product(id_: int, count: int):
        product: Product = await Product.get(id=id)
        await Product.update(product.id, count=product.count - count)


class Order(Model):
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str | None] = mapped_column(SQLEnum(
        StatusType, name='status_type',
        create_constraint=True),
        default=StatusType.PENDING, nullable=True
    )
    total_price: Mapped[float] = mapped_column(Float)
    product = relationship('Product', back_populates='orders', lazy='joined')
    user = relationship('User', back_populates='orders', lazy='joined')


class Channel(Model):
    link: Mapped[str | None] = mapped_column(String)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    channel_id: Mapped[int] = mapped_column(BIGINT, nullable=True)


metadata = Base.metadata
