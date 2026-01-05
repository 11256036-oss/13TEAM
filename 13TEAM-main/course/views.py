# course/views.py

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .decorators import teacher_required, student_required
from .models import Course, Enrollment, Comment, Profile



def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        full_name = request.POST.get("full_name", "").strip()

        # 基本檢查
        if not username or not password:
            return render(request, "registration/register.html", {
                "error": "帳號與密碼必填"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "registration/register.html", {
                "error": "此帳號已存在"
            })

        user = User.objects.create_user(username=username, password=password)

       
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = "student"
        profile.full_name = full_name or username
        profile.save()

        return redirect("login")

    return render(request, "registration/register.html")

@login_required
def after_login(request):
    role = getattr(getattr(request.user, "profile", None), "role", "student")
    if role == "teacher" or request.user.is_staff:
        return redirect("teacher_courses")
    return redirect("student_courses")


# =========================
# 個人資料
# =========================
@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "student", "full_name": request.user.username}
    )

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name", profile.full_name).strip()

        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]

        profile.save()
        return redirect("student_courses")

    return render(request, "profile/edit_profile.html", {"profile": profile})


# =========================
# 教師功能（學生進不來）
# =========================
@teacher_required
def teacher_courses(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, "teacher/course_list.html", {"courses": courses})


@teacher_required
def create_course(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        semester = request.POST.get("semester", "").strip()
        if name and semester:
            Course.objects.create(
                name=name,
                semester=semester,
                teacher=request.user
            )
    return redirect("teacher_courses")


@teacher_required
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    enrollments = Enrollment.objects.filter(course=course).select_related("student")

    # 主留言 + 回覆
    comments = (
        Comment.objects
        .filter(course=course, parent__isnull=True)
        .select_related("user")
        .prefetch_related("replies__user")
        .order_by("-created_at")
    )

    # 儲存成績（用 _action 區分）
    if request.method == "POST" and request.POST.get("_action") == "save_grades":
        for e in enrollments:
            mid = request.POST.get(f"mid_{e.id}", "").strip()
            fin = request.POST.get(f"final_{e.id}", "").strip()

            e.midterm = float(mid) if mid else None
            e.final = float(fin) if fin else None
            e.save()

        return redirect("course_students", course_id=course.id)

    return render(request, "teacher/course_students.html", {
        "course": course,
        "enrollments": enrollments,
        "comments": comments,
    })


@teacher_required
def reply_comment(request, comment_id):
    parent = get_object_or_404(Comment, id=comment_id)

    # 保險：只能該課老師回覆
    if parent.course.teacher != request.user:
        return HttpResponseForbidden("只有這門課的老師可以回覆留言")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(
                course=parent.course,
                user=request.user,
                content=content,
                parent=parent
            )

    return redirect("course_students", course_id=parent.course.id)


@teacher_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == "POST":
        course.delete()
        return redirect("teacher_courses")

    return render(request, "teacher/delete_course_confirm.html", {"course": course})


# =========================
# 學生功能（老師要不要能看你可自行調整）
# =========================
@student_required
def student_courses(request):
    courses = Course.objects.all()
    my_courses = Enrollment.objects.filter(student=request.user)
    my_course_ids = set(my_courses.values_list("course_id", flat=True))

    return render(request, "student/course_list.html", {
        "courses": courses,
        "my_courses": my_courses,
        "my_course_ids": my_course_ids,
    })


@student_required
def enroll(request, course_id):
    Enrollment.objects.get_or_create(student=request.user, course_id=course_id)
    return redirect("student_courses")


@student_required
def drop(request, course_id):
    Enrollment.objects.filter(student=request.user, course_id=course_id).delete()
    return redirect("student_courses")


@student_required
def my_grades(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")

    avgs = []
    for e in enrollments:
        # 兼容你 average 可能是「方法」或「欄位」
        if callable(getattr(e, "average", None)):
            v = e.average()
        else:
            v = getattr(e, "average", None)
        if v is not None:
            avgs.append(v)

    semester_avg = (sum(avgs) / len(avgs)) if avgs else None

    return render(request, "student/my_courses.html", {
        "enrollments": enrollments,
        "semester_avg": semester_avg
    })


# =========================
# 課程詳情 / 留言（學生留言、學生編輯/刪除自己的留言、學生看老師回覆）
# =========================
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    comments = (
        Comment.objects
        .filter(course=course, parent__isnull=True)
        .select_related("user")
        .prefetch_related("replies__user")
        .order_by("-created_at")
    )

    enrollments = Enrollment.objects.filter(course=course)

    if request.method == "POST":
        role = getattr(getattr(request.user, "profile", None), "role", "student")
        if role != "student" and not request.user.is_staff:
            return HttpResponseForbidden("只有學生可以留言")

        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(course=course, user=request.user, content=content)

        return redirect("course_detail", course_id=course.id)

    return render(request, "course/detail.html", {
        "course": course,
        "comments": comments,
        "enrollments": enrollments,
    })


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return HttpResponseForbidden("你不能修改別人的留言")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            comment.content = content
            comment.save()
        return redirect("course_detail", course_id=comment.course.id)

    return render(request, "course/edit_comment.html", {"comment": comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    course_id = comment.course.id

    if request.method == "POST":
        comment.delete()

    return redirect("course_detail", course_id=course_id)
