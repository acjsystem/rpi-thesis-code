"""
SENT DATA
curl -X POST 127.0.0.1:8000/api/v1/assets/ -d '{"name" = "my image   ","source"="/root/images/my_image2.jpg"}' -H "Content-Type: application/json"
"""

#serializers
from django.forms import widgets
from rest_framework import serializers
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
		
#views.py:

from .serializers import AssetSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import status
from rest_framework.decorators import api_view


class AssetAdd(APIView):


    def post(self, request, format=None):
        serializer = AssetSerializer(data=request.DATA)
        print serializer.data

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		
		
		
#models.py:

class Asset(models.Model):

    key = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(_('name'), max_length=200)
    source = models.FileField(_('file'), upload_to=upload_to, storage=default_storage)

    ext = models.CharField(max_length=15, editable=False)
    type = models.PositiveIntegerField(choices=ASSET_TYPE, max_length=15, editable=False)
    size = models.PositiveIntegerField(max_length=32, default=0, editable=False)

    _file_meta = models.TextField(editable=False, null=True, blank=True)

    public = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=1)

    object_id = models.PositiveIntegerField(default=1)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True, auto_now=True)
	
	
	
#ANSWER
from rest_framework.parsers import MultiPartParser, FormParser

class AssetAdd(APIView):
    parser_classes = (MultiPartParser, FormParser,)

		def post(self, request, format=None):
		my_file = request.FILES['file_field_name']
		filename = '/tmp/myfile'
		with open(filename, 'wb+') as temp_file:
			for chunk in my_file.chunks():
				temp_file.write(chunk)

		my_saved_file = open(filename) #there you go