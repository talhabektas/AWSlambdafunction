import json
import os
import boto3
import matplotlib.pyplot as plt
import tempfile
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize AWS clients with credentials from environment
dynamodb = boto3.resource('dynamodb', 
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)
sns = boto3.client('sns', 
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)
s3 = boto3.client('s3', 
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

def generate_sample_data(current_temp, num_points=10):
    """Generate 10-hour sample data"""
    current_time = datetime.now()
    times = []
    temps = []
    
    for i in range(num_points):
        time_point = current_time - timedelta(hours=i)
        times.append(time_point)
        # Random fluctuation of ±1 degree around temperature value
        temp = current_temp + np.random.uniform(-1, 1)
        temps.append(temp)
    
    return list(reversed(times)), list(reversed(temps))

def lambda_handler(event, context):
    try:
        # Save data to DynamoDB
        table = dynamodb.Table(os.getenv('DYNAMODB_TABLE_NAME'))
        timestamp = int(datetime.now().timestamp())
        
        item = {
            'device_id': event['device_id'],
            'timestamp': timestamp,
            'sicaklik': event['sicaklik'],
            'nem': event['nem'],
            'hareket': event['hareket']
        }
        table.put_item(Item=item)

        # Alarm controls and SNS notification
        max_temperature = float(os.getenv('MAX_TEMPERATURE', 30))
        max_humidity = float(os.getenv('MAX_HUMIDITY', 70))
        
        if event['sicaklik'] > max_temperature or event['nem'] > max_humidity:
            alarm_msg = f"DEPO ALARM! Cihaz: {event['device_id']}\n"
            alarm_msg += f"Sıcaklık: {event['sicaklik']}°C\nNem: {event['nem']}%"
            
            sns.publish(
                TopicArn=os.getenv('SNS_TOPIC_ARN'),
                Message=alarm_msg,
                Subject='Depo Alarm Bildirimi'
            )

        # Create advanced chart and save to S3
        dates, temperatures = generate_sample_data(event['sicaklik'])
        
        # Set the figure dimension and style
        plt.style.use('seaborn')
        plt.figure(figsize=(12, 6))
        
        # Main graph
        plt.plot(dates, temperatures, '-o', color='#2563eb', linewidth=2, 
                markersize=6, label='Sıcaklık')
        
        # Visual develops
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.title('Depo Sıcaklık Trendi', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Zaman', labelpad=10)
        plt.ylabel('Sıcaklık (°C)', labelpad=10)
        
        # Y axis
        plt.ylim(30, 40)
        
        # X axis
        plt.gcf().autofmt_xdate()  # auto-format date labels
        
        # Legend
        plt.legend(loc='upper right')
        
        # Add device information below the graph
        info_text = f"""
        Cihaz Bilgileri:
        Device ID: {event['device_id']}
        Son Sıcaklık: {event['sicaklik']}°C
        Son Nem: {event['nem']}%
        Hareket Algılandı: {'Evet' if event['hareket'] else 'Hayır'}
        """
        plt.figtext(0.1, -0.1, info_text, fontsize=10, 
                   bbox=dict(facecolor='#dbeafe', alpha=0.5))
        
        # Save graph
        plt.tight_layout()
        with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
            plt.savefig(tmp.name, format='png', bbox_inches='tight', 
                       dpi=300, pad_inches=0.5)
            s3.upload_file(
                tmp.name, 
                os.getenv('S3_BUCKET_NAME'),
                'sicaklik_trend.png'
            )
        
        return {
            'statusCode': 200, 
            'body': 'İşlem başarılı!'
        }
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        return {
            'statusCode': 500, 
            'body': 'İşlem başarısız!'
        }