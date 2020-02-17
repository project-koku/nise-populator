# nise-populator
A python application for deploying populated nise data for cloud providers


## Development

To get started developing with nise-populator first clone a local copy of the git repository:
```
git clone https://github.com/chambridge/nise-populator.git
````

This project is developed uses Pipenv. Many configuration settings can be read in from a ``.env`` file. To configure, do the following:

1. Copy `example.env` into a `.env`
2. Obtain AWS, Azure, and Insights values and update the following in your `.env`:
```
AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=AWS_SECRET_KEY

AZURE_STORAGE_ACCOUNT=AZURE_STORAGE_ACCOUNT
AZURE_STORAGE_CONNECTION_STRING=AZURE_STORAGE_CONNECTION_STRING

INSIGHTS_USER=INSIGHTS_USER
INSIGHTS_PASSWORD=INSIGHTS_PASSWORD
INSIGHTS_URL=INSIGHTS_URL
```
3. Then project dependencies and a virtual environment can be created using :
```
pipenv install --dev
```
4. To activate the virtual environment run :
```
    pipenv shell
```
5. Install the pre-commit hooks for the repository :
```
pre-commit install
```

## Deploying to OpenShift

The `nise-populator` runs as a *CronJob* on OpenShift creating data daily. You can deploy it to OpenShift as follows:

1. Login to OpenShift
```
oc login
```

2. Select your project
```
oc project koku
```
3. Create OpenShift resources
```
oc create -f openshift/ | oc apply
```
