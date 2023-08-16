#!/bin/bash

while true; do
  echo "Enter file name:"
  read -e -i "" -p "> " file_name

  echo "Enter commit message:"
  read commit_message

  git add "$file_name"
  git commit -m "$commit_message"

  echo "Enter 'c' to continue or 'q' to quit:"
  read choice

  if [ "$choice" == "q" ]; then
    break
  fi
done

