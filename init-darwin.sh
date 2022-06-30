#!/bin/bash

if ! [ "$(uname)" == "Darwin" ]; then
  echo 'ERROR: Not running on macOS!'
  exit 1
fi

if ! [ -x "$(command -v docker)" ]; then
  echo 'ERROR: docker is not installed!' >&2
  exit 1
fi

echo 'Be patient. This may take a while...'
echo "Don't close this window."

sleep 10

if ! [ -x "$(command -v brew)" ]; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

brew install git curl wget netcat
brew install miniforge
brew install --cask tailscale
brew install tailscale

source "$HOME/miniforge3/bin/activate"
conda init
# shellcheck disable=SC2046
conda init $(basename "$SHELL")
source "$HOME/.zshrc"
python -V

pip install requests python-dotenv

# -----------------------------------------------------------------------------

open '/Applications/Tailscale.app'

echo 'Accept the access prompt, then make sure to enable tailscale extension:
  1. Open your system Settings.
  2. Go to Security & Privacy -> General.
  3. Click on the "Open Anyway" button.
  4. Accept the VPN access prompt.'

echo -e "\n\e[36mThe sign up page will open in your browser Then, select:\e[0m"
echo -e "[[  \e[31mSign up with GitHub\e[0m  ]]\n"
sleep 5
open 'https://login.tailscale.com/start'

echo 'Click on tailscale logo in the system menubar, then select: log in...'
open '/Applications/Tailscale.app'

TAILSCALE_IP=$(tailscale ip --4)
export TAILSCALE_IP="$TAILSCALE_IP"
echo "export TAILSCALE_IP=$TAILSCALE_IP" >> "$HOME/.zshrc"
echo "TAILSCALE_IP=$TAILSCALE_IP" >> .env

# -----------------------------------------------------------------------------

git clone --depth 1 https://github.com/heartexlabs/label-studio.git
mv label-studio/deploy .
rm -rf label-studio

python create_env.py
set -o allexport; source '.env'; set +o allexport

docker compose up -d

echo 'Waiting for Label-Studio to start...'
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

🚀 Login page:  ${LABEL_STUDIO_HOST}:${LABEL_STUDIO_PORT}/user/login/
====================================================\n"
printf '\033[0;36m%s\033[0m\n' "$LABEL_STUDIO_CREDS"


printf "Follow the steps below to authenticate to Label-Studio API:
    1. Login to Label-Studio: %s
    2. After you log in, click the user icon in the upper right.
    2. Click Account & Settings.
    3. Copy the access token.
    4. Paste the access token in the line below, then hit ENTER (note: the input field is not visible).
Access token: " "${LABEL_STUDIO_HOST}:${LABEL_STUDIO_PORT}/user/login/"
read -rs LABEL_STUDIO_TOKEN

export LABEL_STUDIO_TOKEN="$LABEL_STUDIO_TOKEN"
printf "\nLABEL_STUDIO_TOKEN=%s\n" "$LABEL_STUDIO_TOKEN" >> .env


# -----------------------------------------------------------------------------

MINIO_CREDS="
====================================================
              🚨 MinIO Credentials 🚨
====================================================
👥 USERNAME:  $MINIO_ROOT_USER
🔐 PASSWORD:  $MINIO_ROOT_PASSWORD

🚀 Login page:  ${MINIO_BROWSER_REDIRECT_URL}/login
====================================================\n"
printf '\033[0;32m%s\033[0m\n' "$MINIO_CREDS"


echo "Now visit MinIO login page and use your credentials to log in.
Then, visit: ${MINIO_BROWSER_REDIRECT_URL}/identity/account/new-account
and click on 'Create'. Copy the Access and Secret Key, then paste them below."

printf "\nAccess Key: "
read -rs MINIO_ACCESS_KEY
echo "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" >> .env

printf "\nSecret Key: "
read -rs MINIO_SECRET_KEY
echo "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" >> .env

# -----------------------------------------------------------------------------

python add_new_project.py

mkdir -p buckets/images buckets/api buckets/tables \
  buckets/public buckets/datasets buckets/models buckets/logs

exit 0
