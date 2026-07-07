from django import forms
from .models import Book, CirculationRecord


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "isbn",
            "genre",
            "total_copies",
            "available_copies",
            "cover_url",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "author": forms.Select(
                attrs={"class": "form-select"}
            ),
            "isbn": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "genre": forms.Select(
                attrs={"class": "form-select"}
            ),
            "total_copies": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "available_copies": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "cover_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/book.jpg"
                }
            ),
        }


class BookIssueForm(forms.ModelForm):

    class Meta:
        model = CirculationRecord
        fields = ["book", "member"]

        widgets = {
            "book": forms.Select(
                attrs={"class": "form-select"}
            ),
            "member": forms.Select(
                attrs={"class": "form-select"}
            ),
        }


class BookReturnForm(forms.ModelForm):

    class Meta:
        model = CirculationRecord
        fields = ["book", "member"]

        widgets = {
            "book": forms.Select(
                attrs={"class": "form-select"}
            ),
            "member": forms.Select(
                attrs={"class": "form-select"}
            ),
        }