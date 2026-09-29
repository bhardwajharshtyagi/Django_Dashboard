from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):

    def clean(self, data, initial=None):

        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files = []

        for file in data:
            cleaned_files.append(
                super().clean(file, initial)
            )

        return cleaned_files


class UploadFileForm(forms.Form):

    files = MultipleFileField(
        widget=MultipleFileInput(
            attrs={
                "class": "form-control",
                "multiple": True,

                # All supported file types
                "accept": (
                    ".jpg,.jpeg,.png,.gif,"
                    ".pdf,"
                    ".xls,.xlsx,"
                    ".csv"
                ),
            }
        )
    )