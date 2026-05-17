{ pkgs, ... }:

{
  packages = [
    pkgs.git
    pkgs.go-task
    pkgs.lefthook
    pkgs.docker-compose
  ];

  enterShell = ''
    if [ ! -f .env ] && [ -f .env.example ]; then
      cp .env.example .env
      echo "Created .env from .env.example"
    fi

    lefthook install
  '';

  scripts.dev.exec = "task dev";
  scripts.test.exec = "task test";
  scripts.lint.exec = "task lint";
  scripts.logs.exec = "task compose:logs";
  scripts.down.exec = "task compose:down";
}
