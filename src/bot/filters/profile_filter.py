from aiogram.filters import BaseFilter


class ProfileFilter(BaseFilter):
    async def __call__(self, *args, **kwargs):
        # TODO: Get information from the database
        return True
