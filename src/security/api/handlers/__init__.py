from .ping import PingView
from .user import RegisterView
from .project import ProjectView, ProjectNameView

HANDLERS = (
    PingView,
    RegisterView,
    ProjectView,
    ProjectNameView,
)
