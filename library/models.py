from django.db import models
from django.utils import timezone
from datetime import timedelta


class Author(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    GENRES = [
        ('TECH', 'Computer Science & Technology'),
        ('SCI', 'Science & Mathematics'),
        ('LIT', 'Literature & Fiction'),
        ('HIST', 'History & Social Sciences'),
    ]

    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'
    )
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=10, choices=GENRES)
    total_copies = models.PositiveIntegerField(default=5)
    available_copies = models.PositiveIntegerField(default=5)
    cover_url = models.URLField(
        blank=True,
        default="https://via.placeholder.com/150x220"
    )

    def __str__(self):
        return f"{self.title} by {self.author.name}"


class Member(models.Model):
    name = models.CharField(max_length=100)
    member_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.member_id})"


class CirculationRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='borrowed_books'
    )
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    fine_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00
    )
    is_returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} -> {self.member.name} (Due: {self.due_date})"