# AutoDetector

Create a custom computer vision model from any dataset.

## Getting Started

Download and install `Docker` from here: https://docs.docker.com/get-docker/.

**Important notes For macOS users:**

- If you're on macOS, click on the Apple icon  top left -> `About This Mac`. If you see "...Intel" under the `processor` field, then download "Mac with Intel chip". If you see "Apple M1" under the `Chip` field, then download "Mac with Apple chip".


When the installation is complete, open `Docker` under the `Applications` folder. Close the Docker window, we don't need it. Docker is now running the background (on macOS: docker icon should appear in the menu bar). Wait for a minute or two, then follow the instructions below according to your operating system.

### macOS

Under `Applications` -> `Utilities`, open `Terminal`. Then copy and run the following lines:

#### Step 1: Clone the repository

```sh
cd ~/Desktop  # If you want to clone to your Desktop

git clone https://github.com/Alyetama/AutoDetector.git
cd AutoDetector
```

#### Step 2: Run the convenience script

Run the two lines below and answer any prompts. At the end of the script, you will see a message that contains the URLs and credentials for your Label-studio and cloud storage application. Bookmark the URLs and save the credentials in a safe place.

```sh
chmod +x init-darwin.zsh
./init-darwin.zsh
```

---

### Linux

Coming soon...

---

### Windows

Coming soon...
