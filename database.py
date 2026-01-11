import boto3
from botocore.exceptions import ClientError
from abc import ABC, abstractmethod
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("users")

class Database(ABC):
    @abstractmethod
    def get_user(self, email: str):
        pass

    @abstractmethod
    def create_user(self, email: str, hashed_password: str):
        pass

class DynamoDB(Database):
    def get_user(self, email: str):
        try:
            response = table.get_item(Key={"email": email})
            return response.get("Item")
        except ClientError as e:
            print(f"Error getting user: {e.response['Error']['Message']}")
            return None

    def create_user(self, email: str, hashed_password: str):
        try:
            table.put_item(Item={"email": email, "hashed_password": hashed_password})
            return True
        except ClientError as e:
            print(f"Error creating user: {e.response['Error']['Message']}")
            return False