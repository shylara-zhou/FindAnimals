import datetime

from django.conf.global_settings import MEDIA_ROOT
from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Animals
def hello(request):
    return HttpResponse("This world is full of Love! ")
def allanimalsdata(request):
    a = Animals.objects.get(Name='Human')

    #test1 = str(a.animals_id)
    #print("NAME"+test1)
    #return HttpResponse("NAME"+test1)
    return HttpResponse("NAME"+a.animals_id)
def get_animalsdata_by_Name(request,name, *args, **kwargs):
    #name = name1.CharField(max_length=32)
    animal = Animals.objects.get(animal_Name=name)
    return render(request,'showAnimal.html',{'animal':animal})
    # return HttpResponse(animal.animals_id)
def add_animal(request,location,species,family,name, *args, **kwargs):
    time1 = datetime.datetime.now()
    animal = Animals(animal_Location=location,animal_Befinded_Date=str(time1),animal_Species=species,animal_Family=family,animal_Name=name)
    animal.save()
    return HttpResponse(animal.Name+animal.Species)

class loginView(APIView):
    def post(self,request,*args,**kwargs):
        print(request.data)
        return Response({"status":True})
    def get(self,request,*args,**kwargs):
        print(request.data)
        return Response({"status":True})


#from FindAnimals.settings import MEDIA_ROOT #导入上传文件保存路径 或 from django.conf import settings
#from app1.models import PicTest #导入图片模型类
# /show_upload
def show_upload(request):
	'''图片上传页'''
	return render(request,'../templates/load.html')

# /upload_handle
# 图上上传处理,图片2种类型：
# 小于2.5M放在内存中：<class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
# 大于2.5放在硬盘上：<class 'django.core.files.uploadedfile.TemporaryUploadedFile'>
def upload_handle(request):
    t_animal = Animals(animal_Pic=request.FILES['pic'],animal_Name='test',animal_Family='test',animal_Species='test',animal_Location='test',animal_Id='t',animal_chuqu_Date='t',animal_Befinded_Date='t')
    t_animal.save()
    return HttpResponse('ok')
	#'''图片上传处理页'''
	#【1】得到图片
#
# 	pic=request.FILES['pic']
# 	#【2】拼接图片保存路径+图片名
# 	save_path="%s/app1/%s"%(MEDIA_ROOT,pic.name)
#
# 	#【3】保存图片到指定路径，因为图片是2进制式，因此用wb，
# 	with open(save_path,'wb') as f:
# 		# pic.chunks()为图片的一系列数据，它是一一段段的，所以要用for逐个读取
# 		for content in pic.chunks():
# 			f.write(content)
#
#
# #【4】保存图片路径到数据库，此处只保存其相对上传目录的路径
# 	#Animals.objects.create(animal_pic='app1/%s'%pic.name)
#     Animals.objects.create(animal_Pic=p)
# 	#【5】别忘记返回信息
#  	return HttpResponse('上传成功，图片地址：app1/%s')





