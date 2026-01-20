import boto3
from botocore.exceptions import ClientError
from abc import ABC, abstractmethod
dynamodb = boto3.resource("dynamodb")
class Database(ABC):
    @abstractmethod
    def get_user(self, email: str):
        pass

    @abstractmethod
    def create_user(self, email: str, hashed_password: str):
        pass

class DynamoDB(Database):
    def __init__(self, table_name: str):
        self.table = dynamodb.Table(table_name)

    def get_user(self, email: str):
        try:
            response = self.table.get_item(Key={"email": email})
            return response.get("Item")
        except ClientError as e:
            print(f"Error getting user: {e.response['Error']['Message']}")
            return None

    def create_user(self, email: str, hashed_password: str):
        try:
            self.table.put_item(Item={"email": email, "hashed_password": hashed_password})
            return True
        except ClientError as e:
            print(f"Error creating user: {e.response['Error']['Message']}")
            return False