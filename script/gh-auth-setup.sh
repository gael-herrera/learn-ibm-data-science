#!/bin/bash

dir="key"

key_filename="github"
config_filename="github-ssh.config"

config_content="Host github.com\n\tHostName github.com\n\tPort 22\n\tUser git\n\tIdentityFile $dir/$key_filename"

printf "[INPUT]: Type your GitHub-linked email address: "
read -r email

printf "[INPUT]: Type passphrase for the key (leave empty for no passphrase): "
read -sr passphrase
echo

git_config_ssh_cmd=$(git config core.sshCommand)

if [[ -f "$dir/$key_filename" || -f "$dir/$key_filename.pub" ]]; then
    echo
    echo "[WARN]: SSH key files already exist at '$dir/$key_filename' or '$dir/$key_filename.pub'."
    printf "[INPUT]: Type 'y' to continue anyway; type any other key to exit: "
    read should_continue

    if [[ "$should_continue" != "y" ]]; then
        echo "[INFO]: Github SSH auth setup canceled."
        exit 0
    fi

    rm "$dir/$key_filename" "$dir/$key_filename.pub"
fi

if grep -q "Host github.com" "$dir/$config_filename" >/dev/null 2>&1; then
    echo "[WARN]: GitHub SSH configuration already exists in $dir/$config_filename."
    printf "[INPUT]: Type 'y' to continue anyway; type any other key to exit: "
    read should_continue

    if [[ "$should_continue" != "y" ]]; then
        echo "[INFO]: Github SSH auth setup canceled."
        exit 0
    fi

    rm "$dir/$config_filename"
fi

if [[ "$git_config_ssh_cmd" != "ssh" && -n "$git_config_ssh_cmd" ]]; then
    echo
    echo "[WARN]: Git 'git config core.sshCommand' is set to '$git_config_ssh_cmd' modifying this could cause issues."
    printf "[INPUT]: Type 'y' to continue anyway; type any other key to exit: "
    read should_continue

    if [[ "$should_continue" != "y" ]]; then
        echo "[INFO]: Github SSH auth setup canceled."
        exit 0
    fi
fi

mkdir -p "$dir"
ssh-keygen -t ed25519 -C "$email" -f "$dir/$key_filename" -N "$passphrase" >/dev/null 2>&1
echo -e "$config_content" >>"$dir/$config_filename"
git config core.sshCommand "ssh -F $dir/$config_filename"
git config user.email $email

current_remote_url=$(git remote get-url origin 2>/dev/null)

if [[ "$current_remote_url" == https://github.com/* ]]; then
    repo_path=${current_remote_url#https://github.com/}
    ssh_url="git@github.com:$repo_path"

    git remote set-url origin "$ssh_url"
    echo "[INFO]: Remote URL converted from HTTPS to SSH: $ssh_url"
else
    echo "[WARN]: Remote URL is already using SSH or no remote URL set."
fi

echo
echo "[INFO]: SSH key generated and Git configured to use it."
echo "[INFO]: Please add the following public SSH key on https://github.com/settings/keys: '$(cat $dir/$key_filename.pub)'"
