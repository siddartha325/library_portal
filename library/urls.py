from django.urls import path
from . import views

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("issue/", views.issue_book, name="issue"),
    path("return/", views.return_book, name="return"),
    path("history/", views.history, name="history"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("calculate-fine/", views.calculate_fine, name="calculate_fine"),

    # Book Management
path("books/", views.book_list, name="book_list"),
path("books/add/", views.add_book, name="add_book"),
path("books/edit/<int:pk>/", views.edit_book, name="edit_book"),
path("books/delete/<int:pk>/", views.delete_book, name="delete_book"),
]