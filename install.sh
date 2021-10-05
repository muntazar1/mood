if [ "$ACCESS_TOKEN" != "" ]; then
  if [ "$VIRTUAL_ENV" != "" ]; then
    export VIRTUAL_ENV="HackerModePro/"
  fi
  rm -rif HackerModePro ~/.HackerModePro ~/../usr/bin/HackerModePro &>/dev/null
  if which sudo >/dev/null; then
    sudo python3 -B HackerModePro delete &>/dev/null
    if ! which wget >/dev/null; then
      sudo apt install wget
    fi
  else
    python3 -B HackerModePro delete &>/dev/null
    if ! which wget >/dev/null; then
      pkg install wget
    fi
  fi

  rm -f future.zip
  wget --header "Authorization: token $ACCESS_TOKEN" https://github.com/Arab-developers/HackerModePro/archive/refs/heads/future.zip
  unzip future.zip &>/dev/null
  rm -f future.zip
  mv -f HackerModePro-future HackerModePro
  if which sudo >/dev/null; then
    sudo chmod +x HackerModePro/bin/*
    sudo chmod -x HackerModePro/bin/activate
  else
    chmod +x HackerModePro/bin/*
    chmod -x HackerModePro/bin/activate
  fi
  if which sudo >/dev/null; then
    sudo python3 -B HackerModePro add_shortcut
    python3 -B HackerModePro install
  else
    if ! [ -d "/sdcard/HackerModePro/" ]; then
      mkdir "/sdcard/HackerModePro/"
    fi
    python3 -B HackerModePro add_shortcut
    python3 -B HackerModePro install
  fi

  function HackerModePro() {
    if [ $1 ]; then
      if [ $1 == "check" ]; then
        $HOME/.HackerModePro/HackerModePro/bin/HackerModePro check
      elif [ $1 == "update" ]; then
        $HOME/.HackerModePro/HackerModePro/bin/HackerModePro update
      elif [ $1 == "delete" ]; then
        $HOME/.HackerModePro/HackerModePro/bin/HackerModePro delete
      else
        $HOME/.HackerModePro/HackerModePro/bin/HackerModePro --help
      fi
    else
      if [ $VIRTUAL_ENV ]; then
        echo "HackerModePro is running..."
      else
        source $HOME/.HackerModePro/HackerModePro/bin/activate
      fi
    fi
  }

  if which termux-reload-settings >/dev/null; then
    mkdir $HOME/.termux &>/dev/null
    if [ -f $HOME/.termux/font.ttf ]; then
      mv -f $HOME/.termux/font.ttf $HOME/.termux/.old_font.ttf
    fi
    cp -f $HOME/.HackerModePro/HackerModePro/share/fonts/DejaVu.ttf $HOME/.termux/font.ttf
    termux-reload-settings
  fi

  rm -f HackerModeInstall

else
  echo "ACCESS_TOKEN not found!"
fi