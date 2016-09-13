Integrating AWS CodeCommit with Bitrise
=======================================

1) Setting up/Connecting a Repository
  * If you store your source code on AWS CodeCommit, and you want to start using the Bitrise CI platform, 
  this setup can seem daunting (and even impossible). Connecting an AWS CodeCommit repository is probably the most complicated part of using Bitrise, 
  but it's not hard to do, and once its done, CodeCommit behaves just about like any other popular hosted source control service.
  * Here's how to connect a repo (assuming you don't already have a keypair)
    1) Create an IAM user specifically for Bitrise CodeCommit access (make sure it has the proper CodeCommit permissions).
    1) Start the "Add an App" process, and under "Connect your repository," select "Own/Manual."
    1) Input a repo URL (it doesn't actually matter what it is at this point, as long as it's a valid SSH URL).
    1) Select "Automatic" for SSH key, so that Bitrise generates a keypair for you, and copy the generated public key; 
    attach this public key to the user created in step 1, and take note of the SSH Key ID.
    1) Now copy the generated _private_ key and store it somewhere safe.
    1) Next, click "Restart" at the top of the page to start this process over (I know... trust me).
    1) This time around, select "Other/Manual" again for the repo type, and input the SSH URL to your repo 
    in the form of "ssh://{SSH_KEY_ID}@{REPO_URL}". 
        * Here, {SSH_KEY_ID} is the ID of the key you attached the IAM user we mentioned earlier, and
        {REPO_URL} is the SSH clone URL of your repository (minus the "ssh://" prefix). 
    1) Next, click "Add Own SSH" and paste in the SSH private key from before (you did save that somewhere _safe_, didn't you?).
    1) Now Bitrise will validate your repo, and you should be good to go!
  * The good part: if you have multiple repositories to connect to Bitrise, you can use the _same_ keypair for all of them, 
  if you wish, so you don't have to go through this backtracking process for every repository.
  * If you _do_ already have a keypair handy that you want to use for Bitrise integration, just start at step 7.
2) Triggering a build on push
  * One of the downsides to using AWS CodeCommit is that it does not provide a native webhook mechanism 
  like what you get with GitHub or other popular hosted source control providers.
  * On the other hand, given that CodeCommit is part of the AWS ecosystem, we have an arsenal of handy tools and services
  that can be combined to implement just about any functionality we desire around our repositories.
  * Thus, at TicketBiscuit we have come up with a simple mechanism that gives us basic webhook functionality -- 
  and thus allows us to trigger Bitrise builds automatically on a push to one of our mobile app repositories.
  * The three key parts of this mechanism are the CodeCommit repo, a Lambda function (written in Python), and the Bitrise API.
  * The mechanism works as follows:
    * We have written an AWS Lambda function that, when triggered by a CodeCommit event, 
    parses the event and converts it into the form of a GitHub webhook push event -- 
    this is something the Bitrise API can easily digest (the code for this function can be found [here](https://github.com/dmarklein/AWSCodeCommitBitrise)) .
    * The CodeCommit trigger is also responsible for passing the correct app slug and API token 
    to the Lambda function -- this way the Lambda function is sure to trigger the right build.
      * This is passed via the CustomData of the trigger, in the format "{APP_SLUG}:{API_TOKEN}" -- 
      these values come from the "Code" tab of your build job in Bitrise.
    * As you could guess, once the parsing is done, the Lambda function POSTs the resultant JSON
    to the proper Bitrise endpoint, and we our mobile app build is off and running.
  * Gotchas:
    * As with anything within the AWS ecosystem, permissions and policies are important. 
    Not only does your Lambda function need permission to access each CodeCommit repo you want to integrate,
    each of the CodeCommit repo's needs permission to trigger the Lambda function.
    * You _probably_ want to read [this doc](http://docs.aws.amazon.com/codecommit/latest/userguide/how-to-notify-lambda.html) thoroughly before trying to implement this in your own system.
