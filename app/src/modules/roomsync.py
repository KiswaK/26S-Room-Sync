import requests
import streamlit as st

API_BASE_URL = "http://web-api:4000"


def api_request(method, path, **kwargs):
    try:
        response = requests.request(method, f"{API_BASE_URL}{path}", timeout=15, **kwargs)
    except requests.exceptions.RequestException as exc:
        return False, None, {"error": str(exc)}

    try:
        payload = response.json()
    except ValueError:
        payload = {"message": response.text}

    return response.ok, response.status_code, payload


def show_api_error(payload, fallback_message="Something went wrong while calling the API."):
    if isinstance(payload, dict):
        st.error(payload.get("error") or payload.get("message") or fallback_message)
    else:
        st.error(fallback_message)


def parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes"}


def option_label(item):
    subtitle = item.get("subtitle")
    if subtitle:
        return f"{item['displayName']} ({subtitle})"
    return item["displayName"]
