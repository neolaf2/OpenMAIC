from __future__ import annotations

import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


class OpenMAICClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None, form: bytes | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        req_headers = headers.copy() if headers else {}
        data = None
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        elif form is not None:
            data = form
        request = urllib.request.Request(url, data=data, method=method, headers=req_headers)
        try:
            with urllib.request.urlopen(request) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"success": False, "error": raw}
            payload.setdefault("success", False)
            payload.setdefault("status_code", e.code)
            return payload

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/api/health")

    def job_status(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/generate-classroom/{job_id}")

    def generate_classroom(self, requirement: str, *, language: str = "zh-CN", pdf_text: str | None = None, pdf_images: list[str] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"requirement": requirement, "language": language}
        if pdf_text is not None:
            body["pdfContent"] = {"text": pdf_text, "images": pdf_images or []}
        return self._request("POST", "/api/generate-classroom", json_body=body)

    def parse_pdf(self, pdf_path: str | Path, *, provider_id: str = "unpdf") -> dict[str, Any]:
        pdf_file = Path(pdf_path).expanduser().resolve()
        boundary = "----clianythingopenmaicboundary"
        mime = mimetypes.guess_type(str(pdf_file))[0] or "application/pdf"
        file_bytes = pdf_file.read_bytes()
        parts = []
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"providerId\"\r\n\r\n{provider_id}\r\n".encode())
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"pdf\"; filename=\"{pdf_file.name}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
            + file_bytes
            + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode())
        payload = b"".join(parts)
        return self._request(
            "POST",
            "/api/parse-pdf",
            form=payload,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(payload))},
        )
