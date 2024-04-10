from chalice import Chalice
import boto3
import os
import uuid
from PIL import Image
import io
import time
app = Chalice(app_name='Attendza')

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = 'users'
table = dynamodb.Table(table_name)

# S3 bucket name
bucket_name = 'attendza-gallery2'

# Dummy database to simulate storing user data
DATABASE = {}

@app.route('/')
def index():
    return {'hello': 'world'}


def create_image_list(paths, fid):
    new_images = []
    for i in paths:
        new_images.append((i,fid))
    return new_images

@app.route('/register', methods=['POST'])
def register_face():
    try:
        request = app.current_request
        data = request.json_body
        
        faceId = data.get('FaceId')
        name = data.get('Name')
        image_paths = data.get('ImagePaths', [])
        image_list = create_image_list(image_paths, faceId)
        print('IMAGE LIST:', image_list)

        for image in image_list:
            file_path = image[0]
            with open(file_path, 'rb') as file:
                file_contents = file.read()
            
            path = image[0].split('/')[-1]
            path = path.split('\\')[-1]
            print('PATH:', path)
            s3.put_object(
                Body=file_contents,
                Bucket='attendza-gallery2',
                Key=path,
                Metadata={'FullName': image[1]}  
            )

        data_without_images = data.copy()
        data_without_images.pop("ImagePaths", None)

        dynamodb = boto3.resource('dynamodb')

        table_name = 'users'

        table = dynamodb.Table(table_name)

        table.put_item(Item=data_without_images)
        return {'status': 'success', 'user_id': faceId}
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}

import random
import datetime
def getUserData(faceId):
    # print("GET USER DATA -> FaceId: ", faceId)
    response = dynamodb_client.get_item(
        TableName='users',  
        Key={'FaceId': {'S': faceId}}
        )
    # print(response)
    return response['Item']

def create_logid(date):
    random_number = random.randint(1000, 9999)
    log_id = date + str(random_number)
    return log_id
            
def status(attn):
    count = attn['Count']
    if count == 0:
        status = 'Sign In'
    else:
        if count % 2 == 0:
            status = 'Sign In'
        else:
            status = 'Sign Out'
    return status
            
def check_attendance(face_id, date):
    response = dynamodb_client.scan(
        TableName='attendence',
        FilterExpression='#faceId = :face_id_val and #date = :date_val',
        ExpressionAttributeNames={
            '#faceId': 'faceId',
            '#date': 'date'
        },
        ExpressionAttributeValues={
            ':face_id_val': {'S': face_id},
            ':date_val': {'S': date}
                    }
                )
    return response
            
def insert_data_to_dynamoDB(data):
    dynamodb = boto3.resource('dynamodb')
    table_name = 'attendence'
    table = dynamodb.Table(table_name)
    table.put_item(Item=data)
    
@app.route('/intruder', methods=['POST'])
def intruder():
    request = app.current_request
    data = request.json_body
    image_path = data.get('Image')
    with open(image_path, 'rb') as file:
                file_contents = file.read()
    s3.put_object(
                Body=file_contents,
                Bucket='attendza-gallery-intruders',
                Key='intruder'+ str(int(time.time())) + '.jpg',
                Metadata={'FullName': 'intruder'+ str(int(time.time())) }  
            )
    
@app.route('/mark', methods=['POST'])
def mark_attendance():
    try:
        request = app.current_request
        data = request.json_body
        image_path = data.get('Image')
        # print(image_path)
        image = Image.open(image_path)
        stream = io.BytesIO()
        image.save(stream,format="JPEG")
        image_binary = stream.getvalue()
        
        response = rekognition.search_faces_by_image(
            CollectionId='attendza',
            Image={'Bytes':image_binary}                                       
        )
        # print(response)
        found = False
        final = None
        
        def found2(res):
            nonlocal found
            if len(res) > 0:
                res.sort(key=lambda x: x['Face']['Confidence'], reverse=True)
                if res[0]['Face']['Confidence'] > 90:
                    found = True
                    return res[0]
                else:
                    found = False
                    return 'Person cannot be recognized'
        
        final = found2(response['FaceMatches'])
        # print(final)
        
        if found: 
            face = dynamodb_client.get_item(
                TableName='face-data',  
                Key={'RekognitionId': {'S': final['Face']['FaceId']}}
            )
            # print('face',face)
            face_id_ki = face['Item']['FullName']['S']
            user = getUserData(face_id_ki)
            print('user',user)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            time_with_sec = datetime.datetime.now().strftime("%H:%M:%S")
            name_user = user['Name']['S']
            
            attn = check_attendance(face_id_ki,date)
            print(attn)
            attendence_one = {
                'LogId': create_logid(date), 
                'faceId': face_id_ki,
                'name': name_user,
                'time': time_with_sec,
                'date': date,
                'timestamp': timestamp,
                'status': status(attn),
            }
            insert_data_to_dynamoDB(attendence_one)
            return {'status': 'success', 'user': user}
        else:
            return {'status': 'error', 'message': 'Person not recognized'}
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}
    
if __name__ == '__main__':
    app.debug = True
    app.run()
