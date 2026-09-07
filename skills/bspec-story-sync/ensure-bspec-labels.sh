#!/usr/bin/env sh
set -eu

gh label create "bspec" --color "0e8a16" --description "Created by the spec-driven workflow" || true
gh label create "story" --color "1d76db" --description "Implementation-ready product story" || true
gh label create "status/ready" --color "0e8a16" --description "Ready for implementation" || true
gh label create "status/in-progress" --color "fbca04" --description "Implementation in progress" || true
gh label create "status/in-review" --color "5319e7" --description "Waiting for review or merge" || true
gh label create "status/needs-fixes" --color "d93f0b" --description "Implementation needs fixes from review" || true
gh label create "status/blocked" --color "b60205" --description "Blocked on an external dependency or decision" || true
gh label create "status/needs-tech-design" --color "c5def5" --description "Needs technical design before implementation" || true
