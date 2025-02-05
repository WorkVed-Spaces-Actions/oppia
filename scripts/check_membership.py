import os
import sys
import requests

def main():
    if len(sys.argv) != 3:
        print("Usage: python check_membership.py <org> <team_slug>")
        sys.exit(1)

    org = sys.argv[1]
    team_slug = sys.argv[2]
    user = os.environ.get("GITHUB_ACTOR")

    if not user:
        print("Error: GITHUB_ACTOR environment variable is not set.")
        sys.exit(1)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    query = """
    query($org: String!, $userLogin: String!) {
      organization(login: $org) {
        teams(userLogins: [$userLogin]) {
          edges {
            node {
              slug
            }
          }
        }
      }
    }
    """

    variables = {
        "org": org,
        "userLogin": user
    }

    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code} - {response.text}")
        sys.exit(1)

    data = response.json()

    if "errors" in data:
        print("GraphQL errors:")
        for error in data["errors"]:
            print(error["message"])
        sys.exit(1)

    teams = data.get("data", {}).get("organization", {}).get("teams", {}).get("edges", [])

    for team in teams:
        if team["node"]["slug"] == team_slug:
            print(f"User '{user}' is a member of the team '{team_slug}' in the organization '{org}'.")
            sys.exit(0)

    print(f"User '{user}' is NOT a member of the team '{team_slug}' in the organization '{org}'.")
    sys.exit(1)

if __name__ == "__main__":
    main()
