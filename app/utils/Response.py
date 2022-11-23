from starlette.responses import JSONResponse


def success_response(data='', total=''):
    return JSONResponse(status_code=200, content={"data": data, "total": total})


def error_response():
    return JSONResponse(status_code=500, content='An error occured')

def error_catching(error):
    return JSONResponse(status_code=500, content=error)

def unauthorized_response():
    return JSONResponse(status_code=401, content='Unauthorized request')

