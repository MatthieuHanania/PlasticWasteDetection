from datetime import datetime
from django import template
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import context, loader
from django.template.base import Template
from django.urls import reverse
from object_detection.utils import visualization_utils as viz_utils

import os
import numpy as np
from six import BytesIO

import tensorflow as tf

import PIL.Image as pimg
import PIL.ExifTags

from .models import pointGPS

#'C:/Users/nil75/Desktop/prog/django/projet/dataction/inference_graph/saved_model'
detect_fn = tf.saved_model.load(os.path.abspath("inference_graph/saved_model"))

def home(request):
    return render(request,'home.html',{})

def submit(request):
    return render(request,'submit.html',{})

def point_index(request):
    point_list = pointGPS.objects.all()

    return render(request,'point_index.html',{"point_list":point_list})

def consigne(request):
    return render(request,"consigne.html")


#pour l'instant tout est dans test
def treatment(request):
    try:
        doc = request.POST['document']
    except:
        # Redisplay the question voting form.
        return HttpResponse("c'est rapé")

    else:
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponse(type(doc))



def test(request):
    try:
        doc = request.POST['document']
    except:
        # Redisplay the question voting form.
        return render(request,'submit.html',{"error": "erreur loes de la soumission du form veuillez réesayer"})
   
    #changé ça
    #path = "C://Users//" + os.getlogin() + "//Pictures//" + doc
    path = os.path.abspath("image") +"/"+ doc

# chargement de l'image pour donné EXIF
    try:
        img = pimg.open(path)
    except:
        return render(request,'submit.html',{"error": "image non trouvé dans le répertoire " + path})

#récupération des donné EXIF et vérification
    exif_data = img._getexif()

    exif = None
    if(exif_data != None):
        exif = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in PIL.ExifTags.TAGS
        }
    else:
        return render(request,'submit.html',{"error": "l'image fournit ne contient pas de données exif est n'est donc pas recevable"})

    if(not "GPSInfo" in exif.keys()):
        return render(request,'submit.html',{"error": "l'image fournit ne contient pas de données GPS merci de vérifier que le paramètre tags de localisation de votre appareil photo de smartphone est bien activé, pour plus d'information reférez vous à la page instruction."})

#test via IA pour voir si déchet ou non

    img = load_image_into_numpy_array(path)
    input_tensor = np.expand_dims(img, 0)
    detections = detect_fn(input_tensor)

    score = detections['detection_scores'][0][0].numpy()


    category_index = {
        1: {'id': 1, 'name': 'Plastic'},
        2: {'id': 2, 'name': 'Not_Plastic'},
    }

    image_np_with_detections = img.copy()
    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'][0].numpy(),
        detections['detection_classes'][0].numpy().astype(np.int32),
        detections['detection_scores'][0].numpy(),
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=.40,
        agnostic_mode=False)

    PIL_image = pimg.fromarray(np.uint8(image_np_with_detections)).convert('RGB')
    PIL_image.show()

    if (score < 0.50):
        erreur = "aucun déchets n'a été trouvé sur votre image s'il s'agit d'une erreur essayé de prendre la photo sous un angle différent. confidence=" + str(score)
        return render(request, 'submit.html', {"error": erreur})



 #ajout du point dans la bdd
    coord = EXIF_to_MDS(exif["GPSInfo"])
    lat, long = MDS_to_latlong(coord)

    date = exif["DateTimeOriginal"].split(":")
    date = datetime(int(date[0]),int(date[1]),int(date[2][0:2]),int(date[2][3:]),int(date[3]),int(date[4]))
    
    new_point = pointGPS(coord=coord,lat=lat,long=long,shot_date=date,clean_state=False)
    new_point.save()

#affichage de la page de détail du point ajouté
    return HttpResponseRedirect(reverse('dataction:detail',args=(new_point.id,)))


def point_detail(request,point_id):
    point = get_object_or_404(pointGPS, pk=point_id)

    return render(request,'detail.html', {'point': point,"coord_integration":coord_transform(point.coord)})

def global_map(request):
    point_list = pointGPS.objects.all()

    return render(request, 'global_map.html', {"point_list": point_list})
        

'''
liste des vue:
home : page d'accueil   ->tout les autres(navbar)
submit : soumettre image    -> point_detail(correspondant)
point_list : tout les point GPS -> point_detail & map
point_detail : le détail d'un point -> point_list & lien maps
map : carte de tout les points  -> à voir
'''
    



#déplacer pour propreté (à validé par les test)

def coord_transform(coord):
    coord_int = coord.replace("°","%C2%B0")
    coord_int =  coord_int.replace("\"","%22")
    coord_int = coord_int.replace(" ","%20")
    return coord_int

def MDS_to_latlong(conver):
    
    conver = conver.replace("\"", "//")
    conver = conver.replace("°", "//")
    conver = conver.replace("'", "//")
    conver = conver.replace("N", "//")
    conver = conver.replace("E", "//") 
    conver = conver.replace("////", "//") 
    conver = conver.split("//")
    
    conver = conver[:-1]
    
    final = []
    for elem in conver:
        if(elem == ''):
            conver.remove(elem)
        else: 
            elem = float(elem)
        print(type(elem))
        print(elem)
        final.append(elem)
    
    lat =  final[0]+((final[1]/60)+final[2])/60
    long = final[3]+((final[4]/60)+final[5])/60
    
    return (lat,long)

def EXIF_to_MDS(GPSInfo):
    coord = ""

    coord+= str(int(GPSInfo[2][0])) + "°"
    coord+= str(int(GPSInfo[2][1])) + "'"
    coord+= str(GPSInfo[2][2]) + "\"" + GPSInfo[1] + " "

    coord+= str(int(GPSInfo[4][0])) + "°"
    coord+= str(int(GPSInfo[4][1])) + "'"
    coord+= str(GPSInfo[4][2]) + "\"" + GPSInfo[3]

    print("https://www.google.fr/maps/place/" + coord)
    return coord

def load_image_into_numpy_array(path):
 
  img_data = tf.io.gfile.GFile(path, 'rb').read()
  image = pimg.open(BytesIO(img_data))
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)