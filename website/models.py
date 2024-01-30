from django.db import models


class Record(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.CharField(max_length=100)
	phone = models.CharField(max_length=15)
	address = models.CharField(max_length=100)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=50)
	zipcode = models.CharField(max_length=20)

	def __str__(self):
		return(f"{self.first_name} {self.last_name}")


class company_information(models.Model):
	# nom_entreprise, siren, type, nb_Effectif, Chiffre_d_Affaire,Grossiste
	nom_entreprise = models.CharField(max_length=50)
	siren = models.CharField(max_length=10)
	type_entreprise = models.CharField(max_length=50)
	nb_Effectif = models.CharField(max_length=20)
	Chiffre_Affaire = models.CharField(max_length=50)
	Grossiste = models.CharField(max_length=500)

	def __str__(self):
		return(f"{self.nom_entreprise}")
