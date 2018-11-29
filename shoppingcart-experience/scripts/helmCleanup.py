from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
from sys import stderr

def delete_objects( api, object_type ):
  method = getattr(api, "delete_namespaced_" + object_type)
  for name in os.getenv(object_type.upper() + "S_TO_BE_DELETED", "").split(","):
    try:
      if name:
        print('Delete {} {}'.format(name, object_type))
        method(name, namespace, client.V1DeleteOptions())
    except ApiException as e:
      print('Delete {} {} failed on {}'.format(name, object_type, e if debug else e.reason), file=stderr)

#Main
try:
  debug=os.getenv("DEBUG", "false")=="true"

  config.load_incluster_config()

  coreV1Api = client.CoreV1Api()
  batchV1Api = client.BatchV1Api()

  with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as namespace_file:
      namespace = namespace_file.read()

  print("Working on {} microservice in {} namespace".format(namespace, os.getenv("MICROSERVICE_NAME", "")))
  delete_objects(batchV1Api, "job")
  delete_objects(coreV1Api, "config_map")
  delete_objects(coreV1Api, "secret")

except Exception as e:
  print("Failed on {}".format(e), file=stderr)