# Faux AWS
## A simple AWS IMDS and SDK endpoint emulator

Faux AWS provides a simple IMDS and SDK emulator allowing you to provide static, canned responses to IMDS queries or AWS CLI endpoint requests.

Data is provided in a directory structure with files containing verbatim responses sent back to clients. 

An example set of responses has been provided, but you will most likely want to provide your own depending on your need.

Faux AWS will look for its data directory root at `/faux-aws/data` in the docker container. Provided sample data can be overridden with a mapped volume or by extending this Docker image.

IMDS is provided under the `imds/` directory in the data root.

AWS SDK endpoints are provided under any supported directory named for the SDK endpoint. For example, EC2 is suported as `ec2/` directory in the data root.

AWS SDK responses are mapped under each service's directory as the name of the `Action` POST body argument. See http://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_Operations.html for a full list of AWS SDK actions for EC2.

The Faux AWS server starts on port 5000 bound to all interfaces (0.0.0.0). Map this port as appropriate to the host using Docker.

## How to run
* Run with python directly (requires Flask):

```
python ./faux-aws.py
```

* Run in Docker:

```
docker build -t faux-aws .
docker run -p 5000:5000 faux-aws
```

## How to use
### AWS CLI
Options:

* Provide the `--endpoint-url URL` argument to the AWS CLI command. This can be done in a variety of ways, depending on your environment. In many cases, a wrapper script placed at `/usr/local/bin/aws` that injects this argument is employed.

### IMDS
All commands to the IMDS HTTP endpoint should be redirected to the server, however it's accessed (via linked Docker container, from a host-mapped port, from the host to the continer IP via the docker0 bridge, etc.)

Options:

* Always provide a hostname in `/etc/hosts` whether testing with Faux AWS or deployed on EC2. For example, an entry of `172.17.42.1 imdshost` when running inside a Docker container (and serving Faux AWS from a host-bound port available on the docker bridge IP, whatever that may be), or `169.254.169.254 imdshost` when running on EC2. All calls would then use `http://imdshost/latest/...` as their IMDS URL.
* Change calls to IMDS when running locally to use the Faux AWS URL explicitly.

Common problems:
* Commonly, curl and wget will not use DNS when the provided hostname for a URL is formatted as an IPv4 address. Intead it will assume the hostname is an IP and skip the DNS lookup. Thus, tricks with the /etc/hosts file won't help to transparently redirect curl or wget to a new host when attempting to reach `169.254.169.254`.

### Warnings / Caveats

* This is a VERY simple service. It provides ZERO error checking, correctness guarantees, or any other structure. It is meant as a dirt-simple proxy to supply canned responses to AWS SDK calls or IMDS calls.

### Examples

#### AWS CLI to EC2 service
To use the AWS CLI EC2 commands, use a custom endpoint url with the `aws` command, as in:

```
aws cli --endpoint-url http://localhost:5000/ec2/ ec2 describe-instances
```

The Faux AWS service will provide the contents at `/faux-aws/data/ec2/DescribeInstances`.

#### IMDS service
Faux AWS emulates the IMDS layout sourced from the `/faux-aws/data/imds/` directory.

Querying the instance identity document can be done as:

```
curl http://localhost:5000/dynamic/instance-identity/document
```

The response is provided from `/faux-aws/data/imds/dynamic/instance-identity/document` file.


## TODO / Roadmap

* Add proxy support to forward calls to real AWS SDK endpoints and return their values to clients of Faux AWS. Optionally support AWS STS to map back to provided IAM credentials.
* Support filter syntax over canned data. I.e. when using `--filters ...`, filter the canned data response before returning to the client.
* Provide command-line arguments to specify data directory, server IP/port to listen on
