import logging
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ECS:

    def __init__(self, identifier, region):
        self.__identifier = identifier
        self.__region = region


    def list_services(self):
        client = boto3.client('ecs', region_name=self.__region)
        services = client.list_services(cluster=self.__identifier, maxResults=100)
        return services.get("serviceArns", None)


    def start_resource(self):
        client = boto3.client('ecs', region_name=self.__region)
        list_services = self.list_services()
        for service in list_services:
            client.update_service(
                cluster=self.__identifier,
                service=service,
                desiredCount=1,
            )


    def stop_resource(self):
        client = boto3.client('ecs', region_name=self.__region)
        list_services = self.list_services()
        for service in list_services:
            client.update_service(
                cluster=self.__identifier,
                service=service,
                desiredCount=0,
            )



class RDS:
    def __init__(self, identifier, region):
        self.__identifier = identifier
        self.__region = region


    def get_dbinstance_status(self):
        session = boto3.Session()
        rds_client = session.client('rds', region_name=self.__region)
        response = rds_client.describe_db_instances(
            DBInstanceIdentifier=self.__identifier
        )
        self.__status = response["DBInstances"][0]["DBInstanceStatus"]
        return self.__status



    def start_resource(self):
        if self.get_dbinstance_status() == "stopped":
            session = boto3.Session()
            rds_client = session.client('rds', region_name=self.__region)
            response = rds_client.start_db_instance(
                DBInstanceIdentifier=self.__identifier
            )


    def stop_resource(self):
        if self.get_dbinstance_status() == "available":
            session = boto3.Session()
            rds_client = session.client('rds', region_name=self.__region)
            response = rds_client.stop_db_instance(
                DBInstanceIdentifier=self.__identifier
            )



def handler(event, context):

    try:

        print(f"EVENT Payload >>>>> {json.dumps(event, indent=4)}")

        action = event.get("action", None)
        print(f"ACTION >>>>> {action}")

        for current_resource in event.get("resources", None):

            service = current_resource.get("service", None)
            identifier = current_resource.get("identifier", None)
            region = current_resource.get("region", None)

            print(f"SERVICE >>>>> {service}")
            print(f"IDENTIFIER >>>>> {identifier}")
            print(f"REGION >>>>> {region}")

            if service is not None and action is not None and identifier is not None and region is not None:

                if service == "ecs":
                    resource = ECS(identifier, region)
                elif service == "rds":
                    resource = RDS(identifier, region)

                if action == "start":
                    resource.start_resource()

                elif action == "stop":
                    resource.stop_resource()



    except Exception as e:
        print(e)