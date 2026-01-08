from django.views.generic import ListView, UpdateView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger, EmptyPage

from .models import Memo
from .forms import MemoForm


class UserInjectMixin:
    """request.userを自動でmodelにセット"""
    user_field = "user"
    
    def form_valid(self, form):
        setattr(form.instance, self.user_field, self.request.user)
        # つまりmemo.user=self.request.userとなるようにする
        return super().form_valid(form)


class MemoListView(LoginRequiredMixin, ListView):
    """メモ帳一覧を表示する。タイトルとメモ内容を表示"""
    template_name = "memo.html"
    paginate_by = 9 
    paginate_orphans = 2 # 最終ページ2つだけなら前ページに含める
    # context_object_name = "memos"
    # page_objがページオブジェクトになる(memosではない)ページネーションの部品化を考えるとpage_objの方が良い    
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = Memo.objects.filter(user=self.request.user)
            category = self.request.GET.get("category")
            if category:
                qs = qs.filter(category=category)
            # カテゴリごとでクエリセットを絞れる
            return qs.order_by("-priority", "-updated_at", "-created_at")
        else:
            return Memo.objects.none()
    
    def paginate_queryset(self, queryset, page_size):
        # 存在しないページのとき１ページ目を返すように設定
        paginator = self.get_paginator(queryset, page_size, orphans=self.paginate_orphans)
        page = self.request.GET.get(self.page_kwarg) or 1
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)
        return  (paginator, page_obj, page_obj.object_list, page_obj.has_other_pages())
    

class MemoCreateView(LoginRequiredMixin, UserInjectMixin, CreateView):
    # UserInjectMixinを継承して、request.userを自動入力
    model = Memo
    template_name = "create.html"
    form_class = MemoForm
    success_url = reverse_lazy("memo:memo")
    
    

class MemoDetailView(LoginRequiredMixin, DetailView):
    model = Memo
    template_name = "detail.html"
    context_object_name = "memo"
    slug_url_kwarg = "slug"
    slug_field = "slug"
    
    def get_queryset(self):
        # user=self.request.user で自分のオブジェクトしか見れなくなる。
        return Memo.objects.filter(user=self.request.user)

class MemoEditView(LoginRequiredMixin, UpdateView):
    model = Memo
    template_name = "edit.html"
    form_class = MemoForm
    slug_field = "slug"
    slug_url_kwarg = "slug"
    def get_success_url(self):
        return reverse_lazy("memo:detail", kwargs={"slug": self.object.slug})
    
    def get_queryset(self):
        return Memo.objects.filter(user=self.request.user)
    

class MemoDeleteView(LoginRequiredMixin,  DeleteView):
    model = Memo
    template_name = "delete.html"
    success_url = reverse_lazy("memo:memo")
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Memo.objects.filter(user=self.request.user)


    
