'''
This code expects to be triggered by a CodeCommit push. 
It also expects the trigger to pass a customData string of the format "{bitriseAppSlug}:{bitriseApiToken}"
containing the credentials to use to build the Bitrise API endpoint URL to hit.

The above conditions given, this code will take the CodeCommit event and transform it
into JSON mimicking a GitHub push event, and then hit the proper Bitrise API
endpoint to trigger a build of the correct repo.
'''

import json
import urllib2
import boto3

codecommit = boto3.client('codecommit')

def lambda_handler(event, context):
    appSlug, apiToken = event['Records'][0]['customData'].split(':')
    endpoint = "https://hooks.bitrise.io/h/github/{0}/{1}".format(appSlug, apiToken)
    repository = event['Records'][0]['eventSourceARN'].split(':')[5]
    references = [reference for reference in event['Records'][0]['codecommit']['references'] ]

    for r in references:
        ref = r["ref"]
        commitId = r["commit"]
        commit = codecommit.get_commit(repositoryName=repository, commitId=commitId)
        message = commit['commit']['message']
        
        print("Triggering Bitrise build for ref {0} of repository {1}".format(ref, repository))
        print("at commit {0} -- {1}".format(commitId, message))

        # Format of the JSON payload we want to shoot at the Bitrise endpoint:
        # {
        #   "ref": "refs/heads/master",
        #   "deleted": false,
        #   "head_commit": {
        #       "distinct": true,
        #       "id": "83b86e5f286f546dc5a4a58db66ceef44460c85e",
        #       "message": "re-structuring Hook Providers, with added tests"
        #   }
        # }

        payload = {}
        payload['ref'] = ref
        payload['deleted'] = False
        payload['head_commit'] = {}
        payload['head_commit']['distinct'] = True
        payload['head_commit']['id'] = commitId
        payload['head_commit']['message'] = message
        
        req = urllib2.Request(endpoint)
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-Github-Event', 'push')
        response = urllib2.urlopen(req, json.dumps(payload))
# end lambda_handler
