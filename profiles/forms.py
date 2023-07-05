from django import forms

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # Render all fields except 'user', which shouldn't change
        exclude = ("user",)

    # Override default form setup
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        # 'default_' matches model
        placeholders = {
            "default_phone_number": "Phone Number",
            "default_country": "Country",
            "default_postcode": "Postal Code",
            "default_town_or_city": "Town or City",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_county": "County, state or locality",
        }

        self.fields["default_phone_number"].widget.attrs["autofocus"] = True

        for field in self.fields:
            if field != "default_country":
                if self.fields[field].required:
                    placeholder = f"{placeholders[field]} *"
                else:
                    placeholder = placeholders[field]

            # Set placeholder values
            self.fields[field].widget.attrs["placeholder"] = placeholder

            # Add class to fields
            self.fields[field].widget.attrs[
                "class"
            ] = "border-black rounded-0 profile-form-input"
            # Remove labels as placeholders are set
            self.fields[field].label = False
