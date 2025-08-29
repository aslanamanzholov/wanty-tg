"""This package is used for a bot logic implementation."""
from .help import help_router
from .start import start_router
from .profile import myprofile_router
from .dreams import dreams_router
from .register import register_router
from .achievements import achievements_router

routers = (
    help_router,
    start_router,
    myprofile_router, 
    dreams_router, 
    register_router,
    achievements_router
)
