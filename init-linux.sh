#!/bin/bash

keyboard_interrupt() {
  printf "\nReset database (y/n)? "
  read -r RESET_DB
  if [[ $RESET_DB = 'y' ]]; then
    docker compose down
    rm -rf postgres-data
  fi
  exit 1
}

trap keyboard_interrupt SIGINT

# -----------------------------------------------------------------------------

if ! [ -x "$(command -v docker)" ]; then
  echo 'ERROR: docker is not installed!' >&2
  exit 1
fi

# -----------------------------------------------------------------------------

printf "\nEmail address: "
read -r USER_EMAIL_ADDRESS
echo "USER_EMAIL_ADDRESS=$USER_EMAIL_ADDRESS" >> .env
export USER_EMAIL_ADDRESS="$USER_EMAIL_ADDRESS"


printf "\nBe patient. This may take a while..."
echo "Don't close this window."
echo "If prompted for a password, use your computer's password."

sleep 10

# -----------------------------------------------------------------------------

python3 -V
pip3 install requests python-dotenv

# -----------------------------------------------------------------------------

if ! [ -f 'words' ]; then
  tar -xvf words.tgz
fi

if [ ! -d ./deploy ]; then
  git clone --depth 1 https://github.com/heartexlabs/label-studio.git
  mv label-studio/deploy .
  rm -rf label-studio
fi

# -----------------------------------------------------------------------------

python3 create_env.py || exit 1
set -o allexport; source '.env'; set +o allexport

# -----------------------------------------------------------------------------

mkdir -p buckets/images buckets/api buckets/tables \
  buckets/public buckets/datasets buckets/models buckets/logs \
  buckets/.minio.sys
chmod -R 770 buckets

mkdir drop-images-here
chmod -R 770 drop-images-here

# -----------------------------------------------------------------------------

docker compose up -d

echo 'Waiting for Label-Studio to start... This may take few minutes.'
until docker compose logs app -t | grep 'Starting development server at' > /dev/null; do
  sleep 1
done
echo 'Ready!'

# -----------------------------------------------------------------------------

LABEL_STUDIO_CREDS="
====================================================
          🚨 Label Studio Credentials 🚨
====================================================
👥 USERNAME:  $LABEL_STUDIO_USERNAME
🔐 PASSWORD:  $LABEL_STUDIO_PASSWORD

🚀 Login page:  ${LABEL_STUDIO_HOST}/user/login/
===================================================="
echo
printf '\033[0;36m%s\033[0m\n' "$LABEL_STUDIO_CREDS"


printf "Follow the steps below to authenticate to Label-Studio API:
    1. Login to Label-Studio using the USERNAME and PASSWORD above (login page: %s)
    2. After you log in, click the user icon in the upper right.
    2. Click Account & Settings.
    3. Copy the access token.
    4. Paste the access token in the line below, then hit ENTER (note: the input field is not visible)." "${LABEL_STUDIO_HOST}/user/login/"

printf "\nAccess token: "
until [[ $LABEL_STUDIO_TOKEN != '' ]]; do
  read -rs LABEL_STUDIO_TOKEN
done
export LABEL_STUDIO_TOKEN="$LABEL_STUDIO_TOKEN"
printf "\nLABEL_STUDIO_TOKEN=%s\n" "$LABEL_STUDIO_TOKEN" >> .env

printf "\n\nFinished setting up label-studio's API!"
sleep 5

# -----------------------------------------------------------------------------

S3_CREDS="
====================================================
              🚨 MinIO Credentials 🚨
====================================================
👥 USERNAME:  $S3_ROOT_USER
🔐 PASSWORD:  $S3_ROOT_PASSWORD

🚀 Login page:  ${S3_BROWSER_REDIRECT_URL}/login
===================================================="
echo
printf '\033[0;32m%s\033[0m\n' "$S3_CREDS"


printf "Follow the steps below to authenticate to MinIO's API:
    1. Visit the login page: %s
    2. Use the credentials above to log in.
    3. Then, visit: %s/identity/account/new-account
    4. Click on 'Create'.
    5. Copy the Access and Secret Key, then paste them below." "${S3_BROWSER_REDIRECT_URL}" "${S3_BROWSER_REDIRECT_URL}"

printf "\nAccess Key: "
until [[ $S3_ACCESS_KEY != '' ]]; do
  read -r S3_ACCESS_KEY
done
echo "S3_ACCESS_KEY=$S3_ACCESS_KEY" >> .env

printf "\nSecret Key: "
until [[ $S3_SECRET_KEY != '' ]]; do
  read -rs S3_SECRET_KEY
done
echo "S3_SECRET_KEY=$S3_SECRET_KEY" >> .env

printf "\n\n"

# -----------------------------------------------------------------------------

python3 add_new_project.py

# -----------------------------------------------------------------------------

exit 0
