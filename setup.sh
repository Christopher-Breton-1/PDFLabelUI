#!/bin/bash

## Do not use this file. Not useful
# define repo URLs and folder names
repos=(
  "https://github.com/Christopher-Breton-1/PDFLabelUIBackend.git backend"
  "https://github.com/Christopher-Breton-1/PDFLabelUIFrontend.git frontend"
  "https://github.com/Christopher-Breton-1/pdfAltoAPI.git alto_extract"
)

# pull or clone each repo
for repo in "${repos[@]}"; do
  url=$(echo "$repo" | cut -d' ' -f1)
  folder=$(echo "$repo" | cut -d' ' -f2)

  if [ -d "$folder" ]; then
    echo "pulling updates for $folder..."
    if ! git -C "$folder" pull; then
      echo "failed to pull updates for $folder."
    fi
  else
    echo "cloning $url into $folder..."
    if ! git clone "$url" "$folder"; then
      echo "failed to clone $url."
    fi
  fi
done

mkdir "shared"

echo "setup complete."

# prompt the user to launch the app
read -p "do you want to launch? (y/n): " choice
if [[ "$choice" =~ ^[Yy]$ ]]; then
  echo "launching the app..."
  ./launch.sh  # replace this with your actual script to run docker-compose up
else
  echo "app launch skipped."
fi