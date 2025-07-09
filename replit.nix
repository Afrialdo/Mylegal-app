{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.flask
    pkgs.sqlite
  ];
}


