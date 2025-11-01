from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, Enrollment


# 首頁：顯示所有修課與平均
def index(request):
    enrollments = Enrollment.objects.select_related('course').all()
    for e in enrollments:
        mid = e.midterm_score or 0
        fin = e.final_score or 0
        e.average = round((mid + fin) / 2, 1)

    avg_score = None
    if enrollments:
        total = sum(e.average for e in enrollments)
        avg_score = round(total / len(enrollments), 2)

    return render(request, "index.html", {
        "enrollments": enrollments,
        "avg_score": avg_score
    })


# 課程列表
def course_list(request):
    courses = Course.objects.all().order_by("course_id")
    return render(request, "course_list.html", {"courses": courses})


# 新增課程
def add_course(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id", "").strip()
        name = request.POST.get("name", "").strip()
        teacher = request.POST.get("teacher", "").strip()

        if not course_id or not name or not teacher:
            messages.error(request, "課號、課名、任課老師不可為空。")
            return render(request, "add_course.html")

        if Course.objects.filter(course_id=course_id).exists():
            messages.error(request, f"課號 {course_id} 已存在，請使用其他課號。")
            return render(request, "add_course.html")

        Course.objects.create(course_id=course_id, name=name, teacher=teacher)
        messages.success(request, f"成功新增課程：{name}")
        return redirect("course_list")

    return render(request, "add_course.html")


# 課程詳情頁
def course_detail(request, course_id: str):
    course = get_object_or_404(Course, course_id=course_id)
    enrollments = Enrollment.objects.filter(course=course)
    for e in enrollments:
        mid = e.midterm_score or 0
        fin = e.final_score or 0
        e.average = round((mid + fin) / 2, 1)

    return render(request, "course_detail.html", {
        "course": course,
        "enrollments": enrollments
    })


# 加選（不需登入）
def enroll_course(request, course_id: str):
    course = get_object_or_404(Course, course_id=course_id)
    student = "訪客"
    enrollment, created = Enrollment.objects.get_or_create(course=course, student=student)
    if created:
        messages.success(request, f"已加選：{course.name}")
    else:
        messages.info(request, f"你已加選過 {course.name}")
    return redirect("course_detail", course_id=course_id)


# 退選（不需登入）
def drop_course(request, course_id: str):
    course = get_object_or_404(Course, course_id=course_id)
    student = "訪客"
    deleted, _ = Enrollment.objects.filter(course=course, student=student).delete()
    if deleted:
        messages.success(request, f"已退選：{course.name}")
    else:
        messages.info(request, f"你尚未加選 {course.name}")
    return redirect("course_detail", course_id=course_id)


# 顯示所有修課（模擬「我的修課」）
def my_courses(request):
    enrollments = Enrollment.objects.select_related("course").all().order_by("course__course_id")
    for e in enrollments:
        mid = e.midterm_score or 0
        fin = e.final_score or 0
        e.average = round((mid + fin) / 2, 1)

    return render(request, "my_courses.html", {"enrollments": enrollments})
