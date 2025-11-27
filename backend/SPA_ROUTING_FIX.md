# SPA Routing Fix for Production

## Problem

The production endpoint `https://rapiddocs.io/generate` was returning `{"detail":"Not Found"}` because FastAPI didn't have a catch-all route to serve the Single Page Application (SPA) for client-side routes.

## Root Cause

The backend (`app/main.py`) only had explicit routes for:
- `/` (root)
- `/favicon.ico`
- `/logo.png`
- `/rd-logo.svg`

When users navigated to `/generate`, `/login`, `/register`, or any other client-side route, FastAPI didn't know what to do and returned a 404.

## Solution

Added a catch-all route in `app/main.py` (lines 116-129):

```python
# Catch-all route for SPA (Single Page Application) routing
# This must be last to allow other routes to match first
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    Serve the SPA for all non-API routes.
    This allows client-side routing to work correctly.
    """
    # Don't interfere with API routes
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}

    # Serve index.html for all other routes
    return FileResponse(os.path.join(static_dir, "index.html"))
```

## How It Works

1. **All non-API routes** (`/generate`, `/login`, `/pricing`, etc.) → Serve `index.html`
2. **API routes** (`/api/v1/*`) → Handled by FastAPI routers (or return 404 if not found)
3. **Root route** (`/`) → Explicitly serves `index.html`
4. **Static assets** (`/assets/*`) → Served by StaticFiles mount

## Client-Side Flow

1. User visits `https://rapiddocs.io/generate`
2. FastAPI catch-all route serves `index.html`
3. Browser loads the SPA JavaScript
4. Client-side router (`router.ts`) takes over and renders the Generate page
5. User interacts with the form
6. Frontend makes API call to `https://rapiddocs.io/api/v1/generate/document`
7. Backend processes the request correctly

## Testing

Run the test script to verify routing logic:

```bash
python test_routing.py
```

Expected output shows that:
- Frontend routes serve `index.html`
- API routes are handled separately

## Deployment

After deploying this fix:

1. Restart the FastAPI application
2. Test the following URLs:
   - `https://rapiddocs.io/` ✓ Should load homepage
   - `https://rapiddocs.io/generate` ✓ Should load generate page
   - `https://rapiddocs.io/login` ✓ Should load login page
   - `https://rapiddocs.io/api/v1/generate/document` ✓ Should require authentication

## Important Notes

- The catch-all route MUST be defined AFTER all other explicit routes
- This is a standard pattern for serving SPAs with backend APIs
- The frontend uses `/api/v1` as the base URL for all API calls (see `frontend/src/ts/api/client.ts`)

## Related Files

- `backend/app/main.py` - Main application with routing
- `frontend/src/ts/router.ts` - Client-side router
- `frontend/src/ts/api/client.ts` - API client configuration
- `frontend/src/ts/api/endpoints.ts` - API endpoint definitions
