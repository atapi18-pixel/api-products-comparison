from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse


class CustomError(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


def error_handler(app: FastAPI):
    @app.exception_handler(CustomError)
    async def custom_handler(request: Request, err: CustomError):
        return JSONResponse(status_code=err.status_code, content={"code":err.code, "message": str(err)})
    
    @app.exception_handler(Exception)
    async def default_handler(request: Request, err: Exception):
        return JSONResponse(status_code=500, content={"code":"ERR0001", "message":"Internal server error. Please contant system admin!"})