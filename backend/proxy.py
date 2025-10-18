from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

# Replace this with your actual Streamlit app URL
STREAMLIT_URL = "https://aquatech-ai-assistant.onrender.com/"

@app.get("/")
async def proxy(request: Request):
    async with httpx.AsyncClient() as client:
        # Forward the request to your Streamlit app
        streamlit_response = await client.get(STREAMLIT_URL)

    # Create a response without the iframe-blocking headers
    headers = {
        k: v for k, v in streamlit_response.headers.items()
        if k.lower() not in ["x-frame-options", "content-security-policy"]
    }

    return Response(
        content=streamlit_response.content,
        status_code=streamlit_response.status_code,
        headers=headers,
        media_type=streamlit_response.headers.get("content-type")
    )