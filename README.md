# AWS IoT Based Warehouse Monitoring System



## 📌Project Overview

A system that monitors warehouse temperature, humidity and motion data in real-time using AWS IoT Core, sends SMS/email notifications via SNS for critical situations, and stores data in DynamoDB + S3.


## Technologies Used

-AWS IoT Core

-AWS Lambda

-Amazon DynamoDB

-Amazon SNS

-Amazon S3

-Python

## Architecture

The system architecture consists of:

1.IoT sensors publishing data to AWS IoT Core via MQTT

2.Lambda functions processing incoming data

3.DynamoDB storing sensor readings

4.SNS sending notifications when thresholds are exceeded

5.S3 storing visualization data

## 🚀 Installation & Setup

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name DepoIzlemeSistemi \
  --capabilities CAPABILITY_NAMED_IAM
```
## 2. Subscribe SNS Topic
Add your email address to the DepoAlarmlari Topic from the AWS SNS Console and confirm.

## 3.Configure IoT Device Simulator
Send test data in JSON format to depo/veri Topic.
```bash 
{
  "device_id": "TestCihaz1",
  "sicaklik": 35,
  "nem": 75,
  "hareket": false
}
```

## 🔧Development

Update Lambda Function:

Edit lambda/lambda_function.py. 

Make ZIP file and upload to AWS.


```bash 

zip lambda.zip lambda_function.py
aws lambda update-function-code --function-name DepoAlarmLambda --zip-file fileb://lambda.zip
```
## 🙌 Contribution
You can open a Pull Request for bug fixes and suggestions.

## 🌟 Thank you!

If you liked the project, you can support it by giving it a star ⭐

## 📜 Licence

MIT
