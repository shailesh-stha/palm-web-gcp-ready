# Build and deploy in Google cloud platform (GCP)
## Command to build the application. PLease remeber to change the project name and application name
gcloud builds submit --tag gcr.io/palm-web-407908/palm-web --project=palm-web-407908

## Command to deploy the application
gcloud run deploy --image gcr.io/palm-web-407908/palm-web --platform managed --project=palm-web-407908 --region=europe-west3 --allow-unauthenticated

# Regions: https://cloud.google.com/run/docs/locations?_ga=2.160369341.-1826852978.1702288551&_gac=1.189908825.1702375924.CjwKCAiApuCrBhAuEiwA8VJ6JuDO3ELKmGZtDP8ie_0cNxkuAeO2XS0WXpMTxgjLuPEoBKxLGmiqExoCJiAQAvD_BwE
# Europe-west3: Frankfurt, Germany (19)