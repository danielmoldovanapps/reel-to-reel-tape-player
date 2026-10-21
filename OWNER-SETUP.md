# Owner setup on GitHub

Suggested repository name: reel-to-reel-tape-player
Visibility: public. Owner: Daniel's own GitHub account, not a contributor's.
Initial branch: main.

This folder is prepared source; it has not been published or connected to an
external repository. Repository ownership, branch protection and release access
cannot be enforced by files alone.

After creation:

1. Keep administrator and write access with the owner. Contributors can fork
   the public repository and propose pull requests without collaborator access.
2. Enable two-factor authentication for the owner account.
3. Under Settings > Branches, create a main-branch protection rule requiring
   pull requests and conversation resolution. Keep force pushes and branch
   deletion disabled. Initially the owner can review and merge incoming PRs;
   requiring an additional approving reviewer can block a sole owner's own work.
4. Once the actual owner GitHub username is known, add a CODEOWNERS rule naming
   that account and enable code-owner review if appropriate. Do not insert an
   invented handle or assume a copyright notice configures repository ownership.
5. Keep GitHub Actions permissions read-only by default. Do not give untrusted
   pull requests credentials or automatic release/deployment permissions.
6. Before adding any package maintainer, agree who submits updates and who can
   publish them. Keep upstream GitHub ownership and Snap Store access separate.

These are setup instructions, not confirmation that the settings are active.
Any public recruitment request must be written/sent by the owner as appropriate;
no external forum, email or issue message has been sent from this preparation.
