from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.routers import auth, user, admin, instructor, student

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(instructor.router)
app.include_router(student.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema["openapi"] = "3.0.3"

    def convert_binary(schema):
        if isinstance(schema, dict):
            if schema.get("contentMediaType") == "application/octet-stream":
                schema.pop("contentMediaType", None)
                schema["format"] = "binary"

            for value in schema.values():
                convert_binary(value)

        elif isinstance(schema, list):
            for item in schema:
                convert_binary(item)

    convert_binary(schema)

    app.openapi_schema = schema
    return schema
    
app.openapi = custom_openapi