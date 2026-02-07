import requests
import json
import os
import base64
from datetime import datetime
from urllib.parse import urlparse
from .repo_profile import RepoProfile
from .feature_classifier import FeatureClassifier


class ComparisonEngine:
    def __init__(self, retriever, llm):
        self.profiler = RepoProfile(retriever, llm)
        self.feature_classifier = FeatureClassifier(llm)
        self.llm = llm

    def _get_repo_owner_and_name(self, repo_url: str) -> tuple:
        """Extract owner and repo name from GitHub URL."""
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").replace(".git", "").split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return None, None

    def _fetch_repo_metadata(self, repo_url: str) -> dict:
        """Fetch repository metadata from GitHub API."""
        owner, repo = self._get_repo_owner_and_name(repo_url)
        if not owner or not repo:
            return {
                "name": repo_url,
                "description": "",
                "stars": 0,
                "forks": 0,
                "language": "",
                "license": "",
                "dependencies": 0,
                "last_updated": ""
            }

        token = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
        headers = {
            "Accept": "application/vnd.github+json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Get license name
            license_name = ""
            if data.get("license"):
                license_name = data["license"].get("spdx_id") or data["license"].get("name") or ""

            # Get dependencies count
            dependencies_count = self._get_dependencies_count(owner, repo, headers)

            # Format last updated date
            last_updated = data.get("updated_at", "")
            if last_updated:
                # Format as "X days ago" or just the date
                try:
                    updated_date = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                    now = datetime.now(updated_date.tzinfo)
                    days_ago = (now - updated_date).days
                    if days_ago == 0:
                        last_updated = "Today"
                    elif days_ago == 1:
                        last_updated = "1 day ago"
                    else:
                        last_updated = f"{days_ago} days ago"
                except:
                    pass

            return {
                "name": data.get("full_name", repo_url),
                "description": data.get("description", "") or "",
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "language": data.get("language", "") or "",
                "license": license_name,
                "dependencies": dependencies_count,
                "last_updated": last_updated
            }
        except Exception as e:
            print(f"Error fetching metadata for {repo_url}: {e}")
            return {
                "name": repo_url,
                "description": "",
                "stars": 0,
                "forks": 0,
                "language": "",
                "license": "",
                "dependencies": 0,
                "last_updated": ""
            }

    def _get_dependencies_count(self, owner: str, repo: str, headers: dict) -> int:
        """Get dependencies count from package.json or requirements.txt."""
        dependencies = set()
        
        # Try to fetch package.json
        try:
            package_url = f"https://api.github.com/repos/{owner}/{repo}/contents/package.json"
            response = requests.get(package_url, headers=headers, timeout=10)
            if response.status_code == 200:
                content_data = response.json()
                if content_data.get("encoding") == "base64":
                    content = base64.b64decode(content_data["content"]).decode("utf-8")
                    try:
                        data = json.loads(content)
                        for key in ("dependencies", "devDependencies", "peerDependencies"):
                            section = data.get(key, {})
                            if isinstance(section, dict):
                                dependencies.update(section.keys())
                    except:
                        pass
        except:
            pass

        # Try to fetch requirements.txt if no package.json dependencies found
        if not dependencies:
            try:
                req_url = f"https://api.github.com/repos/{owner}/{repo}/contents/requirements.txt"
                response = requests.get(req_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    content_data = response.json()
                    if content_data.get("encoding") == "base64":
                        content = base64.b64decode(content_data["content"]).decode("utf-8")
                        for line in content.splitlines():
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            for sep in ("==", ">=", "<=", "~=", ">", "<", "["):
                                if sep in line:
                                    line = line.split(sep, 1)[0].strip()
                                    break
                            if line:
                                dependencies.add(line)
            except:
                pass

        return len(dependencies)

    def compare(self, repo_a: str, repo_b: str) -> dict:
        profile_a = self.profiler.build(repo_a)
        profile_b = self.profiler.build(repo_b)

        features_a = self.feature_classifier.classify(profile_a)
        features_b = self.feature_classifier.classify(profile_b)

        metadata_a = self._fetch_repo_metadata(repo_a)
        metadata_b = self._fetch_repo_metadata(repo_b)

        comparison_prompt = f"""
You are an expert software architect.

Compare the following two GitHub repositories.

Return the result STRICTLY in valid JSON with this structure:

{{
  "overview": [string],
  "architecture": [string],
  "strengths": {{
    "repo_a": [string],
    "repo_b": [string]
  }},
  "tradeoffs": [string],
  "ideal_use_cases": {{
    "repo_a": [string],
    "repo_b": [string]
  }},
  "verdict": [string]
}}

Rules:
- Each array item must be 1 clear bullet point
- Be detailed but concise
- Do NOT include markdown
- Do NOT include extra text outside JSON

Repository A:
{profile_a}

Repository B:
{profile_b}
"""

        raw_response = self.llm.generate(comparison_prompt)

        try:
            structured_comparison = json.loads(raw_response)
        except Exception:
            structured_comparison = {
                "overview": [raw_response],
                "architecture": [],
                "strengths": {"repo_a": [], "repo_b": []},
                "tradeoffs": [],
                "ideal_use_cases": {"repo_a": [], "repo_b": []},
                "verdict": []
            }

        # Generate a paragraph summary for backward compatibility
        paragraph_prompt = f"""
Summarize the comparison between these two repositories in ONE concise paragraph.
Focus on approach, architecture, trade-offs, and ideal use cases.

Repository A:
{profile_a}

Repository B:
{profile_b}
"""
        paragraph = self.llm.generate(paragraph_prompt)

        # Add paragraph to structured_comparison
        structured_comparison["paragraph"] = paragraph

        return {
            "repo_a": metadata_a,
            "repo_b": metadata_b,
            "overall_comparison": structured_comparison,
            "feature_comparison": {
                feature: {
                    "repo_a": features_a.get(feature, "partial"),
                    "repo_b": features_b.get(feature, "partial"),
                }
                for feature in features_a
            }
        }
