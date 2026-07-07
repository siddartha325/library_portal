from decimal import Decimal
from datetime import timedelta
from .forms import BookForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .forms import BookIssueForm, BookReturnForm
from .models import Book, Member, CirculationRecord


# =========================
# Catalog
# =========================

def catalog(request):

    books = Book.objects.all()

    search = request.GET.get("search")
    genre = request.GET.get("genre")

    if search:
        books = books.filter(title__icontains=search)

    if genre:
        books = books.filter(genre=genre)

    return render(request, "library/catalog.html", {
        "books": books
    })


# =========================
# Dashboard
# =========================

@login_required
def dashboard(request):

    total_books = Book.objects.count()

    available_books = Book.objects.filter(
        available_copies__gt=0
    ).count()

    borrowed = CirculationRecord.objects.filter(
        is_returned=False
    )

    total_members = Member.objects.count()

    context = {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed.count(),
        "members": total_members,
        "borrowed": borrowed,
        "today": timezone.now().date(),
    }

    return render(
        request,
        "library/dashboard.html",
        context
    )


# =========================
# Issue Book
# =========================

@login_required
def issue_book(request):

    if request.method == "POST":

        form = BookIssueForm(request.POST)

        if form.is_valid():

            record = form.save(commit=False)

            book = record.book
            member = record.member

            # Prevent duplicate active issue
            if CirculationRecord.objects.filter(
                book=book,
                member=member,
                is_returned=False
            ).exists():

                messages.error(
                    request,
                    "This member already has this book issued."
                )

                return redirect("issue")

            # Check available copies
            if book.available_copies <= 0:

                messages.error(
                    request,
                    "No copies available."
                )

                return redirect("issue")

            # Automatically set dates
            record.issue_date = timezone.now().date()
            record.due_date = record.issue_date + timedelta(days=14)
            record.return_date = None
            record.is_returned = False
            record.fine_amount = Decimal("0.00")

            # Save record
            record.save()

            # Reduce available copies
            book.available_copies -= 1
            book.save()

            messages.success(
                request,
                f"""
Book issued successfully!

Book : {book.title}

Member : {member.name}

Issue Date : {record.issue_date}

Due Date : {record.due_date}
"""
            )

            return redirect("catalog")

        else:

            print(form.errors)

            messages.error(
                request,
                f"Form Errors: {form.errors}"
            )

    else:

        form = BookIssueForm()

    return render(
        request,
        "library/issue_book.html",
        {
            "form": form,
            "today": timezone.now().date(),
        }
    )


# =========================
# Return Book
# =========================

@login_required
def return_book(request):

    if request.method == "POST":

        form = BookReturnForm(request.POST)

        if form.is_valid():

            record = CirculationRecord.objects.filter(
                book=form.cleaned_data["book"],
                member=form.cleaned_data["member"],
                is_returned=False
            ).order_by("-issue_date").first()

            if record is None:

                messages.error(
                    request,
                    "Borrow record not found."
                )

                return redirect("return")

            record.return_date = timezone.now().date()
            record.is_returned = True

            late_days = 0
            record.fine_amount = Decimal("0.00")

            if record.return_date > record.due_date:

                late_days = (
                    record.return_date - record.due_date
                ).days

                record.fine_amount = (
                    Decimal(late_days) * Decimal("0.50")
                )

            record.save()

            book = record.book
            book.available_copies += 1
            book.save()

            messages.success(
                request,
                f"""
Book returned successfully!

Issue Date : {record.issue_date}
Due Date : {record.due_date}
Return Date : {record.return_date}

Late Days : {late_days}

Fine Amount : ₹{record.fine_amount}
"""
            )

            return redirect("catalog")

    else:

        form = BookReturnForm()

    return render(
        request,
        "library/return_book.html",
        {
            "form": form
        }
    )


# =========================
# History
# =========================

@login_required
def history(request):

    records = CirculationRecord.objects.all().order_by(
        "-issue_date"
    )

    return render(
        request,
        "library/history.html",
        {
            "records": records
        }
    )


# =========================
# Login
# =========================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("catalog")

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                username=username,
                password=password
            )

            if user:

                login(request, user)

                return redirect("catalog")

        messages.error(
            request,
            "Invalid username or password."
        )

    else:

        form = AuthenticationForm()

    return render(
        request,
        "library/login.html",
        {
            "form": form
        }
    )


# =========================
# Logout
# =========================

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("login")


# =========================
# AJAX Fine Calculator
# =========================

@login_required
def calculate_fine(request):

    book_id = request.GET.get("book")
    member_id = request.GET.get("member")

    if not book_id or not member_id:

        return JsonResponse({
            "fine": "0.00",
            "late_days": 0,
            "due_date": "",
            "today": timezone.now().date().strftime("%d-%m-%Y")
        })

    record = CirculationRecord.objects.filter(
        book_id=book_id,
        member_id=member_id,
        is_returned=False
    ).order_by("-issue_date").first()

    if record is None:

        return JsonResponse({
            "fine": "0.00",
            "late_days": 0,
            "due_date": "",
            "today": timezone.now().date().strftime("%d-%m-%Y")
        })

    today = timezone.now().date()

    late_days = 0
    fine = Decimal("0.00")

    if today > record.due_date:

        late_days = (
            today - record.due_date
        ).days

        fine = (
            Decimal(late_days) * Decimal("0.50")
        )

    return JsonResponse({

        "issue_date": record.issue_date.strftime("%d-%m-%Y"),
        "due_date": record.due_date.strftime("%d-%m-%Y"),
        "today": today.strftime("%d-%m-%Y"),
        "late_days": late_days,
        "fine": str(fine)

    })
@login_required
def book_list(request):

    books = Book.objects.all().order_by("title")

    return render(
        request,
        "library/book_list.html",
        {
            "books": books
        }
    )


@login_required
def add_book(request):

    if request.method == "POST":

        form = BookForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Book added successfully."
            )

            return redirect("book_list")

    else:

        form = BookForm()

    return render(
        request,
        "library/book_form.html",
        {
            "form": form,
            "title": "Add Book"
        }
    )


@login_required
def edit_book(request, pk):

    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":

        form = BookForm(
            request.POST,
            instance=book
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Book updated successfully."
            )

            return redirect("book_list")

    else:

        form = BookForm(instance=book)

    return render(
        request,
        "library/book_form.html",
        {
            "form": form,
            "title": "Edit Book"
        }
    )


@login_required
def delete_book(request, pk):

    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":

        book.delete()

        messages.success(
            request,
            "Book deleted successfully."
        )

        return redirect("book_list")

    return render(
        request,
        "library/delete_book.html",
        {
            "book": book
        }
    )