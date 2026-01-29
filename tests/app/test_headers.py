from flask import url_for


def test_owasp_useful_headers_set(
    service_id,
    document_id,
    key,
    document_has_metadata_requires_confirmation,
    client,
    mocker,
    sample_service,
    fake_nonce,
):
    mocker.patch("secrets.token_urlsafe", return_value=fake_nonce)

    mocker.patch("app.service_api_client.get_service", return_value={"data": sample_service})

    response = client.get(
        url_for(
            "main.landing",
            service_id=service_id,
            document_id=document_id,
            key=key,
        )
    )

    assert response.headers["X-Robots-Tag"] == "noindex, nofollow"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Permitted-Cross-Domain-Policies"] == "none"
    assert response.headers["Content-Security-Policy"] == (
        "default-src 'self';"
        "script-src 'self' 'nonce-TESTs5Vr8v3jgRYLoQuVwA';"
        "connect-src 'self';"
        "object-src 'self';"
        "font-src 'self' data:;"
        "img-src 'self' data:;"
        "style-src 'self' 'nonce-TESTs5Vr8v3jgRYLoQuVwA';"
        "frame-ancestors 'self';"
        "frame-src 'self';"
    )

    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store, no-cache, private, must-revalidate"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Cross-Origin-Embedder-Policy"] == "require-corp;"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin;"
    assert response.headers["Cross-Origin-Resource-Policy"] == "same-origin;"
    assert (
        response.headers["Permissions-Policy"]
        == "geolocation=(), microphone=(), camera=(), autoplay=(), payment=(), sync-xhr=()"
    )
    assert response.headers["Server"] == "Cloudfront"
