from aiogram.filters import BaseFilter


class DreamsFilter(BaseFilter):
    async def __call__(self, *args, **kwargs):
        # TODO: Get information from the database
        return True
