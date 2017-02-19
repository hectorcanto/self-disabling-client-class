# Goal

This module is designed for being self-disabled depending on a given variable, in this example AWS_S3_ENABLED.
Instead of checking the variable in the main application many times, it is the class itself which decides what to do.

This way we **prevent**:
- Duplicating code, by making many similar if statements all around the application
- Coupling the module from the main application, through global settings and conditionals.
- Make testing more difficult.

It was initially though for Django applications but it may be used in others frameworks or standalone. Instructions will
be provided bellow, in the section #Usage.

## Advanced notes

This approach is based on the principle _Tell don't ask_ and on polymorphism. It uses an abstract class to define
the interface and a _dummy_ class that will replace the real class when disabled - hence the polymorphism.

# Implementation and dependencies

There are 3 classes in aws_s3_dummy:
- An interface ( abstract class)
- A dummy class
- The real class

If the module is disabled - AWS_S·_ENABLED = False - it will internally instantiated as the
Dummy class. In the rest of the application we will not need to replaced

## Dependencies
There are a _requirements.txt_ file to install dependencies with pip but there are not depencies for the _dummy_ part.
- _abc_ belongs to the Python core,
- boto3 is needed for the example,
 - and the rest are needed by virtualenv but not the module itself.

## TODOs

Make the dummy class implement all the public methods in one go, saving the time of repeating the implementation for
each public method.

# Usage
## Standalone usage
Define the variables in local_config.py directly. If you miss any, it should raise a _NonImplementedError_

## Direct instantiation

We can override the imported setting by specifying _enabled_ in the class instantiation. This is useful for testing
purposes. Example:

```ClientS3(enabled=False)```

The class also accepts parameters, so the instantiation is also customizable, useful for testing purposes.

## Coupled with Django

- Copy the django_local_config.py into local_config.py
- Change the _django_app_ with your Django app module name

 This file will import all the variables from the django app settings with a given prefix. You can replace it for
 whatever you need but my recommendation is to reduce the imports to the minimum possible to minimize errors.

The way variables are imported in _django_local_config.py_ is also interesting since it limits imports to
the wanted variables and allows using the module without entering the django shell, which sometimes is _blocked_
from some other error in the code. Since the module was coupled it was unusable if it depended on the django
settings directly.

## Usage in third-party services

I use this structure for third-party services like AWS, GoogleAPI, Facebook, Firebase and others
This example is a simple interface to upload and delete files with AWS storage service S3 taking care
of some frequent errors.


