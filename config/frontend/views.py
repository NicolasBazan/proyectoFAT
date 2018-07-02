# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.conf import settings
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from controlAsistencia.models import *
from django.contrib.auth.models import User
from controlAsistencia.forms import *
import datetime
from datetime import timedelta
from django.core.mail import send_mail
from reportlab.pdfgen import canvas


# Create your views here.
def main(request):
	results={}
	try:
		preceptor = Preceptor.objects.get(user=request.user)
		results['years'] = preceptor.getYear()
		return render(request, 'main.html', results)
	except:
		return render(request, 'main.html')

def prueba(request):
	 return render(request, 'prueba.html')

def list_render(request, id):
	results={}
	year = Year.objects.get(id=id)
	results['students'] = year.getStudents()
	return render(request, 'asistencia_lista.html', results)

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('main')
		else:
			return render(request, 'index.html')


def logout_user(request):
	logout(request)
	return redirect('/')

def register_user(request):
	if request.method == "POST":
		form = PreceptorForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		sec_pass = request.POST['sec_password']
		email = request.POST['email']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		if form.is_valid():	
			if password == sec_pass:
				try :
					User.objects.get(username = username)
				except User.DoesNotExist:
					user = User.objects.create_user(username, email, password)
					user.is_active = True
					user.first_name = first_name
					user.last_name = last_name
					user.save()
					internal_tel= form.cleaned_data.get("internal_tel")
					year= form.cleaned_data.get("year")
					preceptor = Preceptor(user=user,internal_tel=internal_tel)	
					preceptor.save()
					for i in year:
						preceptor.year.add(i)
				return redirect('/')
	else:
		form = PreceptorForm()
	return render(request, 'register.html', {'form': form})

def ausente(request):
	if request.method == "POST":
		today_date = datetime.date.today()
		today_time = datetime.datetime.now().time()
		preceptor = Preceptor.objects.get(user=request.user)
		student = Student.objects.get(dni=request.POST['student'])
		year= Student.objects.get(dni=request.POST['student']).year
		try:
			Absence.objects.get(date=today_date, preceptor=preceptor, year=year,student=student)
		except Absence.DoesNotExist:
			absence=Absence.objects.create(date=today_date,time=today_time, preceptor=preceptor, year=year, student=student, percentage=1, origin=0)
	return HttpResponse("ok")

def create_student(request):
	if request.method == "POST":
		form = StudentForm(request.POST)
		if form.is_valid():
			first_name= form.cleaned_data.get("first_name")
			last_name= form.cleaned_data.get("last_name")
			student_tag= form.cleaned_data.get("student_tag")
			list_number= form.cleaned_data.get("list_number")
			birthday= form.cleaned_data.get("birthday")
			address= form.cleaned_data.get("address")
			dni= form.cleaned_data.get("dni")
			neighbourhood= form.cleaned_data.get("neighbourhood")
			city= form.cleaned_data.get("city")
			yearqs= form.cleaned_data.get("year")
			status= form.cleaned_data.get("status")
			food_obvs= form.cleaned_data.get("food_obvs")
			year= Year.objects.get(id=yearqs)
			try: 
				Student.objects.get(dni=dni)
			except Student.DoesNotExist:
				student = Student(first_name = first_name ,last_name = last_name, dni=dni , student_tag=student_tag ,list_number=list_number, birthday=birthday, address=address, neighbourhood=neighbourhood, year=year,city=city,status=status, food_obvs=food_obvs)
				student.save()
		return redirect('/')
	else:
		form = StudentForm()
	return render(request, 'create_student.html', {'form': form})

def index(request):
	return render(request, 'index.html')

def manage(request):
	return render(request, 'manage.html')

def update_preceptor(request):
	if request.method == "POST":
		form = PreceptorUpdateForm(request.POST)
		if form.is_valid():
			years=[]
			internal_tel= form.cleaned_data.get("internal_tel")
			year= form.cleaned_data.get("year")	
			preceptor_id= form.cleaned_data.get("preceptor_id")
			preceptor=Preceptor.objects.filter(id=preceptor_id)
			preceptor_year=Preceptor.objects.get(id=preceptor_id)
			preceptor_year.year.clear()
			# if request.POST["username"]!= preceptor_year.user.username: probar performance
			preceptor_year.user.username = request.POST["username"]
			preceptor_year.user.first_name = request.POST["first_name"]
			preceptor_year.user.last_name = request.POST["last_name"]
			preceptor_year.user.email = request.POST["email"]
			preceptor_year.user.save()

			for i in year:
				preceptor_year.year.add(i)
			preceptor.update(internal_tel=internal_tel)
		return redirect('/')
	else:
		years = []
		results= {}
		id=request.GET.get('preceptor')
		results["id"] = id
		preceptor = Preceptor.objects.get(id=id)
		results["username"]= preceptor.user.username
		results["first_name"]= preceptor.user.first_name
		results["last_name"]= preceptor.user.last_name
		results["email"]= preceptor.user.email
		qs_year = preceptor.getYearid()
		for i in qs_year:
			years.append(i)
		form = PreceptorUpdateForm(initial={'preceptor_id':id,'internal_tel':preceptor.internal_tel, 'year':years})
		results["form"]= form
	return render(request,'update_preceptor.html', results)

def preceptor_list(request):
	preceptors=Preceptor.objects.all()
	return render(request,'preceptor_list.html',{ 'preceptors':preceptors })

def student_list(request):
	students=Student.objects.all().order_by('birthday','last_name','first_name')
	return render(request,'student_list.html',{ 'students':students })

def update_student(request):
	if request.method == "POST":
		form = StudentForm(request.POST)
		if form.is_valid():
			first_name= form.cleaned_data.get("first_name")
			dni= form.cleaned_data.get("dni")
			student=Student.objects.filter(dni=dni)
			last_name= form.cleaned_data.get("last_name")
			student_tag= form.cleaned_data.get("student_tag")
			list_number= form.cleaned_data.get("list_number")
			birthday= form.cleaned_data.get("birthday")
			address= form.cleaned_data.get("address")
			neighbourhood= form.cleaned_data.get("neighbourhood")
			city= form.cleaned_data.get("city")
			year= form.cleaned_data.get("year")
			status= form.cleaned_data.get("status")
			food_obvs= form.cleaned_data.get("food_obvs")
			student.update(first_name=first_name, last_name=last_name, student_tag=student_tag, list_number=list_number, birthday=birthday, address=address, neighbourhood=neighbourhood, city=city, year=year, status=status, food_obvs=food_obvs)
		return redirect('/')
	else:
		results= {}
		dni=request.GET.get('student')
		results["dni"] = dni
		student = Student.objects.get(dni=dni)
		age = student.getAge()
		form = StudentForm(initial={'first_name':student.first_name, 'last_name':student.last_name, 'dni':student.dni, 'student_tag':student.student_tag, 'list_number':student.list_number, 'birthday':student.birthday, 'address':student.address, 'neighbourhood':student.neighbourhood, 'city':student.city, 'year':student.year.id, 'status':student.status,'food_obvs':student.food_obvs})
		results["form"]= form
	return render(request,'update_student.html', results)

def late_arrival(request):
	if request.method == "POST":
		absence_time = Absence.objects.get(id=request.POST['absence'])
		""" PARA FUTURO CALCULO DE FALTAS

		print "dia falta "+ str(absence_time.date)
		print "hoy dia"+ str(datetime.date.today())
		print "hora falta "+ str(absence_time.time)
		print "hoy hora "+ str(datetime.datetime.now().time())
		a = datetime.datetime.now().time()- absence_time.time
		print "dif" + str(a)
		"""
		absence_q = Absence.objects.filter(id=request.POST['absence'])

		now = datetime.datetime.now().time()
		a9am = now.replace(hour=9, minute= 0 , second= 0) 
		a10_30am = now.replace(hour=10, minute= 30 , second= 0) 
		a12am = now.replace(hour=12, minute= 0 , second= 0) 
		a15am = now.replace(hour=15, minute= 0 , second= 0) 

		if now > a15am:
			absence_q.update(percentage=1)
			
		elif now > a12am:
			absence_q.update(percentage=0.75)

		elif now > a10_30am:
			absence_q.update(percentage=0.5)

		elif now > a9am:
			absence_q.update(percentage=0.25)

		
	return HttpResponse("hola")

def late_render(request, id):
	results={}
	year = Year.objects.get(id=id)
	preceptor = Preceptor.objects.get(user=request.user)
	students = year.getStudents()
	today_date = datetime.date.today()
	absences = Absence.objects.filter(date=today_date, preceptor=preceptor, year=year).order_by('student__last_name','student__first_name')
	results['absences']= absences
	return render(request, 'llegada_tarde.html', results)

def early_retirement(request):
	if request.method == "POST":
		student = Student.objects.get(dni=request.POST['student'])
		year = Year.objects.get(id=student.year.id)
		preceptor = Preceptor.objects.get(user = request.user)
		today_date = datetime.date.today()
		now = datetime.datetime.now().time()
		a9am = now.replace(hour=9, minute= 0 , second= 0) 
		a12_30am = now.replace(hour=12, minute= 30 , second= 0) 
		a15_20am = now.replace(hour=15, minute= 20 , second= 0) 

		if now < a9am:
			Absence.objects.create(percentage=0.75,student=student,origin=2,date=today_date,time=now,preceptor=preceptor,year=year)
			
		elif now < a12_30am:
			Absence.objects.create(percentage=0.50,student=student,origin=2,date=today_date,time=now,preceptor=preceptor,year=year)

		elif now < a15_20am:
			Absence.objects.create(percentage=0.25,student=student,origin=2,date=today_date,time=now,preceptor=preceptor,year=year)

		
	return HttpResponse("hola")

def early_render(request, id):
	results={}
	ausentes = []
	presentes=[]
	today_date = datetime.date.today()
	year = Year.objects.get(id=id)
	preceptor = Preceptor.objects.get(user=request.user)
	students = year.getStudents()
	faltas = Absence.objects.filter(date = today_date , percentage=1, student__year=year)
	for i in faltas:
		ausentes.append(i.student)

	for i in students:
		for j in ausentes:
			if i!=j:
				presentes.append(i)
	results['students']= presentes
	return render(request, 'retiro_anticipado.html', results)

def justification_render(request, id):
	results={}
	year = Year.objects.get(id=id)
	if request.user.is_staff:
		absences = Absence.objects.filter(year=year).order_by('date')
		results['absences']= absences
		return render(request, 'justificar_falta.html', results)
	else:	
		today_date = datetime.date.today()
		n = 2
		fecha = today_date - timedelta(days=n)
		print fecha
		absences = Absence.objects.filter(year=year,date__gte=fecha).order_by('date')
		results['absences']= absences
		return render(request, 'justificar_falta.html', results)


def justify(request):
		absence_q = Absence.objects.filter(id=request.POST['absence'])
		absence_q.update(justified=True)
		return HttpResponse("okk")

def send_email(request):
	send_mail('probando', 'email test', 'test.asistencia@gmail.com', ['nikobazan@gmail.com',])
	return HttpResponse("se mando")

def pdf(request):
	response = HttpResponse(content_type='controlAsistencia/pdf')
	response['Content-Disposition'] = 'inline; filename="test.pdf"'
	p = canvas.Canvas(response)
	p.drawString(100, 100, "Hello world.")
	p.showPage()
	p.save()
	return response
