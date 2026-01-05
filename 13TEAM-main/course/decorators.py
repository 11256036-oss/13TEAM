from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def _get_role(user):
    # 你如果有 Profile.role 就會用到；沒有也不會炸
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None)

def teacher_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        role = _get_role(request.user)

        # 兩種判斷擇一即可：
        # A) 用 Profile.role
        if role == "teacher":
            return view_func(request, *args, **kwargs)

        # B) 或者你用 admin 建的老師帳號是 staff，也可以放行：
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)

        # 不符合：擋掉
        return HttpResponseForbidden("你沒有教師權限")
        # 或改成：return redirect("student_courses")
    return _wrapped


def student_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        role = _get_role(request.user)

        if role == "student":
            return view_func(request, *args, **kwargs)

        # staff/teacher 不給進學生頁（你想允許也可以改）
        return HttpResponseForbidden("你沒有學生權限")
    return _wrapped
