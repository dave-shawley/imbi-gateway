import pydantic


class GitHubConnection(pydantic.BaseModel):
    api_root: pydantic.HttpUrl
    app_id: str
    private_key: str


# GitHub Enterprise webhooks use a custom OAuth2 application to
# interact with the GitHub API.
# https://docs.github.com/en/enterprise-cloud@latest/webhooks/using-webhooks/creating-webhooks#creating-webhooks-for-a-github-app
# https://docs.github.com/en/enterprise-cloud@latest/apps/creating-github-apps/writing-code-for-a-github-app/building-a-github-app-that-responds-to-webhook-events


class PagerDutyConnection(pydantic.BaseModel):
    api_root: pydantic.HttpUrl
    client_id: str
    client_secret: str
    scopes: list[str]


# PagerDuty webhook uses **Scoped OAuth** to retrieve additional
# information as necessary.
# https://developer.pagerduty.com/docs/oauth-functionality#scoped-oauth
