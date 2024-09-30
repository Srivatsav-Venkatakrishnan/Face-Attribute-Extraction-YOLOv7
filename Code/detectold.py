

import cv2
import math
import argparse
from tensorflow.keras.models import load_model
import numpy as np
def highlightFace(net, frame, conf_threshold=0.7):
    frameOpencvDnn=frame.copy()
    frameHeight=frameOpencvDnn.shape[0]
    frameWidth=frameOpencvDnn.shape[1]
    blob=cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections=net.forward()
    faceBoxes=[]
    for i in range(detections.shape[2]):
        confidence=detections[0,0,i,2]
        if confidence>conf_threshold:
            x1=int(detections[0,0,i,3]*frameWidth)
            y1=int(detections[0,0,i,4]*frameHeight)
            x2=int(detections[0,0,i,5]*frameWidth)
            y2=int(detections[0,0,i,6]*frameHeight)
            faceBoxes.append([x1,y1,x2,y2])
            cv2.rectangle(frameOpencvDnn, (x1,y1), (x2,y2), (0,255,0), int(round(frameHeight/150)), 8)
    return frameOpencvDnn,faceBoxes


parser=argparse.ArgumentParser()
parser.add_argument('--image')

args=parser.parse_args()

faceProto="opencv_face_detector.pbtxt"
faceModel="opencv_face_detector_uint8.pb"
ageProto="age_deploy.prototxt"
ageModel="age_net.caffemodel"
genderProto="gender_deploy.prototxt"
genderModel="gender_net.caffemodel"
model = load_model(r"D:\Facial-Attribute-Recognition-from-face-images-main\pre trained\model_inception_facial_keypoints.h5",compile=False)#,custom_objects={"Adamw":tfa.optimizers.AdamW})


MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList=['Male','Female']
facialList = ['5_o_Clock_Shadow', 'Arched_Eyebrows', 'Attractive',
      'Bags_Under_Eyes', 'Bald', 'Bangs', 'Big_Lips', 'Big_Nose',
      'Black_Hair', 'Blond_Hair', 'Blurry', 'Brown_Hair', 'Bushy_Eyebrows',
      'Chubby', 'Double_Chin', 'Eyeglasses', 'Goatee', 'Gray_Hair',
      'Heavy_Makeup', 'High_Cheekbones', 'Male','Mouth_Slightly_Open',
      'Mustache', 'Narrow_Eyes', 'No_Beard', 'Oval_Face', 'Pale_Skin',
      'Pointy_Nose', 'Receding_Hairline', 'Rosy_Cheeks', 'Sideburns',
      'Smiling', 'Straight_Hair', 'Wavy_Hair', 'Wearing_Earrings',
      'Wearing_Hat', 'Wearing_Lipstick', 'Wearing_Necklace',
      'Wearing_Necktie', 'Young']

faceNet=cv2.dnn.readNet(faceModel,faceProto)
ageNet=cv2.dnn.readNet(ageModel,ageProto)
genderNet=cv2.dnn.readNet(genderModel,genderProto)

video=cv2.VideoCapture(args.image if args.image else 0)
padding=20
image_batch = np.zeros((1,128,128,3))

while cv2.waitKey(1)<0 :
    hasFrame,frame=video.read()
    if not hasFrame:
        cv2.waitKey()
        break
    
    resultImg,faceBoxes=highlightFace(faceNet,frame)
    if not faceBoxes:
        print("No face detected")

    for faceBox in faceBoxes:
        face=frame[max(0,faceBox[1]-padding):
                   min(faceBox[3]+padding,frame.shape[0]-1),max(0,faceBox[0]-padding)
                   :min(faceBox[2]+padding, frame.shape[1]-1)]
        
        image_batch[0] = cv2.resize(face,(128,128))/256
        output = model.predict(image_batch)
        
        blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), MODEL_MEAN_VALUES, swapRB=False)
        genderNet.setInput(blob)
        genderPreds=genderNet.forward()
        gender=genderList[genderPreds[0].argmax()]
        print(f'Gender: {gender}')

        ageNet.setInput(blob)
        agePreds=ageNet.forward()
        age=ageList[agePreds[0].argmax()]
        print(f'Age: {age[1:-1]} years')

        position0  = np.where(output[0]>0.5)[0]
        count = 25
        for i2 in range(len(position0)):
            if  "Eyeglasses" == facialList[position0[i2]]:
                print("Wearing EyeGlasses : Yes")
                cv2.putText(resultImg,"EyeGlasses :Yes", (faceBox[2],15+count),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2, cv2.LINE_AA)
            else:
                print(str(facialList[position0[i2]])+" "+str(np.round(output[0][position0[i2]],3)))
                cv2.putText(resultImg,str(facialList[position0[i2]]), (faceBox[2],15+count),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2, cv2.LINE_AA)
            count = count+15
    
    
        cv2.putText(resultImg, 'Age:'+str(age), (faceBox[2], 15+count), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2, cv2.LINE_AA)
        cv2.imshow("Detecting facial attributes", resultImg)
