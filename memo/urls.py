from django.urls import path

from .views import MemoListView, MemoDetailView, MemoCreateView, MemoEditView, MemoDeleteView


app_name = "memo"
urlpatterns = [
    path("", MemoListView.as_view(), name="memo"),
    path("detail/<slug:slug>/", MemoDetailView.as_view(), name="detail"),
    path("create/", MemoCreateView.as_view(), name="create"),
    path("edit/<slug:slug>/", MemoEditView.as_view(), name="edit"),
    path("delete/<slug:slug>/", MemoDeleteView.as_view(), name="delete"),
]