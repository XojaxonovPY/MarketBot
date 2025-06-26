from db.model import User
async def save_user(**kwargs):
    check=await User.get(User.user_id,kwargs.get('user_id'))
    if not check:
        await User.create(**kwargs)






