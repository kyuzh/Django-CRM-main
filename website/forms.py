from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Record, company_information

class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'	


# Create Add Record Form
class AddRecordForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder":"First Name", "class":"form-control"})
    )
    last_name = forms.CharField(
        required=True,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder":"Last Name", "class":"form-control"})
    )
    email = forms.CharField(
        required=True,
        label="Email",
        widget=forms.TextInput(attrs={"placeholder":"Email", "class":"form-control"})
    )
    phone = forms.CharField(
        required=True,
        label="Phone",
        widget=forms.TextInput(attrs={"placeholder":"Phone", "class":"form-control"})
    )
    address = forms.CharField(
        required=True,
        label="Address",
        widget=forms.TextInput(attrs={"placeholder":"Address", "class":"form-control"})
    )
    city = forms.CharField(
        required=True,
        label="City",
        widget=forms.TextInput(attrs={"placeholder":"City", "class":"form-control"})
    )
    state = forms.CharField(
        required=True,
        label="State",
        widget=forms.TextInput(attrs={"placeholder":"State", "class":"form-control"})
    )
    zipcode = forms.CharField(
        required=True,
        label="Zipcode",
        widget=forms.TextInput(attrs={"placeholder":"Zipcode", "class":"form-control"})
    )

    class Meta:
        model = Record
        exclude = ("user",)


class AddRecordForm_compagny_information(forms.ModelForm):
    nom_entreprise = forms.CharField(
        required=True,
        label="Nom de l'entreprise",
        widget=forms.TextInput(attrs={"placeholder":"Nom d'entreprise", "class":"form-control"})
    )
    siren = forms.CharField(
        required=True,
        label="SIREN",
        widget=forms.TextInput(attrs={"placeholder":"SIREN", "class":"form-control"})
    )
    type_entreprise = forms.CharField(
        required=True,
        label="Type d'entreprise",
        widget=forms.TextInput(attrs={"placeholder":"Type d'entreprise", "class":"form-control"})
    )
    nb_Effectif = forms.CharField(
        required=True,
        label="Nombre d'effectif",
        widget=forms.TextInput(attrs={"placeholder":"Nb Effectif", "class":"form-control"})
    )
    Chiffre_Affaire = forms.CharField(
        required=True,
        label="Chiffre d'Affaire",
        widget=forms.TextInput(attrs={"placeholder":"Chiffre d'Affaire", "class":"form-control"})
    )
    Grossiste = forms.CharField(
        required=True,
        label="Grossiste",
        widget=forms.TextInput(attrs={"placeholder":"Grossiste", "class":"form-control"})
    )

    class Meta:
        model = company_information
        exclude = ("user",)
